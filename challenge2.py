#!/usr/bin/python -tt

import pyrax
import argparse
import os




def main():
    
    creds_file = raw_input("Location of credentials file [~./rackspace_cloud_credentials]? ")
    if (creds_file == ""):
        creds_file = "~/.rackspace_cloud_credentials"
    
    pyrax.set_credential_file(os.path.expanduser(creds_file))
    
    cs = pyrax.cloudservers
    
    servers = cs.servers.list()
    
    srv_dict = {}
    
    for pos, srv in enumerate(servers):
        print "%s: %s" % (pos, srv.name)
        srv_dict[str(pos)] = srv.id
        
    choice = None
    
    while choice not in srv_dict:
        if choice is not None:
            print "  ** Not a valid server choice ** "
        choice = raw_input("Choose a server to clone: ")

if __name__ == '__main__':
    main()