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

def print_container(container):

	print "cdn_enabled", container.cdn_enabled
	print "cdn_ttl", container.cdn_ttl
	print "cdn_log_retention", container.cdn_log_retention
	print "cdn_uri", container.cdn_uri
	print "cdn_ssl_uri", container.cdn_ssl_uri
	print "cdn_streaming_uri", container.cdn_streaming_uri
	# print "cdn_ios_uri", container.cdn_ios_uri

def main():

	default_creds_file = os.path.join(os.path.expanduser("~"), 
		".rackspace_cloud_credentials")

	parser = argparse.ArgumentParser(
		description = "Creates a CDN-enabled container in Cloud Files.")
	parser.add_argument('-c', '--container', default = "", 
		help="Name of container to use/create; random name is used if unspecified.")
	parser.add_argument('-r', '--region', required = True, 
		choices=['DFW', 'ORD', 'LON'], help="Name of region.")
	parser.add_argument('-t', '--ttl', type = int, default = 1200, 
		help = "TTL for container; defaults to 1200.")
	parser.add_argument('-f', '--creds_file', default = default_creds_file, 
		help = "Location of credentials file; defaults to {}.".format(default_creds_file))
	args = parser.parse_args()

	if args.container == "":
		args.container = pyrax.utils.random_name(8, ascii_only = True)

	pyrax.set_setting("identity_type", "rackspace")
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
		except:
			print "Container error."
			sys.exit(1)

	try:
		container.make_public(ttl=args.ttl)
	except Exception, e:
		print "Error making container public: {}".format(e)
		
	print "Enabling CDN..."
	print_container(container)

if __name__ == '__main__':
	main()