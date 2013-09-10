import pyrax
import os
import sys
import time

def make_choice(item_list, prompt):

	for index, item in enumerate(item_list):
		print index, item

	selection = -1
	while selection < 0 or selection > len(item_list) - 1:
		selection = int(raw_input(prompt))

	return item_list[selection]

def main():

	pyrax.set_setting('identity_type', 'rackspace')
	def_creds_file = os.path.join(os.path.expanduser("~"), ".rackspace_cloud_credentials")
	creds_file = raw_input("Location of credentials file [{}]? ".format(def_creds_file))
	if creds_file == "":
		creds_file = def_creds_file
	else:
		creds_file = os.path.abspath(os.path.expanduser(creds_file))
	pyrax.set_credential_file(creds_file)

	region = ""
	print "Region?"
	while region not in pyrax.regions:
		region = raw_input("(" + " | ".join(list(pyrax.regions)) + "): ")
	cs = pyrax.connect_to_cloudservers(region)

	base_server = make_choice(cs.servers.list(), "Choose server: ")
	print

	def_image_name = "{}{}".format(base_server.name, "-image")
	image_name = raw_input("Enter a name for the image [{}]: ".format(def_image_name))
	if (image_name == ""):
		image_name = def_image_name
	print

	def_clone_name = "{}{}".format(base_server.name, "-clone")
	clone_name = raw_input("Enter a name for the clone [{}]: ".format(def_clone_name))
	if (clone_name == ""):
		clone_name = def_clone_name

	flavors = cs.flavors.list()
	valid_flavors = [flavor for flavor in flavors if flavor.disk >= cs.flavors.get(base_server.flavor['id']).disk]
	clone_flavor = make_choice(valid_flavors, "Choose a flavor: ")

	print "Creating image '{}' from server '{}'...".format(base_server.name, image_name)
	try:
		image_id = base_server.create_image(image_name)
	except Exception, e:
		print "Error in image creation:", e
		sys.exit(1)

	image = cs.images.get(image_id)

	image = pyrax.utils.wait_until(image, 'progress', 100, verbose = True, interval = 15)
	print "Image Created.\n"

	print "Creating server '{}' from image '{}'...".format(clone_name, image_name)
	try:
		server = cs.servers.create(clone_name, image, clone_flavor)
	except Exception, e:
		print "Error in server creation:", e

	admin_pass = server.adminPass

	while server.status != 'ACTIVE':
		time.sleep(20)
		server = cs.servers.get(server.id)
		if server.status == 'ERROR':
			print "Error in server build.  Exiting.\n"
			sys.exit(1)
		print "{} {}% complete".format(clone_name, server.progress)

	print "Clone finished."
	print "Name:", server.name
	print "ID:", server.id
	print "Status:", server.status
	print "Admin Password:", admin_pass
	print "Networks", server.networks
	print 

if __name__ == '__main__':
	main()