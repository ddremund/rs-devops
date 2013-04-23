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

def create_dns_record(dns, domain_name, name, data, ttl, rec_type = "A"):

    try:
        domain = dns.find(name = domain_name)
    except pyrax.exceptions.NotFound:
        answer = raw_input("The domain '{}' was not found.  Do you want to "
            "create it? [Y/N]".format(domain_name))
        if not answer.lower().startswith("y"):
            sys.exit(1)
        email = raw_input("Email address for domain? ")
        try:
            domain = dns.create(name = domain_name, emailAddress = email,
                ttl = 300, comment = "created via API script")
        except pyrax.exceptions.DomainCreationFailed, e:
            print "Domain creation failed:", e
            sys.exit(1)
        print "Domain Created:", domain

    a_rec = {"type": rec_type,
            "name": name,
            "data": data,
            "ttl": ttl}
    try:
        recs = domain.add_records([a_rec])
    except Exception, e:
        print "DNS record creation failed:", e
        sys.exit(1)

    print "Record created."
    print recs
    print

    return recs

def main():

    default_creds_file = os.path.join(os.path.expanduser("~"), 
        ".rackspace_cloud_credentials")

    parser = argparse.ArgumentParser(description = "Creates a static web page "
        "served out of Cloud Files.", 
        epilog = "Ex: {} -r DFW -d bob.com -n www -s 'Hello There!' - "
        "creates a site for www.bob.com with content 'Hello There!'".format(__file__))
    parser.add_argument('-r', '--region', required = True, 
        choices=['DFW', 'ORD', 'LON'], help="Name of region to use.")
    parser.add_argument('-d', '--domain', required = True, 
        help = "Domain in which to create the CNAME record.")
    parser.add_argument('-n', '--hostname', required = True, 
        help = "Hostname to use when creating the CNAME record.")
    parser.add_argument('-t', '--ttl', type = int, default = 300, 
        help = "Time to Live for the CNAME record; default 300")
    parser.add_argument('-c', '--container', default = "", 
        help="Name of container to use/create; random name is used if unspecified.")
    parser.add_argument('-i', '--index_file', 
        help="Index file to upload; overrides --content_string.")
    parser.add_argument('-s', '--content_string', default = "", 
        help = "String to place in index file; defaults to 'Welcome!'")
    parser.add_argument('-p', '--page_name', default = "index.html", 
        help = "Name of index page to create if content_string is specified.")
    parser.add_argument('-f', '--creds_file', default = default_creds_file, 
        help = "Location of credentials file; defaults to {}".format(default_creds_file))
    args = parser.parse_args()

    if args.container == "":
        args.container = pyrax.utils.random_name(8, ascii_only = True)

    creds_file = os.path.abspath(os.path.expanduser(args.creds_file)) 
    pyrax.set_credential_file(creds_file)

    cf = pyrax.connect_to_cloudfiles(args.region)
    dns = pyrax.cloud_dns

    print "Using container \"{}\"".format(args.container)

    container = None
    try:
        container = cf.get_container(args.container)
    except:
        try:
            container = cf.create_container(args.container)
        except Exception, e:
            print "Container exception:", e
            sys.exit(1)

    try:
        container.make_public(ttl = 1200)
    except Exception, e:
        print "Error making container public:", e

    if args.index_file is None:
        if args.content_string is None:
            print "Must specify either index_file or content_string.\n"
            sys.exit(1)
        try:
            obj = container.store_object(args.page_name, args.content_string, 
                content_type = "text/html")
            container.set_web_index_page(obj.name)
        except Exception, e:
            print "Error creating index file:", e
            sys.exit(1)
    else:
        file_name = os.path.abspath(os.path.expanduser(args.index_file))
        try:
            obj = container.upload_file(file_name, content_type = "text/html")
            container.set_web_index_page(obj.name)
        except Exception, e:
            print "Error uploading index file:", e

    recs = create_dns_record(dns, args.domain, "{}.{}".format(args.hostname, args.domain), 
        container.cdn_uri[len('http://'):], args.ttl, rec_type = "CNAME")

    # try:
    #     domain = dns.find(name = args.domain)
    # except pyrax.exceptions.NotFound:
    #     answer = raw_input("The domain '{}' was not found.  Do you want to "
    #         "create it? [Y/N]".format(args.domain))
    #     if not answer.lower().startswith("y"):
    #         sys.exit(1)
    #     email = raw_input("Email address for domain? ")
    #     try:
    #         domain = dns.create(name = args.domain, emailAddress = email,
    #             ttl = 300, comment = "created via API script")
    #     except pyrax.exceptions.DomainCreationFailed, e:
    #         print "Domain creation failed:", e
    #         sys.exit(1)
    #     print "Domain Created:", domain

    # cname_rec = {"type": "CNAME",
    #             "name": "{}.{}".format(args.hostname, args.domain),
    #             "data": container.cdn_uri[len('http://'):],
    #             "ttl": args.ttl}

    # try:
    #     recs = domain.add_records([cname_rec])
    # except Exception, e:
    #     print "Error adding CNAME record:", e
    #     sys.exit(1)


if __name__ == '__main__':
    main()