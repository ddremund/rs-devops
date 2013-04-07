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
    
    print cs.servers.list()

if __name__ == '__main__':
    main()