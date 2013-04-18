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

def choose_db_instance_flavor(cdb, prompt, initial_choice):

    flavors = cdb.list_flavors()
    ram_options = {}
    for flavor in flavors:
        if initial_choice == flavor.ram:
            return flavor
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

    default_creds_file = os.path.join(os.path.expanduser("~"), 
        ".rackspace_cloud_credentials")

    parser = argparse.ArgumentParser()
    parser.add_argument('region', metavar = "REGION", choices = ['DFW', 'ORD', 
        'LON'], help = "Region to connect to")
    parser.add_argument('ram', metavar ='RAM', 
        help = "RAM amount for instance in MB")
    parser.add_argument('instance_name', metavar = 'INST_NAME', 
        help = "Name of MySQL instance to create")
    parser.add_argument('db_name', metavar = 'DB_NAME', 
        help = "Name of database to create")
    parser.add_argument('user_name', metavar = 'USER_NAME', 
        help = "User to create")
    parser.add_argument('-f', '--creds_file', default = default_creds_file, 
        help = "Location of credentials file; defaults to {}".format(default_creds_file))

    args = parser.parse_args()

    creds_file = os.path.abspath(os.path.expanduser(args.creds_file)) 
    pyrax.set_credential_file(creds_file)

    cdb = pyrax.connect_to_cloud_databases(region = region)
    flavor = choose_db_instance_flavor(cdb, "Ram Amount: ", args.ram)
           

if __name__ == '__main__':
    main()