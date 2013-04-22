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

def main():

    default_creds_file = os.path.join(os.path.expanduser("~"), 
        ".rackspace_cloud_credentials")

    parser = argparse.ArgumentParser(description = "Creates a static web page "
        "served out of Cloud Files.", 
        epilog = "{} -r DFW -d bob.com -n www -s 'Hello There!' - "
        "creates a site for www.bob.com with content 'Hello There!'".format(__file__))
    parser.add_argument('-r', '--region', required = True, 
        choices=['DFW', 'ORD', 'LON'], help="Name of region to use.")
    parser.add_argument('-d', '--domain', required = True, 
        help = "Domain in which to create the CNAME record.")
    parser.add_argument('-n', '--hostname', required = True, 
        help = "Hostname to use when creating the CNAME record.")
    parser.add_argument('-c', '--container', default = "", 
        help="Name of container to use/create; random name is used if unspecified.")
    parser.add_argument('-i', '--index_file', 
        help="Index file to upload; overrides --content_string.")
    parser.add_argument('-s', '--content_string', default = "", 
        help = "String to place in index file; defaults to 'Welcome!'")
    parser.add_argument('-f', '--creds_file', default = default_creds_file, 
        help = "Location of credentials file; defaults to {}".format(default_creds_file))
    args = parser.parse_args()

    if args.container == "":
        args.container = pyrax.utils.random_name(8, ascii_only = True)

    creds_file = os.path.abspath(os.path.expanduser(args.creds_file)) 
    pyrax.set_credential_file(creds_file)

    cf = pyrax.connect_to_cloudfiles(args.region)

    print "Using container \"{}\"".format(args.container)

    container = None
    try:
        container = cf.get_container(args.container)
    except:
        try:
            container = cf.create_container(args.container)
        except Exception, e:
            print "Container exception: {}".format(e)
            sys.exit(1)

    try:
        container.make_public(ttl = 1200)
    except Exception, e:
        print "Error making container public: {}".format(e)

    if args.index_file is None:
        if args.content_string is None:
            print "Must specify either index_file or content_string.\n"
            sys.exit(1)
        try:
            obj = cf.store_object(container, 'index.html', args.content_string, 
                content_type = "text/html")
            cf.set_container_web_index_page(container, 'index.html')
        except Exception, e:
            print "Error creating index file: {}".format(e)
            sys.exit(1)
    else:
        file_name = os.path.abspath(os.path.expanduser(args.index_file))
        try:
            obj = cf.upload_file(cont, file_name, content_type = "text/html")
            cf.set_container_web_index_page(container, obj.name)
        except Exception, e:
            print "Error uploading index file: {}".format(e)


if __name__ == '__main__':
    main()