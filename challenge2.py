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
import argparse
import os
import time
import sys

def choose_server(cs, prompt):

    servers = cs.servers.list()
    
    srv_dict = {}
    
    for pos, srv in enumerate(servers):
        print "{}: {}".format(pos, srv.name)
        srv_dict[str(pos)] = srv
        
    choice = None
    
    while choice not in srv_dict:
        if choice is not None:
            print "  ** Not a valid server choice ** "
        choice = raw_input(prompt)

    return srv_dict[choice]

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

def create_image(cs, base_server, image_name):

    print "\nCreating image \"{}\" from \"{}\"...".format(image_name, base_server.name)
    try:
        image_id = cs.servers.create_image(base_server.id, image_name)
    except Exception, e:
        print "Error in image creation: {}".format(e)
        sys.exit(1) 

    complete = False
    while(not complete):
        time.sleep(10)
        imgs = cs.images.list()
        for img in imgs:
            if img.id == image_id:
                print "{} - {}% complete".format(img.name, img.progress)
                if img.progress > 99:
                    complete = True

    print "Image created.\n"

    return image_id

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
        #print "{} of {} servers completed".format(len(completed), len(new_servers))
        for server in servers: 
            new_servers_copy = list(new_servers)
            for new_server, admin_pass in new_servers_copy:
                if (server.id == new_server.id):
                    print "{} - {}% complete".format(server.name, server.progress)
                    if server.status == 'ACTIVE':
                        completed.append((server, admin_pass))
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
    
    def_creds_file = os.path.join(os.path.expanduser("~"), ".rackspace_cloud_credentials")
    creds_file = raw_input("Location of credentials file [{}]? ".format(def_creds_file))
    if creds_file == "":
        creds_file = def_creds_file
    else:
        creds_file = os.path.abspath(os.path.expanduser(creds_file))

    region = None
    print "Region?"
    while region not in ["DFW", "ORD"]:
        region = raw_input("(DFW | ORD): ")
    
    pyrax.set_credential_file(creds_file)
    cs = pyrax.connect_to_cloudservers(region = region)

    base_server = choose_server(cs, "Choose a server to clone: ")
    print

    def_image_name = "{}{}".format(base_server.name, "-image")
    image_name = raw_input("Enter a name for the image [{}]: ".format(def_image_name))
    if (image_name == ""):
        image_name = def_image_name
    print

    def_clone_name = "{}{}".format(base_server.name, "-clone")
    clone_name = raw_input("Enter a name for the clone [{}]: ".format(def_clone_name))
    if (clone_name == ""):
        clone_name = def_clone_name

    clone_flavor = choose_flavor(cs, "Enter a flavor ID for the clone: ", 
        base_server.flavor['id'])

    image_id = create_image(cs, base_server, image_name)

    server_dict = {'name': clone_name, 'image_name': image_name,
                    'image_id': image_id, 'flavor': clone_flavor}
    create_servers(cs, [server_dict])

if __name__ == '__main__':
    main()