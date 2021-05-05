# Team_15 SNS Assignment1 - End To End Messaging System Using Python
- **Suman Mitra - 2020202018**
- **Aditya Mahajan - 2020202019**
- **Dipankar Saha - 2020201084**
- **Shivam Puri - 2020201096**

# Functionality

- **SERVER**: python server.py 127.0.0.1 <ANY_FREE_PORT>
- **CLIENT**: python client.py <SAME_IP_AS_ABOVE> <SAME_PORT_AS_ABOVE>
  
# Commands:
- SIGNUP (username) (password)  
- LOGIN (username) (password) 
- LOGOUT  
 while the server is ON, the client can LOGOUT and LOGIN again to use the system
- CREATE (group_name)
- JOIN (group_name)
- LIST 
this will list out all the group information currently available along with client user name and total client count
- SEND (username/group_name) (message)  
username: Message will send to particular user with `username` along with the information who send it   
group_name: Message will send to all the user belong to that particualr group `group_name` along with the information who send it and from which group it has been send 
- SEND (username/group_name) FILE (relative FILEPATH) 

# Security:
 - `Two-key triple DES` has been used for End to End Encryption
 - `Diffie-Hellman` method has been used to exchange the key between sender and receiver

## NOTE: 
Relative filepath is the home directory (including filename) from where client.py is executed. So, for example, if *client.py* is executed from **TMP** and  if some image *pic.jpg* is present in its child directory **TMP/images**, then the command will be: **SEND (username/group_name) FILE images/pic.jpg**
