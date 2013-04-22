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
import sys

def main():

    default_creds_file = os.path.join(os.path.expanduser("~"), 
    	".rackspace_cloud_credentials")
    
    parser = argparse.ArgumentParser(description = "Create a new A record in"
        " Cloud DNS.", 
        epilog = "Ex: {} blog.bob.com 1.2.3.4 bob.com -t 600"
        " - Create an A record pointing blog.bob.com to 1.2.3.4 with TTL 600".format(__file__))
    parser.add_argument('fqdn', metavar ='FQDN', help = "FQDN for A record")
    parser.add_argument('ip', metavar = 'IP', help = "Target IP address")
    parser.add_argument('domain', metavar = 'DOMAIN', 
    	help = "Domain in which to create the record")
    parser.add_argument('-t', '--ttl', type = int, default = 300, 
    	help = "Time to Live for A record; default 300")
    parser.add_argument('-f', '--creds_file', default = default_creds_file, 
        help = "Location of credentials file; defaults to {}".format(default_creds_file))

    args = parser.parse_args()

    creds_file = os.path.abspath(os.path.expanduser(args.creds_file)) 
    pyrax.set_credential_file(creds_file)

    dns = pyrax.cloud_dns

    try:
    	domain = dns.find(name = args.domain)
    except pyrax.exceptions.NotFound:
    	answer = raw_input("The domain '{}' was not found.  Do you want to "
    		"create it? [Y/N]".format(args.domain))
    	if not answer.lower().startswith("y"):
    		sys.exit(1)
    	email = raw_input("Email address for domain? ")
    	try:
    		domain = dns.create(name = args.domain, emailAddress = email,
    			ttl = 300, comment = "created via API script")
    	except pyrax.exceptions.DomainCreationFailed, e:
    		print "Domain creation failed:", e
    		sys.exit(1)
    	print "Domain Created:", domain

    a_rec = {"type": "A",
    		"name": args.fqdn,
    		"data": args.ip,
    		"ttl": args.ttl}

    recs = domain.add_records([a_rec])
    print recs

if __name__ == '__main__':
    main()