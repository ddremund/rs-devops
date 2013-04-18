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

def choose_db_instance_flavor(cdb, prompt):

    flavors = cdb.list_flavors()
    ram_options = {}
    for flavor in flavors:
        ram_options[str(flavor.ram)] = flavor
    print "\nHow much RAM ?\nOptions:",
    for option in sorted(ram_options.iteritems(), key=lambda item: int(item[0])):
        print option[0],
    print
    ram = None
    while ram not in ram_options:
        if ram is not None:
            print " ** Not a valid RAM amount **"
        ram = raw_input(prompt)

    return ram_options[ram]

def main():

    def_creds_file = os.path.join(os.path.expanduser("~"), 
        ".rackspace_cloud_credentials")
    creds_file = raw_input("Location of credentials file [{}]? ".format(def_creds_file))
    if creds_file == "":
        creds_file = def_creds_file
    else:
        creds_file = os.path.abspath(os.path.expanduser(creds_file))
    pyrax.set_credential_file(creds_file)

    region = None
    print "Region?"
    while region not in ["DFW", "ORD"]:
        region = raw_input("(DFW | ORD | LON): ")

    cdb = pyrax.connect_to_cloud_databases(region = region)
    flavor = choose_db_instance_flavor(cdb, "Ram Amount: ")
    

           

if __name__ == '__main__':
    main()