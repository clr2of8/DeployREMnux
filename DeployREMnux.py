#!/usr/bin/python

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import ScriptDeployment
from libcloud.compute.base import NodeAuthSSHKey
from libcloud.compute.ssh import ParamikoSSHClient
import datetime, json, argparse, time, string, random
from distutils.util import strtobool


parser = argparse.ArgumentParser(description='some')
parser.add_argument('-p','--password',help='The password for the remnux user that will be used to RDP into the instace', required=False)
parser.add_argument('-t','--terminate',help='Terminate the specified node id and associated resources. e.g. -t i-0cf26edddf5c39b6a', required=False)
parser.add_argument('-u','--update',help='Issue the "update-remnux full" command on deploy to have the REMnux distro update itself', default=False, required=False, action='store_true')
args = parser.parse_args()


# read config file
with open('DeployREMnux-config.txt') as json_data_file:
    config = json.load(json_data_file)
ACCESS_ID = config["AmazonConfig"]["aws_access_key_id"]
SECRET_KEY = config["AmazonConfig"]["aws_secret_access_key"]
private_key_file = config["SshConfig"]["private_key_file"]
public_key_file = config["SshConfig"]["public_key_file"]

myregion = 'us-east-1'
IMAGE_ID = 'ami-79cff703'
SIZE_ID = config["AmazonConfig"]["aws_instance_size"]

cls = get_driver(Provider.EC2)
driver = cls(ACCESS_ID, SECRET_KEY, region=myregion)

def cleanup_and_exit(node):
    print ("Terminating node and associated resources.")
    nodeName = node.name
    driver.destroy_node(node)
    start_time = time.time()
    retry_timeout = 60*2 # retry time in seconds
    while(True):
        try:
            driver.ex_delete_security_group(nodeName)
        except Exception:
            if(time.time() - start_time > retry_timeout):
                print "Failed to delete associated Security Group"
                break
            time.sleep(3)
            continue
        break
    kp = driver.get_key_pair(nodeName)
    driver.delete_key_pair(kp)
    print("REMnux Instance Shutdown")
    exit()
    
if args.terminate:
    node = driver.list_nodes([args.terminate])[0]   
    cleanup_and_exit(node)

print("Spinning up REMnux Instance, this will take a minute or two. . .")

nodeName = datetime.datetime.utcnow().strftime("REMnux-%Y-%m-%dt%H-%M-%S-%f")

sizes = driver.list_sizes()
images = driver.list_images(location=myregion, ex_image_ids=[IMAGE_ID])

size = [s for s in sizes if s.id == SIZE_ID][0]
image = [i for i in images if i.id == IMAGE_ID][0]
 
#read in public key in order to deploy to new node
with file(public_key_file) as f:
    pub_key = f.read()
pk = NodeAuthSSHKey(pub_key)
 
# create this ssh key in the cloud
driver.import_key_pair_from_string(nodeName, pub_key)
   
# create the security group, only allowing ssh at first
sg = driver.ex_create_security_group(nodeName, "allows ssh and rdp from anywhere", vpc_id=None)
sg = driver.ex_authorize_security_group_ingress(sg["group_id"], 22, 22, cidr_ips=['0.0.0.0/0'], group_pairs=None, protocol='tcp')

# a deployment to change the remnux user password that will be used for RDP access
# Generate a random password if a blank password was provided in the configuration file, Random string generator from https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
newPass = config["RemnuxConfig"]["remnux_user_password"]
if args.password:
    newPass = args.password
if newPass == "":
    newPass = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(20))
passwd_change_cmd = ('echo -e "malware\n%s\n%s\n\" | passwd' % (newPass,newPass)).encode('utf-8')
sd = ScriptDeployment(passwd_change_cmd, args=None, name="change_passwd.sh",delete=True)

my_mapping = [{'VirtualName': None, 'Ebs': {'DeleteOnTermination': 'true'}, 'DeviceName': '/dev/sda1'}]


# create and provision node
node = driver.deploy_node(name=nodeName, ex_blockdevicemappings=my_mapping, image=image, size=size, ex_security_groups=[nodeName] ,auth=pk, ssh_username="remnux",ssh_key=private_key_file,deploy=sd)

# on Windows, libcloud doesn't run the deploy script to change the password, so we try it manually here
sshclient = ParamikoSSHClient(node.public_ips[0],username="remnux",key=private_key_file)
res1 = sshclient.connect()
res2 = sshclient.run(passwd_change_cmd)


# allow remote access (RDP) by modifying the security group
driver.ex_authorize_security_group(nodeName, 3389, 3389, cidr_ip='0.0.0.0/0', protocol='tcp')

#update REMnux
if args.update:
	print("The image is deployed, but now it is updating itself, this will take ... quite a while. (~35 minutes)")
	res3 = sshclient.run("update-remnux full")
	print("The update is complete. Rebooting now for settings to take full effect.")
	node.reboot()
	driver.wait_until_running([node], wait_period=10, timeout=1500, ssh_interface='public_ips', force_ipv4=True, ex_list_nodes_kwargs=None)
	print("Done! Whew, that was a lot of work!")

print("REMnux Instance Ready to use, IP address: %s  RDP password for the 'remnux' user is %s" % (node.public_ips[0], newPass))
print("For SSH access use this command: ssh -i %s remnux@%s" % (private_key_file, node.public_ips[0]))
	
# prompt before instance shutdown
print 'Would you like to shutdown the instance now? [Y/n]',
while True:
    try:
        response = raw_input().lower()
        if ((response is "") or (strtobool(response))):
            cleanup_and_exit(node)
            break
        else:
            print ("You can terminate this instance in the future by running this command:\n python DeployREMnux.py -t %s" % node.id)
            break
    except ValueError:
        print "Please respond with y or n",       




