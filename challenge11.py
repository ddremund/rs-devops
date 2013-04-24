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
import time
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

def create_servers_with_networks(cs, server_list, networks, update_freq = 20): 

    new_servers = []
    print

    for server in server_list:
        print "Creating server \"{}\" from \"{}\"...\n".format(server['name'], 
            server['image_name'])
        try:
            server_object = cs.servers.create(server['name'], server['image_id'], 
                server['flavor'].id, nics = networks)
        except Exception, e:
            print "Error in server creation: {}".format(e)
        else:
            new_servers.append((server_object, server_object.adminPass))

    completed = []
    
    total_servers = len(new_servers)

    while len(completed) < total_servers:
        time.sleep(update_freq)
        servers = cs.servers.list()
        print "{} of {} servers completed".format(len(completed), total_servers)
        for server in servers: 
            new_servers_copy = list(new_servers)
            for new_server, admin_pass in new_servers_copy:
                if (server.id == new_server.id):
                    print "{} - {}% complete".format(server.name, server.progress)
                    if server.status == 'ACTIVE':
                        completed.append((server, admin_pass))
                        new_servers.remove((new_server, admin_pass))
                    if server.status == 'ERROR':
                        print "{} - Error in server creation.".format(server.name)
                        new_servers.remove((new_server, admin_pass))
                        total_servers -= 1

    print "\n{} Server(s) created.\n".format(len(completed))
    for server, admin_pass in completed: 
        print "Name:", server.name
        print "ID:", server.id
        print "Status:", server.status
        print "Admin Password:", admin_pass
        print "Networks", server.networks
        print

    return completed

def create_load_balancer(clb, name, port, protocol, nodes, virtual_ips):

    print "Building Load Balancer '{}'...".format(name)
    try:
        lb = clb.create(name, port = port, protocol = protocol, 
            nodes = nodes, virtual_ips = virtual_ips)
    except Exception, e:
        print "Error in load balancer creation: {}".format(e)
        sys.exit(1)
    lb = wait_until(lb, 'status', ['ACTIVE', 'ERROR'], interval = 10, attempts = 30, 
        verbose = True, verbose_atts = 'status')

    return lb

def print_load_balancer(lb):

    print "Name:", lb.name
    print "ID:", lb.id
    print "Status:", lb.status
    print "Nodes:", lb.nodes
    print "Virtual IPs:", lb.virtual_ips
    print "Algorithm:", lb.algorithm
    print "Protocol:", lb.protocol
    print "Port:", lb.port
    print

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

    parser = argparse.ArgumentParser(description = "Creates multiple Cloud "
        "Servers and places them behind a new Cloud Load Balancer.", 
        epilog = "Ex: {} -r DFW -b web -n 3 -k ~/ssh.key -i 'Ubuntu 11.10'"
        " -f 512 -l lb1 -d site1.site.com -t 600 -e 'Error!'"
        " -s tuesday - create web1, web2, and web3 and place them behind a new "
        "CLB called lb1.".format(__file__))

    parser.add_argument("-r", "--region", required = True, 
        choices = ['DFW', 'ORD', 'LON'], 
        help = "Cloud Servers region to connect to.")
    parser.add_argument("-b", "--base", required = True, 
        help = "Base name for servers.")
    parser.add_argument("-n", "--number", type = int, default = 2, 
        help = "Number of servers to build; default is 2.")
    parser.add_argument("-k", "--keyfile", required = True, 
        help = "SSH Key to be installed at /root/.ssh/authorized_keys.")
    parser.add_argument("-i", "--image_name", 
        help = "Image name to use to build server.  Menu provided if absent.")
    parser.add_argument("-f", "--flavor_ram", type = int, 
        help = "RAM of flavor to use in MB.  Menu provided if absent.")
    parser.add_argument("-s", "--volume_size", type = int, default = 100, 
        help = "Size of block storage volume to add to servers in GB; "
        "defaults to 100.")
    parser.add_argument("-u", "--volume_type", default = "SATA", 
        choices = ["SATA", "SSD"], 
        help = "Type of cloud block storage volume to add to servers; "
        "defaults to SATA.")
    parser.add_argument("-x", "--volume_name", 
        help = "Volume name for CBS servers.  Will be appended to server "
        "names; randomly generated if not supplied.")
    parser.add_argument("-l", "--lb_name", required = True, 
        help = "Name of load balancer to create")
    parser.add_argument("-d", "--dns_fqdn", required = True, 
        help = "FQDN for DNS A record pointing to LB VIP.")
    parser.add_argument("-t", "--ttl", type = int, default = 300, 
        help = "TTL for DNS A record; defaults to 300.")
    parser.add_argument("-p", "--port", type = int, default = 80, 
        help = "Port to load balance; defaults to 80.")
    parser.add_argument("-q", "--protocol", default = "HTTP", 
        help = "Protocol to load balance; defaults to HTTP")
    parser.add_argument("-v", "--vip_type", default = "PUBLIC",
        choices = ["PUBLIC", "PRIVATE"], help = "VIP type; defaults to PUBLIC.")
    parser.add_argument('-c', '--creds_file', default = default_creds_file, 
        help = "Location of credentials file; defaults to {}".format(default_creds_file))

    args = parser.parse_args()

    creds_file = os.path.abspath(os.path.expanduser(args.creds_file)) 
    pyrax.set_credential_file(creds_file)

    cs = pyrax.connect_to_cloudservers(region = args.region)
    clb = pyrax.connect_to_cloud_loadbalancers(region = args.region)
    cbs = pyrax.connect_to_cloud_blockstorage(region = args.region)
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

    servers = []
    for i in range(1, args.number + 1):
        servers.append({'name': "{}{}".format(args.base, i),
                        'image_name': image.name,
                        'image_id': image.id,
                        'flavor': flavor})


if __name__ == '__main__':
    main()