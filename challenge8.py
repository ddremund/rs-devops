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

def main():

    default_creds_file = os.path.join(os.path.expanduser("~"), 
        ".rackspace_cloud_credentials")

    parser = argparse.ArgumentParser()
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


if __name__ == '__main__':
    main()