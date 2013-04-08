#!/usr/bin/python -tt

import pyrax
import argparse
import os
import time

def chooseServer(cs, prompt):

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

def chooseFlavor(cs, prompt, minimum_ram):

    flavors = cs.flavors.list()

    flavors_dict = {}

    print "Valid flavors: \n"

    for flavor in flavors
        if flavor.ram < minimum_ram
            continue
        flavors_dict[str(flavor.id)] = flavor
        print "ID:", flavor.id
        print "Name:", flavor.name
        print "RAM:", flavor.ram
        print "Disk:", flavor.disk
        print "vCPUs:", flavor.vcpus
        print

    choice = None

    while choice not in flavors_dict and flavors_dict[choice].ram < minimum_ram
        if choice is not None:
            print " ** Not a valid flavor ID ** "
        choice = raw_input(prompt)

    return flavors_dict[choice]



def main():
    
    def_creds_file = os.path.join(os.path.expanduser("~"), ".rackspace_cloud_credentials")
    creds_file = raw_input("Location of credentials file [{}]? ".format(def_creds_file))
    if (creds_file == ""):
        creds_file = def_creds_file
    else:
        creds_file = os.path.expanduser(creds_file)
    
    pyrax.set_credential_file(creds_file)
    cs = pyrax.cloudservers

    base_server = chooseServer(cs, "Choose a server to clone: ")
    print

    def_image_name = "{}{}".format(base_server.name, "-image")
    image_name = raw_input("Enter a name for the image [{}]: ".format(def_image_name))
    if (image_name == ""):
        image_name = def_image_name
    print

    def_clone_name = "{}{}".format(base_server.name, "-clone")
    clone_name = raw_input("Enter a name for the clone [{}]:".format(def_clone_name))
    if (clone_name == ""):
        clone_name = def_clone_name

    clone_flavor = chooseFlavor(cs, "Enter a flavor ID for the clone: ", base_server.flavor.ram)

    print "Creating image \"{}\" from \"{}\"...".format(image_name, base_server.name)
    try:
        img_id = cs.servers.create_image(base_server.id, image_name)
    except Exception, e:
        print "Error in image creation: {}".format(e)
        sys.exit(1) 

    complete = False
    while(not complete):
        time.sleep(5)
        imgs = cs.images.list()
        for img in imgs:
            if (img.id == img_id):
                print "{} - {}%% complete".format(img.name, img.progress)
        if (img.progress > 99):
            complete = True

    print "Image created.\n"

    print "Creating server \"{}\" from \"{}\"...".format(clone_name, image_name)
    try:
        clone = cs.servers.create(clone_name, img_id, clone_flavor.id)
    except Exception, e:
        print "Error in clone creation: {}".format(e)
        sys.exit(1)

    complete = False
    while(not complete)
        time.sleep(5)
        servers = cs.servers.list()
        for server in servers:
            if (server.id == clone.id):
                print "{} - {}%% complete".format(server.name, server.progress)
        if (server.progress > 99):
            clone = server
            complete = True

    print "Clone server created.\n"
    print "Name:", clone.name
    print "ID:", clone.id
    print "Status:", clone.status
    print "Admin Password:", clone.adminPass
    print "Networks", clone.networks

if __name__ == '__main__':
    main()