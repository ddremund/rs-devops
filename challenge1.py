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

def create_servers(cs, server_list): 

    new_servers = []
    print

    for server in server_list:
        print "Creating server \"{}\" from \"{}\"...".format(server['name'], 
            server['image_name'])
        try:
            server_object = cs.servers.create(server['name'], server['image_id']
                , server['flavor'].id)
        except Exception, e:
            print "Error in server creation: {}".format(e)
        else:
            new_servers.append((server_object, server_object.adminPass))

    completed = []
    
    while len(completed) < len(new_servers):
        time.sleep(20)
        servers = cs.servers.list()
        print "{} of {} servers completed".format(len(completed), len(new_servers))
        for server in servers: 
            new_servers_copy = list(new_servers)
            for new_server, admin_pass in new_servers_copy:
                if (server.id == new_server.id):
                    print "{} - {}% complete".format(server.name, server.progress)
                    if server.status == 'ACTIVE':
                        completed.append((server, admin_pass))
                        new_servers.remove((new_server, admin_pass))
                    if server.status == 'ERROR':
                        print "Error in server creation."
                        new_servers.remove((new_server, admin_pass))

    print "\n{} Server(s) created.\n".format(len(completed))
    for server, admin_pass in completed: 
        print "Name:", server.name
        print "ID:", server.id
        print "Status:", server.status
        print "Admin Password:", admin_pass
        print "Networks", server.networks
        print

    return completed

def main():

    default_creds_file = os.path.join(os.path.expanduser("~"), 
    	".rackspace_cloud_credentials")

    parser = argparse.ArgumentParser()

    parser.add_argument("-r", "--region", required = True, choices = ['DFW', 'ORD', 'LON'], 
    	help = "Cloud Servers region to connect to.")
    parser.add_argument("-b", "--base", required = True, help = "Base name for servers.")
    parser.add_argument("-n", "--number", type = int, default = 3, help = "Number of servers to build; default is 3.")
    parser.add_argument('-f', '--creds_file', default = default_creds_file, 
        help = "Location of credentials file; defaults to {}".format(default_creds_file))

    args = parser.parse_args()

    creds_file = os.path.abspath(os.path.expanduser(args.creds_file)) 
    pyrax.set_credential_file(creds_file)

    cs = pyrax.connect_to_cloudservers(region = args.region)

    flavor = choose_flavor(cs, "Flavor ID for servers: ")
    image = choose_image(cs, "Image choice: ")

    servers = []
    for i in range(1, args.number + 1):
        #create_server_from_image(cs, "{}{}".format(args.base, i), image.name, image.id, flavor)
        servers.append({'name': "{}{}".format(args.base, i),
                        'image_name': image.name,
                        'image_id': image.id,
                        'flavor': flavor})
    create_servers(cs, servers)

if __name__ == '__main__':
    main()