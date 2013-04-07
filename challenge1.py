#!/usr/bin/python -tt

import argparse
import json
import requests
import time

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base', help="Base hostname to use for servers.")
    parser.add_argument('-c', '--count', type=int, default=3, help="Number of servers to create; default 3.")
    parser.add_argument('-i', '--image', default="3afe97b2-26dc-49c5-a2cc-a2fc8d80c001", help="ID of image from which to build servers.")
    parser.add_argument('-f', '--flavor', type=int, choices=range(2,9), default=2, help="Flavor of slice; default 2.")
    parser.add_argument('-r', '--region', choices=['DFW', 'ORD', 'LON'], default='DFW', help="Region (datacenter) in which to build servers; default DFW.")
    parser.add_argument('-u', '--user', help="Username for authentication.", required=True)
    parser.add_argument('-a', '--api-key', help="API Key for authentication.", required=True)
    
    args = parser.parse_args()
    
    auth_url = 'https://identity.api.rackspacecloud.com/v2.0/tokens'
    auth_data = {
        "auth": {
            "RAX-KSKEY:apiKeyCredentials": {
                "apiKey": args.api_key,
                "username": args.user
            }
        }
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    r = requests.post(auth_url, data=json.dumps(auth_data), headers=headers)
    #print json.dumps(r.json(), indent=4)
    auth_response = r.json()
    service_catalog = auth_response['access']['serviceCatalog']
    token = auth_response['access']['token']['id']
    tenant = auth_response['access']['token']['tenant']
    
    headers['X-Auth-Token'] = token
    
    
    service_cat_key = 'cloudServersOpenStack'
    
    endpoint = None
    
    for service in service_catalog:
        if service['name'] == service_cat_key:
            for ep in service['endpoints']:
                if ep['region'] == args.region:
                    endpoint = ep['publicURL']
                    break
            break
    if not endpoint:
        raise SystemExit('Endpoint not found')
    else:
        print endpoint
        
    servers = {}
        
    for i in range(0, args.count):
        name = "{}{}".format(args.base, i)
        
        server_data = {
            "server" : {
                "flavorRef": args.flavor,
                "imageRef": args.image,
                "name": name
            }
        }
        server_url = "{}/servers".format(endpoint)
        r = requests.post(server_url, data=json.dumps(server_data), headers=headers)    
        servers[name] = r.json()['server']  
        # print r.json()
        
    completed = []
    
    time.sleep(20)
    
    while len(completed) < args.count:
        for name, server in servers.iteritems():
            if name in completed:
                print '%s: 100%%' % name,
                continue
            r = requests.get("{}/servers/{}".format(endpoint, server['id']), headers = headers)
            detail = r.json()['server']
            servers[name] = dict(server, **detail)
            if detail['status'] == 'ERROR':
                progress = detail['status']
                servers[name]['progress'] = progress
            else:
                progress = detail['progress']
            print '%s: %s%%' % (name, progress),
            if detail['status'] in ['ACTIVE', 'ERROR']:
                completed.append(name)
                if detail['status'] == 'ERROR':
                    requests.delete(server_url, headers=headers)
        print
        time.sleep(30)
        
    for name, server in servers.iteritems():
        print 'Name: %s' % name
        print 'ID: %s' % server['id']
        print 'Status: %s' % server['status']
        print 'IP: %s' % server['accessIPv4']
        print 'Admin Password: %s' % server['adminPass']
        
if __name__ == '__main__':
    main()