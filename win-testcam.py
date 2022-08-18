#This runs on a PC and transfers the captured images to the raspberry pi
import paramiko
from scp import SCPClient
import glob, os, datetime

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
ssh.connect(hostname='10.0.0.1', username='root', password='toor',port=22)

# SCPCLient takes a paramiko transport as an argument
scp = SCPClient(ssh.get_transport())

filename = (datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + ".jpg"
for file in glob.glob("testcam-img/*.jpg"):
    scp.put(file, ("/tmp/"+filename))

scp.close()  
ssh.close()