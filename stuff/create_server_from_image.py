def create_server_from_image(cs, server_name, image_name, image_id, flavor):

    print "Creating server \"{}\" from \"{}\"...".format(server_name, image_name)
    try:
        new_server = cs.servers.create(server_name, image_id, flavor.id)
    except Exception, e:
        print "Error in server creation: {}".format(e)
        sys.exit(1)

    adminPass = new_server.adminPass

    complete = False
    while(not complete):
        time.sleep(20)
        servers = cs.servers.list()
        for server in servers:
            if (server.id == new_server.id):
                print "{} - {}% complete".format(server.name, server.progress)
                if server.status == 'ACTIVE':
                    new_server = server
                    complete = True
                if server.status == 'ERROR':
                    print "Error in server creation."
                    sys.exit(1)

    print "\nServer created.\n"
    print "Name:", new_server.name
    print "ID:", new_server.id
    print "Status:", new_server.status
    print "Admin Password:", adminPass
    print "Networks", new_server.networks

    return new_server.id