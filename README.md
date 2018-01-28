# DeployREMnux

DeployREMnux is a Python script that will deploy a cloud instance of the public REMnux distribution in the Amazon cloud (AWS).


## Installation

Make sure you have Python 2.7 installed and use it here.
To use the script, you will need to Install the python cloud library https://libcloud.apache.org/ and two other libraries.

```
pip install apache-libcloud
pip install paramiko
pip install pycrypto
```

Special Considerations for usage on Windows:

1. You must install the "Microsoft Visual C++ 9.0" before installing pycrypto, which you can get [here](https://www.microsoft.com/en-us/download/details.aspx?id=44266).
2. The pip tool may not be in your PATH, so you may need to call it directly like "c:\Python27\Scripts\pip install paramiko"
3. Unfortunately, there is a bug in  libcloud on Windows resulting in the default remnux user password not being changed during deployment. If you ran DeployREMnux from windows, you need to connect to the instance via SSH or RDP with the default password of "malware" and manually run the change_passwd.sh script. For security reasons, this should be done immediately after deployment.


Also, you'll need active Amazon EC2 access keys.  You can create keys using the following steps:

```
Log into your EC2 Console: https://console.aws.amazon.com
Select your name -> Security Credentials.
Expand "Access Keys"
Create New Access Key.
Record the Access Key ID and the Access Key
```

You also need to set up your configuration file, see **DeployREMnux-config.txt.example** for an example. Make a copy of this file and rename it by removing **.example** from the end of the file name. Then update each of the configuration values as needed. At a minimum, you must specify your Amazon access keys that you generated above, as well as the location of your public and private SSH keys. If specifying a windows path to a key file use double backslashes like "c:\\\\path\\\\to\\\\key\\\\id_pub".

Generate your private key without a passphrase.
Note, if on Windows, generating the SSH keys via PuTTYgen is problematic. Use ssh-keygen (for example, ssh-keygen -t rsa -b 4096) to generate your keys. You can do this from Linux or through the Git Bash command line on windows.


## Usage

Use this command to spin up your REMnux instance in the cloud:

```
python DeployREMnux.py
```
The output of this command will tell you how to connect to your instance via SSH and RDP as well as give you an option for terminating the instance.

## Watch for Orphaned Resources that may cost you money unnecessarily

Always keep an eye on Amazon console (https://console.aws.amazon.com/ec2) as you run these scripts to watch for orphaned instances, volums, etc, killing them manually if necessary to avoid additional charges. You must change to the region where the resources were created (N. Virginia), in order to see them.
 
