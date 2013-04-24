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
import type
from pyrax.utils import wait_until

def main():

    default_creds_file = os.path.join(os.path.expanduser("~"), 
        ".rackspace_cloud_credentials")

    parser = argparse.ArgumentParser(description = "Creates multiple Cloud "
        "Servers and places them behind a new Cloud Load Balancer.", 
        epilog = "Ex: {} -r DFW -b web -n 3 -k ~/ssh.key -i 'Ubuntu 11.10'"
        " -f 512 -l lb1 -d site1.site.com -t 600 -e 'Error!'"
        " -s tuesday - create web1, web2, and web3 and place them behind a new "
        "CLB called lb1.".format(__file__))

    parser.add_argument("-r", "--region", required = True, 
        choices = ['DFW', 'ORD', 'LON'], 
        help = "Cloud Servers region to connect to.")
    parser.add_argument("-b", "--base", required = True, 
        help = "Base name for servers.")
    parser.add_argument("-n", "--number", type = int, default = 2, 
        help = "Number of servers to build; default is 2.")
    parser.add_argument("-k", "--keyfile", required = True, 
        help = "SSH Key to be installed at /root/.ssh/authorized_keys.")
    parser.add_argument("-i", "--image_name", 
        help = "Image name to use to build server.  Menu provided if absent.")
    parser.add_argument("-f", "--flavor_ram", type = int, 
        help = "RAM of flavor to use in MB.  Menu provided if absent.")
    parser.add_argument("-s", "--volume_size", type = int, default = 100, 
        help = "Size of block storage volume to add to servers in GB; "
        "defaults to 100.")
    parser.add_argument("-l", "--lb_name", required = True, 
        help = "Name of load balancer to create")
    parser.add_argument("-d", "--dns_fqdn", required = True, 
        help = "FQDN for DNS A record pointing to LB VIP.")
    parser.add_argument("-t", "--ttl", type = int, default = 300, 
        help = "TTL for DNS A record; defaults to 300.")
    parser.add_argument("-p", "--port", type = int, default = 80, 
        help = "Port to load balance; defaults to 80.")
    parser.add_argument("-q", "--protocol", default = "HTTP", 
        help = "Protocol to load balance; defaults to HTTP")
    parser.add_argument("-v", "--vip_type", default = "PUBLIC",
        choices = ["PUBLIC", "PRIVATE"], help = "VIP type; defaults to PUBLIC.")
    parser.add_argument('-c', '--creds_file', default = default_creds_file, 
        help = "Location of credentials file; defaults to {}".format(default_creds_file))

    args = parser.parse_args()


if __name__ == '__main__':
    main()