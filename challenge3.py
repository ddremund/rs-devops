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

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--container', default = "", help="Name of container to use/create; random name is used if unspecified.")
    parser.add_argument('-r', '--region', choices=['DFW', 'ORD', 'LON'], default='DFW', help="Name of region; defaults to DFW.")
    parser.add_argument('-d', '--dir', default = os.path.dirname(os.path.realpath(__file__)), help="Directory to upload; defaults to the current directory.")
    parser.add_argument('-f', '--creds_file', default = os.path.join(os.path.expanduser("~"), ".rackspace_cloud_credentials"), help = "Location of credentials file; defaults to ~/.rackspace_cloud_credentials")

    args = parser.parse_args()

    if args.container == "":
    	args.container = pyrax.utils.random_name(8, ascii_only = True)

    creds_file = os.path.expanduser(args.creds_file)
    pyrax.set_credential_file(creds_file)

    cf = pyrax.connect_to_cloudfiles(args.region)

    print "Using container \"{}\"".format(args.container)

if __name__ == '__main__':
    main()