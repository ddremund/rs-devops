#!/usr/bin/python -tt

# Copyright 2013 Derek Remund (derek.remund@rackspace.com)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pyrax
import os
import sys
import argparse
from pyrax.utils import wait_until

def choose_image(cs, prompt):

    images = cs.images.list()

    images_dict = {}

    print "\nAvailable Images"

    for num, image in enumerate(images):
        images_dict[str(num)] = image
        print "Selection {}".format(num)
        print "Name: {}\nID: {}".format(image.name, image.id)
        print

    choice = None

    while choice not in images_dict:
        if choice is not None:
            print " ** Not a valid image choice ** "
        choice = raw_input(prompt)

    return images_dict[choice]

def choose_flavor(cs, prompt, default_id=2):

    flavors = cs.flavors.list()

    flavors_dict = {}
    minimum_ram = 0

    print "\nValid flavors: \n"

    for flavor in flavors:
        if flavor.id == default_id:
            minimum_ram = flavor.ram

    for flavor in flavors:
        if flavor.ram < minimum_ram:
            continue
        flavors_dict[str(flavor.id)] = flavor
        print "ID:", flavor.id
        print "Name:", flavor.name
        print "RAM:", flavor.ram
        print "Disk:", flavor.disk
        print "vCPUs:", flavor.vcpus
        print

    choice = None

    while choice not in flavors_dict:
        if choice is not None:
            print " ** Not a valid flavor ID ** "
        choice = raw_input(prompt)

    return flavors_dict[choice]

def create_dns_record(dns, domain_name, name, data, ttl, rec_type = "A"):

    try:
        domain = dns.find(name = domain_name)
    except pyrax.exceptions.NotFound:
        answer = raw_input("The domain '{}' was not found.  Do you want to "
            "create it? [Y/N]".format(domain_name))
        if not answer.lower().startswith("y"):
            sys.exit(1)
        email = raw_input("Email address for domain? ")
        try:
            domain = dns.create(name = domain_name, emailAddress = email,
                ttl = 300, comment = "created via API script")
        except pyrax.exceptions.DomainCreationFailed, e:
            print "Domain creation failed:", e
            sys.exit(1)
        print "Domain Created:", domain

    a_rec = {"type": rec_type,
            "name": name,
            "data": data,
            "ttl": ttl}
    try:
        recs = domain.add_records([a_rec])
    except Exception, e:
        print "DNS record creation failed:", e
        sys.exit(1)

    print "Record created."
    print recs
    print

    return recs

def main():

    default_creds_file = os.path.join(os.path.expanduser("~"), 
        ".rackspace_cloud_credentials")

    parser = argparse.ArgumentParser(description = "Creates a Cloud Server "
        "and associated A record.", 
        epilog = "Ex: {} -r DFW -n web1.bob.com -f 512 -i 'Ubuntu 12.10' - "
        "creates a 512MB Ubuntu 12.10 server called web1.bob.com and an "
        "A record pointing to its IP.".format(__file__))
    parser.add_argument('-r', '--region', required = True, 
        choices=['DFW', 'ORD', 'LON'], help="Name of region to use.")
    parser.add_argument('-n', '--name', required = True, 
        help = "Hostname to use for the server and A record.")
    parser.add_argument('-t', '--ttl', type = int, default = 300, 
        help = "Time to Live for the A record; default 300")
    parser.add_argument('-i', '--image_name', 
        help = "Image name to use to build server.  Menu provided if absent.")
    parser.add_argument('-f', '--flavor_ram', type = int, 
        help = "RAM of flavor to use in MB.  Menu provided if absent.")
    parser.add_argument('-c', '--creds_file', default = default_creds_file, 
        help = "Location of credentials file; defaults to {}".format(default_creds_file))
    args = parser.parse_args()

    pyrax.set_setting("identity_type", "rackspace")
    creds_file = os.path.abspath(os.path.expanduser(args.creds_file)) 
    pyrax.set_credential_file(creds_file)

    cs = pyrax.connect_to_cloudservers(region = args.region)
    dns = pyrax.cloud_dns

    if args.flavor_ram is None:
        flavor = choose_flavor(cs, "Choose a flavor ID: ")
    else:
        flavor = [flavor for flavor in cs.flavors.list() 
            if flavor.ram == args.flavor_ram]
        if flavor is None or len(flavor) < 1:
            flavor = choose_flavor(cs, "Specified flavor not found.  Choose a flavor ID: ")
        else:
            flavor = flavor[0]

    if args.image_name is None:
        image = choose_image(cs, "Choose an image: ")
    else:
        image = [img for img in cs.images.list() if args.image_name in img.name]
        if image == None or len(image) < 1:
            image = choose_image(cs, "Image matching '{}' not found.  Select image: ".format(args.image_name))
        else:
            image = image[0]

    print "Creating server '{}' with image {} and flavor {}...".format(args.name, image.name, flavor.name)
    server = cs.servers.create(args.name, image.id, flavor.id)
    admin_pass = server.adminPass
    server = wait_until(server, 'status', ['ACTIVE', 'ERROR'], interval = 15, 
        attempts = 80, verbose = True, verbose_atts = 'progress')

    if server == None:
        print "Error in server creation.\n"
        sys.exit(1)
    if server.status == 'ERROR':
        print 'Server in ERROR status.  Deleting...\n'
        server.delete()
        sys.exit(1)

    print "\nServer created."
    print "Name:", server.name
    print "ID:", server.id
    print "Status:", server.status
    print "Admin Password:", admin_pass
    print "Networks", server.networks
    print

    dns_tokens = args.name.split('.')
    count = len(dns_tokens)
    domain_name = "{}.{}".format(dns_tokens[count -2], dns_tokens[count - 1])

    recs = create_dns_record(dns, domain_name, args.name, server.accessIPv4, args.ttl, rec_type = "A")


if __name__ == '__main__':
    main()