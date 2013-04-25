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
import time

def delete_resources(resources):

    for resource in resources:
        try:
            resource.delete()
        except Exception, e:
            print "Error deleting {}:", e

def main():

    default_creds_file = os.path.join(os.path.expanduser("~"), 
        ".rackspace_cloud_credentials")

    parser = argparse.ArgumentParser(description = "Deletes all objects in "
        "various cloud resource categories.")
    parser.add_argument("-r", "--region", required = True, 
        choices = ['DFW', 'ORD', 'LON'], 
        help = "Cloud Servers region to delete from")
    parser.add_argument('-s', '--servers', action = 'store_true', 
        help = "Delete all Cloud Servers"))
    parser.add_argument('-i', '--images', action = 'store_true', 
        help = "Delete all custom Cloud Server images")
    parser.add_argument('-l', '--load_balancers', action = 'store_true', 
        help = "Delete all Cloud Load Balancers")
    parser.add_argument('-f', '--files', action = 'store_true', 
        help = "Delete all Cloud Files containers and objects")
    parser.add_argument('-d', '--databases', action = 'store_true', 
        help = "Delete all Cloud Database databases and instances")
    parser.add_argument('-n', '--networks', action = 'store_true', 
        help = "Delete all custom Cloud Networks")
    parser.add_argument('-b', '--block_storage', action = 'store_true', 
        help = "Delete all Cloud Block Storage volumes")
    parser.add_argument('-c', '--creds_file', default = default_creds_file, 
        help = "Location of credentials file; defaults to {}".format(default_creds_file))

    args = parser.parse_args()

    creds_file = os.path.abspath(os.path.expanduser(args.creds_file)) 
    pyrax.set_credential_file(creds_file)

    if(args.servers):
        cs = pyrax.connect_to_cloudservers(region = args.region)
        delete_resources(cs.servers.list())

    if(args.images):
        custom_images = []
        cs = pyrax.connect_to_cloudservers(region = args.region)
        images = cs.images.list()
        for image in images:
            if not image.metadata['image_type'] == 'base':
                custom_list.append(image)
        delete_resources(custom_images)

    if(args.load_balancers):
        clb = pyrax.connect_to_cloud_loadbalancers(region = args.region)
        delete_resources(clb.list())

if __name__ == '__main__':
    main()