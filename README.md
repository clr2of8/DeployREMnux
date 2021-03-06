# !!! The AWS instance that contained REMnux no longer exists so this script no longer works as is

# DeployREMnux

DeployREMnux is a Python script that will deploy a cloud instance of the public REMnux distribution in the Amazon cloud (AWS). The REMnux distribution itself is maintained by [Lenny Zeltser](https://zeltser.com/) with extensive help from [David Westcott](https://twitter.com/beast_fighter) and is available from https://remnux.org. 


## Installation

Make sure you have Python 2.7 installed and use it here.
To use the script, you will need to Install the python cloud library https://libcloud.apache.org/ and two other libraries.

```
pip install apache-libcloud paramiko pycrypto
```

Special Considerations for usage on Windows:

1. You must install "Microsoft Visual C++ for Python 2.7" before installing pycrypto, which you can get [here](https://www.microsoft.com/en-us/download/details.aspx?id=44266).
2. The pip tool may not be in your PATH, so you may need to call it directly like "c:\Python27\Scripts\pip install paramiko"
3. Use forward slashes when specifying file paths in the config file.


Also, you'll need Amazon EC2 access keys.  You can create keys using the following steps:

```
Log into your EC2 Console: https://console.aws.amazon.com
Select your name -> Security Credentials.
Expand "Access Keys"
Create New Access Key.
Record the Access Key ID and the Access Key
```

You also need to set up your configuration file, see **DeployREMnux-config.txt.example** for an example. Make a copy of this file and rename it by removing **.example** from the end of the file name. Then update each of the configuration values as needed. At a minimum, you must specify your Amazon access keys that you generated above, as well as the location of your public and private SSH keys. If specifying a windows path to a key file use forward slashes like "c:/path/to/key/id_pub".

Generate your private key without a passphrase.
Note, if on Windows, generating the SSH keys via PuTTYgen is problematic. Use ssh-keygen (for example, **ssh-keygen -t rsa -b 4096**) to generate your keys. You can do this from Linux or through the Git Bash command line or the Linux subsystem on windows.


## Usage

Use this command to spin up your REMnux instance in the cloud:

```
python DeployREMnux.py
```
The output of this command will tell you how to connect to your instance via SSH and RDP as well as give you an option for terminating the instance.

If you would like to instruct REMnux to update itself as part of the deployment, use the update option when running the script as follows:

```
python DeployREMnux.py -u
```
This is the equivalent of running "update-remnux full" manually from the command line. Note that deploying with the update option will add a significant amount of time to the deployment (~35 minutes), but is recommended.

## Watch for Orphaned Resources that may cost you money unnecessarily

Always keep an eye on the Amazon console (https://console.aws.amazon.com/ec2) as you run these scripts to watch for orphaned instances, volumes, etc, killing them manually if necessary to avoid additional charges. You must change to the region where the resources were created (N. Virginia), in order to see them.
 
