
import pyrax
import os 

from pyrax.utils import wait_until
pyrax.set_credential_file(os.path.expanduser('~/.rackspace_cloud_credentials'))
cs = pyrax.cloudservers
ubu = [img for img in cs.images.list() if "Ubuntu 12.04" in img.name][0]
server = cs.servers.create('test', image=ubu, flavor=2)
server = wait_until(server, 'status', ['ACTIVE', 'ERROR'], interval = 15, attempts = 40, verbose = True, verbose_atts = 'progress')
if server.status == 'ACTIVE':
     print server.accessIPv4
else:
     server.delete()