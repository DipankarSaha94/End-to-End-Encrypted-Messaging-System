import socket 
import select 
import sys 
import tqdm
import os
from os import path
from Crypto.Cipher import DES3
from Crypto import Random
from random import randint
from time import *

def pad(text):
    while len(text) % 8 != 0:
        text += ' '
    return text
def pad_file_chunk(file_chunk):
    while len(file_chunk) % 8 != 0:
        file_chunk.extend(b'9')
    return file_chunk

G = 9
P = 23
a = 0


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
if len(sys.argv) != 3: 
	print ("Correct usage: script, IP address, port number") 
	exit() 
IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 
server.connect((IP_address, Port)) 

message = server.recv(2048).decode()
print(message)

SEPARATOR = "<FALTU>"
BUFFER = 4096
BUFFER2 = 4096 + 2048

username = ''

while True: 
	sockets_list = [sys.stdin, server] 
	read_sockets, write_socket, error_socket = select.select(sockets_list,[],[]) 
	
	for socks in read_sockets:
		if socks == server:
			act = server.recv(2048)
			act_split = act.split(b'<SEPARATOR>')
			if str(act_split[0])[2:-1] == 'FILE':
				filename = str(act_split[1])[2:-1]
				itr = int(str(act_split[2])[2:-1])
				filename = os.path.basename(filename)
				tmp = 0
				#print('Receiving.', end = '')
				with open(filename, "wb") as f:
					for i in range(0, itr):
						by = server.recv(BUFFER2)
						by_split = by.split(b'<SEPARATOR>')
						
						y = int(str(by_split[4])[2:-1])
						key2 = int(pow(y, a, P))
						if key2 == 1:
							key2 += 5
						
						temp = []
						for i in range(16):
							b = (key2 >> (i * 8)) & 0xFF
							temp.append(b)
						
						temp2 = [chr(b) for b in temp]
						key2_main = bytearray(b'')
						for i in temp2:
							key2_main.extend(bytes(i, 'utf-8'))

						cipher_decrypt2 = DES3.new(bytes(key2_main), DES3.MODE_OFB, by_split[1])
						decrypted_chunk = cipher_decrypt2.decrypt(by_split[2]).strip(b'9')			
						f.write(decrypted_chunk)
						tmp += 1
						#print('.', end = '')
				if tmp > 0:
					if str(by_split[5])[2:7] == 'faltu':
						print('<' + str(by_split[3])[2:-1] + '>: File <' + filename + '> Received !!')
					else:
						print('<' + str(by_split[5])[2:-3] + '><' + str(by_split[3])[2:-1] + '>: File <' + filename + '> Received !!')
			else:
				if str(act_split[2])[2:-1] == 'GROUP':
					y = int(str(act_split[5])[2:-1])
				else:
					y = int(str(act_split[3])[2:-1])
								
				key2 = int(pow(y, a, P))
				if key2 == 1:
					key2 += 5
				
				temp = []
				for i in range(16):
					b = (key2 >> (i * 8)) & 0xFF
					temp.append(b)
				
				temp2 = [chr(b) for b in temp]
				key2_main = bytearray(b'')
				for i in temp2:
					key2_main.extend(bytes(i, 'utf-8'))
				
				cipher_decrypt = DES3.new(bytes(key2_main), DES3.MODE_OFB, act_split[0])
				decrypted_text = cipher_decrypt.decrypt(act_split[1])
				if str(act_split[2])[2:-1] == 'GROUP':
					print('<' + str(act_split[3])[2:-3] + '><' + str(act_split[4])[2:-1] + '>: ' + str(decrypted_text)[2:-1].strip())
				else:
					print('<' + str(act_split[2])[2:-1] + '>: ' + str(decrypted_text)[2:-1].strip())
				
		else:
			msg = sys.stdin.readline()
			msg2_split = msg.split(' ')
			msg2 = ''
			for i in range(0, len(msg2_split)):
				msg2 += msg2_split[i] + '<SEPARATOR>'
			msg = msg2[:-11]
			msg_split = msg2.split('<SEPARATOR>')
			msg_split.pop()
			
			if msg_split[0] == 'LOGIN':
				username = msg_split[1]
				
				server.send(bytes(msg, 'utf-8'))
				flag = server.recv(2048).decode()
				if flag == '0':
					print('LOGIN FAILED.. Please try again !!')
					continue
				else:
					print('LOGIN Successful !!')
					a = randint(0, 999999) + 2020202018
					x = int(pow(G, a, P))
					server.send(bytes('X<SEPARATOR>' + str(x) + '<SEPARATOR>faltu', 'utf-8'))
				
			elif msg_split[0] == 'LOGOUT\n':
				username = ''
				server.send(bytes(msg, 'utf-8'))
				flag_msg = server.recv(2048).decode()
				if flag_msg != 0:
					print(flag_msg)
				else:
					print('Some LOGOUT Error !! Please try again...')
				
			elif msg_split[0] == 'SIGNUP': 
				username = msg_split[1]
				server.send(bytes(msg, 'utf-8'))
				flag = server.recv(2048).decode()
				if flag == '1':
					print('SIGNUP Successful !! Please login to continue...')
				else:
					print('SIGNUP FAILED.. Please try again !!')
				continue
			
			elif msg_split[0] == 'CREATE':
				server.send(bytes(msg, 'utf-8'))
				flag = server.recv(2048).decode()
				if flag == '0':
					print('FAILURE in GROUP CREATION !!')
				else:
					print(flag)

			elif msg_split[0] == 'LIST\n':
				server.send(bytes(msg, 'utf-8'))
				flag = server.recv(2048).decode()
				if flag == '0':
					print('GROUP_LIST Error !!')
				else:
					print(flag)      

			elif msg_split[0] == 'JOIN':
				server.send(bytes(msg, 'utf-8'))
				flag = server.recv(2048).decode()
				if flag == '0':
					print('JOIN_GROUP Error !!')
				else:
					print(flag)

			elif msg_split[0] == 'EXIT\n':
				username = ''
				server.send(bytes('LOGOUT\n', 'utf-8'))
				flag_msg = server.recv(2048).decode()
				if flag_msg != 0:
					print(flag_msg)
				else:
					print('Some LOGOUT Error !! Please try again...')
				sys.exit()


			elif msg_split[0] == 'SEND':
				server.send(bytes('CHECK<SEPARATOR>' + msg_split[1] + '<SEPARATOR>' + username + '<SEPARATOR>faltu', 'utf-8'))
				chk_flg = server.recv(2048).decode()
				chk_flg_s = chk_flg.split('<SEPARATOR>')

				if chk_flg_s[0] == 'YES_GROUP':
					all_x = chk_flg_s[1].split('<SEP>')
					all_uname = chk_flg_s[2].split('<SEP>')
					exist_flag = 0
					tmp_var = 0
					filepath = None
					for i2 in range(0, len(all_x) - 1):
						server.send(bytes('SEND<SEPARATOR>' + all_uname[i2] + '<SEPARATOR>faltu3', 'utf-8'))
						flag = server.recv(2048).decode()
						
						if msg_split[2] == 'FILE':
							filepath = msg_split[3][:-1].strip()
							if path.exists(filepath):
								server.send(bytes('FILE<SEP>' + filepath, 'utf-8'))
								f = server.recv(2048).decode()
								tmp_var = 0
								with open(filepath, "rb") as f:
									while True:
										bytes_read = f.read(BUFFER)
										if not bytes_read:
											break
										tmp_var += 1
								server.send(bytes(str(tmp_var), 'utf-8'))
								f = server.recv(2048).decode()
								f_split = f.split('<SEPARATOR>')
								x = int(f_split[0])
								uname = f_split[1]
								with open(filepath, "rb") as f:
									while True:
										bytes_read = f.read(BUFFER)
										if not bytes_read:
											break

										iv = Random.new().read(DES3.block_size)
										
										y = int(all_x[i2])
										key1 = int(pow(y, a, P))
										if key1 == 1:
											key1 += 5
										
										temp = []
										for i in range(16):
											b = (key1 >> (i * 8)) & 0xFF
											temp.append(b)
										
										temp2 = [chr(b) for b in temp]
										key1_main = bytearray(b'')
										for i in temp2:
											key1_main.extend(bytes(i, 'utf-8'))

										cipher_encrypt = DES3.new(bytes(key1_main), DES3.MODE_OFB, iv)
										actual_bytes_read = pad_file_chunk(bytearray(bytes_read))
										encrypted_chunk = cipher_encrypt.encrypt(bytes(actual_bytes_read))

										total = bytearray(b'faltu<SEPARATOR>')
										total.extend(iv)
										total.extend(b'<SEPARATOR>')
										total.extend(encrypted_chunk)
										total.extend(b'<SEPARATOR>')
										total.extend(bytes(uname, 'utf-8'))
										total.extend(b'<SEPARATOR>')
										total.extend(bytes(str(x), 'utf-8'))
										total.extend(b'<SEPARATOR>')
										total.extend(bytes(chk_flg_s[3], 'utf-8'))
										total.extend(b'<SEPARATOR>faltu')
										server.sendall(total)			

										ack = server.recv(2048).decode()
										sleep(0.2)
										
							else:
								server.send(b'NO_FILE')
								f = server.recv(2048).decode()
								exist_flag = 1
								break
							
						else:
							server.send(b'MSG')
							f = server.recv(2048).decode()
							actual = ''
							for i in range(2, len(msg_split)):
								actual += msg_split[i] + ' '
							actual = actual.strip()
							
							iv = Random.new().read(DES3.block_size)

							y = int(all_x[i2])
							key1 = int(pow(y, a, P))
							if key1 == 1:
								key1 += 5
							
							temp = []
							for i in range(16):
								b = (key1 >> (i * 8)) & 0xFF
								temp.append(b)
							
							temp2 = [chr(b) for b in temp]
							key1_main = bytearray(b'')
							for i in temp2:
								key1_main.extend(bytes(i, 'utf-8'))

							cipher_encrypt = DES3.new(bytes(key1_main), DES3.MODE_OFB, iv)
							
							actual_msg = pad(actual)
							encrypted_text = cipher_encrypt.encrypt(bytes(actual_msg, 'utf-8'))

							total = bytearray(iv)
							total.extend(b'<SEPARATOR>')
							total.extend(encrypted_text)
							total.extend(b'<SEPARATOR>GROUP<SEPARATOR>')
							total.extend(bytes(chk_flg_s[3], 'utf-8'))
							server.send(total)
						sleep(0.5)

					if exist_flag == 1:
						print('INVALID File name/path !!')
					elif exist_flag == 0 and tmp_var > 0:
						sleep(0.2)
						print('FILE <' + os.path.basename(filepath) + '> SENT to Group <' + msg_split[1] + '> SUCCESSFULLY !!')

				elif chk_flg_s[0] == 'YES':
					server.send(bytes('SEND<SEPARATOR>' + msg_split[1] + '<SEPARATOR>faltu2', 'utf-8'))
					flag = server.recv(2048).decode()
					
					if msg_split[2] == 'FILE':
						filepath = msg_split[3][:-1].strip()
						if path.exists(filepath):
							server.send(bytes('FILE<SEP>' + filepath, 'utf-8'))
							f = server.recv(2048).decode()
							
							tmp_var = 0
							with open(filepath, "rb") as f:
								while True:
									bytes_read = f.read(BUFFER)
									if not bytes_read:
										break
									tmp_var += 1
							server.send(bytes(str(tmp_var), 'utf-8'))
							f = server.recv(2048).decode()
							f_split = f.split('<SEPARATOR>')
							x = int(f_split[0])
							uname = f_split[1]
							
							with open(filepath, "rb") as f:
								while True:
									bytes_read = f.read(BUFFER)
									if not bytes_read:
										break

									iv = Random.new().read(DES3.block_size)
									
									y = int(chk_flg_s[1])
									key1 = int(pow(y, a, P))
									if key1 == 1:
										key1 += 5
									
									temp = []
									for i in range(16):
										b = (key1 >> (i * 8)) & 0xFF
										temp.append(b)
									
									temp2 = [chr(b) for b in temp]
									key1_main = bytearray(b'')
									for i in temp2:
										key1_main.extend(bytes(i, 'utf-8'))

									cipher_encrypt = DES3.new(bytes(key1_main), DES3.MODE_OFB, iv)
									actual_bytes_read = pad_file_chunk(bytearray(bytes_read))
									encrypted_chunk = cipher_encrypt.encrypt(bytes(actual_bytes_read))

									total = bytearray(b'faltu<SEPARATOR>')
									total.extend(iv)
									total.extend(b'<SEPARATOR>')
									total.extend(encrypted_chunk)
									total.extend(b'<SEPARATOR>')
									total.extend(bytes(uname, 'utf-8'))
									total.extend(b'<SEPARATOR>')
									total.extend(bytes(str(x), 'utf-8'))
									total.extend(b'<SEPARATOR>faltu')
									server.sendall(total)			

									ack = server.recv(2048).decode()
									sleep(0.2)
									
							if tmp_var == 0:
								print('Unable to send file !!')
							else:
								sleep(0.2)
								print('FILE <' + os.path.basename(filepath) + '> SENT to User <' + msg_split[1] + '> SUCCESSFULLY !!')	

						else:
							server.send(b'NO_FILE')
							print('INVALID FILE NAME/PATH !!')
							f = server.recv(2048).decode()	
							continue			
						
					else:
						server.send(b'MSG')
						f = server.recv(2048).decode()
						actual = ''
						for i in range(2, len(msg_split)):
							actual += msg_split[i] + ' '
						actual = actual.strip()
						
						iv = Random.new().read(DES3.block_size)

						y = int(chk_flg_s[1])
						key1 = int(pow(y, a, P))
						if key1 == 1:
							key1 += 5
						
						temp = []
						for i in range(16):
							b = (key1 >> (i * 8)) & 0xFF
							temp.append(b)
						
						temp2 = [chr(b) for b in temp]
						key1_main = bytearray(b'')
						for i in temp2:
							key1_main.extend(bytes(i, 'utf-8'))

						cipher_encrypt = DES3.new(bytes(key1_main), DES3.MODE_OFB, iv)
						
						actual_msg = pad(actual)
						encrypted_text = cipher_encrypt.encrypt(bytes(actual_msg, 'utf-8'))

						total = bytearray(iv)
						total.extend(b'<SEPARATOR>')
						total.extend(encrypted_text)
						server.send(total)
												
				else:
					print('INVALID USERNAME/GROUP NAME !!')
					continue
			else:
				print('PLEASE ENTER A VALID COMMAND...')
			 	
sys.stdout.write('Exiting...') 				
server.close() 