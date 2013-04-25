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

import os
import sys
import json
import requests
import argparse

def create_route(api_key, recipient, target, priority, description):

    create_url = 'https://api.mailgun.net/v2/routes'

    return requests.post(
        create_url, auth = ("api", api_key), 
        data = {"priority": priority,
                "description": description,
                "expression": "match_recipient(\"{}\")".format(recipient),
                "action": ["forward(\"{}\")".format(target), "stop()"]})

def main():

    default_key_file = os.path.join(os.path.expanduser("~"), ".mailgunapi")

    parser = argparse.ArgumentParser(description = "Configures a simple "
        "route in Mailgun", 
        epilog = "Ex: {} derek.remund@apichallenges.mailgun.org "
        "http://cldsrvr.com/challenge1 -p 1 -d 'API Challenge 12'".format(__file__))
    parser.add_argument('recipient', metavar = 'RECIPIENT', 
        help = "Recipient to match")
    parser.add_argument('target', metavar = 'TARGET', 
        help = "Target URL to forward to")
    parser.add_argument('-d', '--description', default = "", 
        help = "Description for route")
    parser.add_argument('-p', '--priority', type = int, default = 1, 
        help = "Priority for route; defaults to 1")
    parser.add_argument('-k', '--api_key', help = "Mailgun API key; overrides"
        " --key_file")
    parser.add_argument('-f', '--key_file', default = default_key_file, 
        help = "File with API key; defaults to {}".format(default_key_file))

    args = parser.parse_args()

    if args.api_key is None:
        try: 
            with open(os.path.abspath(os.path.expanduser(args.key_file))) as f:
                api_key = f.read()
        except Exception, e:
            print "Error reading API key file:", e
            sys.exit(1)
    else:
        api_key = args.api_key

    response =  create_route(api_key, args.recipient, args.target, 
        args.priority, args.description)
    print response.text

if __name__ == '__main__':
    main()