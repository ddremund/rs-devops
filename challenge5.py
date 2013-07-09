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

def choose_db_instance_flavor(cdb, prompt, initial_choice):

    flavors = cdb.list_flavors()
    ram_options = {}
    for flavor in flavors:
        ram_options[str(flavor.ram)] = flavor
    if initial_choice in ram_options:
        return ram_options[initial_choice]
    print "\nRAM Options:",
    for option in sorted(ram_options.iteritems(), key=lambda item: int(item[0])):
        print option[0],
    print
    ram = None
    while ram not in ram_options:
        if ram is not None:
            print " ** Not a valid RAM amount **"
        ram = raw_input(prompt)

    return ram_options[ram]

def create_clouddb_instance(cdb, name, flavor, disk):

    print "\nCreating MySQL instance \"{}\" from \"{}\"...".format(name, flavor.name)
    try:
        new_instance = cdb.create(name, flavor = flavor, volume = disk)
    except Exception, e:
        print "Error in instance creation: {}".format(e)
        sys.exit(1) 

    complete = False
    while(not complete):
        instances = cdb.list()
        for instance in instances:
            if instance.id == new_instance.id:
                print "{} - Building...".format(instance.name)
                if instance.status == 'ACTIVE':
                    complete = True
                    new_instance = instance
                if instance.status == 'ERROR':
                    print "Error in instance creation."
                    sys.exit(1)
        time.sleep(15)

    print "Instance created.\n{} - {}\n".format(new_instance.name, new_instance.id)

    return new_instance

def create_clouddb_database(cdb, instance, name):

    try:
        db = instance.create_database(name)
    except Exception, e:
        print "Error in DB creation: {}".format(e)
        sys.exit(1)

    dbs = instance.list_databases()
    print "Database {} created.".format(db.name)
    print "Current databases for instance: '{}':".format(instance.name)
    for db in dbs:
        print db.name

    return db

def create_db_user(cdb, instance, name, password, databases):

    try:
        user = instance.create_user(name, password, database_names = databases)
    except Exception, e:
        print "Error in user creation: {}".format(e)
        sys.exit(1)

    print "User {} created on instance {}.".format(user.name, instance.name)

    return user

def main():

    default_creds_file = os.path.join(os.path.expanduser("~"), 
        ".rackspace_cloud_credentials")

    parser = argparse.ArgumentParser(description = "Create a Cloud Database"
        " instance with a database and a user.", 
        epilog = "{} -r DFW -f 1024 -s 1 -i mysql1 -d db1 -u user1 -p passw0rd"
        "\nCreate a 1GB RAM, 1GB disk space instance with the given names.".format(__file__))
    parser.add_argument('-r', '--region', choices = ['DFW', 'ORD', 
        'LON'], help = "Region to connect to", required = True)
    parser.add_argument('-f', '--flavor_ram', type = int, 
        help = "RAM amount for instance in MB", required = True)
    parser.add_argument('-s', '--disk_space', type = int, 
        help = "Amount of disk space to allocate in GB", required = True)
    parser.add_argument('-i', '--instance_name', 
        help = "Name of MySQL instance to create", required = True)
    parser.add_argument('-d', '--db_name', 
        help = "Name of database to create", required = True)
    parser.add_argument('-u', '--user_name', 
        help = "User to create", required = True)
    parser.add_argument('-p', '--password', 
        help = "Password for user", required = True)
    parser.add_argument('-c', '--creds_file', default = default_creds_file, 
        help = "Location of credentials file; defaults to {}".format(default_creds_file))

    args = parser.parse_args()

    pyrax.set_setting("identity_type", "rackspace")
    creds_file = os.path.abspath(os.path.expanduser(args.creds_file)) 
    pyrax.set_credential_file(creds_file)

    cdb = pyrax.connect_to_cloud_databases(region = args.region)
    flavor = choose_db_instance_flavor(cdb, 
        "Chosen flavor RAM invalid, choose a valid amount: ", str(args.flavor_ram))
    
    instance = create_clouddb_instance(cdb, args.instance_name, 
        flavor, args.disk_space)

    db = create_clouddb_database(cdb, instance, args.db_name)
    user = create_db_user(cdb, instance, args.user_name, args.password, [db.name])
    print

if __name__ == '__main__':
    main()