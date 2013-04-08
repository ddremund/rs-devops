#!/usr/bin/python -tt

import pyrax
import argparse
import os

def chooseServer(cs, prompt):

    servers = cs.servers.list()
    
    srv_dict = {}
    
    for pos, srv in enumerate(servers):
        print "{}: {}".format(pos, srv.name)
        srv_dict[str(pos)] = (srv.id, srv.name)
        
    choice = None
    
    while choice not in srv_dict:
        if choice is not None:
            print "  ** Not a valid server choice ** "
        choice = raw_input("Choose a server to clone: ")

    return srv_dict[choice]


def main():
    

    creds_file = raw_input("Location of credentials file [~./rackspace_cloud_credentials]? ")
    if (creds_file == ""):
        creds_file = os.path.join(os.path.expanduser("~"), ".rackspace_cloud_credentials")
    else:
        creds_file = os.path.expanduser(creds_file)

    print creds_file
    
    pyrax.set_credential_file(creds_file)
    
    cs = pyrax.cloudservers

    base_server = chooseServer(cs, "Choose a server to clone: ")

    base_id = base_server[0]
    print

    def_image_name = "{}{}".format(base_server[1], "-image")
    image_name = raw_input("Enter a name for the image [{}]: ".format(def_image_name))
    if (image_name == ""):
        image_name = def_image_name

    print "Image Name: {}".format(image_name)

if __name__ == '__main__':
    main()