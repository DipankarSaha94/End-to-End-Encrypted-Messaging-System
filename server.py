import socket 
import select 
import sys 
from _thread import *
import tqdm
import os
from time import *

class users:
	def __init__(self, ip, port, username, password, conn, login, x):
		self.ip = ip
		self.port = port
		self.username = username
		self.password = password
		self.conn = conn
		self.login = login
		self.x = x

class groups:
	def __init__(self, group_name, owner):
		self.group_name = group_name
		self.owner = owner
		self.group_members = []
		self.mem_count = 1

user_list = []
group_list = []

BUFFER = 4096
BUFFER2 = 4096 + 2048
SEPARATOR = '<FALTU>'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

if len(sys.argv) != 3: 
	print ("Correct usage: script, IP address, port number") 
	exit() 

IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 

server.bind((IP_address, Port)) 
server.listen(50)
print('SERVER <' + IP_address + '> listening on port <' + str(Port) + '>...')

list_of_clients = [] 

def clientthread(conn, addr): 
	conn.send(b"## Welcome to Terminal-Whatsapp ##")
	while True: 
		#try: 
			message = conn.recv(2048).decode()
			msg_split = message.split('<SEPARATOR>')
			if msg_split[0] == 'SIGNUP':
				fl = 0
				for usr in user_list:
					if usr.username == msg_split[1]:
						fl = 1 
						break
				if fl == 0:
					u = users(addr[0], addr[1], msg_split[1], msg_split[2], conn, 0, 0)
					user_list.append(u)
					conn.send(b'1')
					continue
				else:
					conn.send(b'0')

			if msg_split[0] == 'X':
				for u in user_list:
					if u.conn == conn and u.login == 1:
						u.x = int(msg_split[1])

			if msg_split[0] == 'LOGIN':
				fl = 0
				for usr in user_list:
					if msg_split[1] == usr.username and msg_split[2] == usr.password and usr.login == 0:
						usr.login = 1
						usr.conn = conn
						print("User: <" + usr.username + "> Logged in !!")
						fl = 1
						conn.send(b'1')
						break
				if fl == 0:
					conn.send(b'0')
					continue

			if msg_split[0] == 'LOGOUT\n':
				fl = 0
				for usr in user_list:
					if conn == usr.conn and usr.login == 1:
						usr.login = 0
						usr.conn = None
						print('<' + usr.username + '> LOGGED OUT !!')
						conn.send(bytes('<' + usr.username + '> LOGGED OUT Successfully !!', 'utf-8'))
						fl = 1
						break
				if fl == 1:
					continue
				else:
					print('<' + usr.username + '> LOGOUT ERROR...')
					conn.send(b'0')

			if msg_split[0] == 'CREATE':
				fl = 0
				for g in group_list:
					if g.group_name == msg_split[1]:
						fl = 1
						conn.send(b'0')
						break
				if fl == 0:
					fl2 = 0
					for usr in user_list:
						if usr.conn == conn and usr.login == 1:
							gr = groups(msg_split[1], usr.username)
							gr.group_members.append(usr.username)
							group_list.append(gr)
							conn.send(bytes('Group <' + msg_split[1][:-1] + '> CREATED Successfully !!', 'utf-8'))
							fl2 = 1
							break
					if fl2 == 0:
						conn.send(b'0')

			if msg_split[0] == 'LIST\n':			
				fl = 0
				for usr in user_list:
					if usr.conn == conn and usr.login == 1:
						fl = 1
						break
				if fl == 0:
					conn.send(b'0')
					continue
				else:
					msg = 'GROUP_NAME\tOWNER\tMEMBERS\tMEMBER_COUNT\n'
					for g in group_list:
						msg2 = ''
						for mem in g.group_members:
							msg2 += mem + ', '
						msg += g.group_name[:-1] + '\t\t' + g.owner + '\t(' + msg2 + ')\t' + str(g.mem_count) + '\n'
					conn.send(bytes(msg, 'utf-8'))

			if msg_split[0] == 'JOIN':
				fl = 0
				for usr in user_list:
					if usr.conn == conn and usr.login == 1:
						fl = 1
						break
				if fl == 0:
					conn.send(b'0')
					continue
				else:
					fl2 = 0
					for g in group_list:
						if msg_split[1] == g.group_name:
							fl2 = 1
							usr = ''
							for u2 in user_list:
								if u2.conn == conn:
									usr = u2.username
									break
							if usr not in g.group_members:
								g.group_members.append(usr)
								g.mem_count += 1
								conn.send(bytes('You joined the group <' + g.group_name[:-1] + '> Successfully !!', 'utf-8'))
							else:
								conn.send(bytes('You CANNOT JOIN the group <' + g.group_name[:-1] + '> again..', 'utf-8'))
							break
					if fl2 == 0:
						conn.send(b'0')

			if msg_split[0] == 'CHECK':
				flag = b'NO<SEPARATOR>faltu'
				fl = 0
				for u in user_list:
					if u.username == msg_split[1] and u.login == 1:
						flag = bytes('YES<SEPARATOR>' + str(u.x) + '<SEPARATOR>faltu', 'utf-8') 
						fl = 1
						break
				if fl == 0:
					grp_name = msg_split[1] + '\n'
					for g in group_list:
						if g.group_name == grp_name and msg_split[2] in g.group_members:
							str_x = ''
							str_uname = ''
							for u4 in user_list:
								if u4.conn != conn and u4.login == 1 and u4.username in g.group_members:
									str_x += str(u4.x) + '<SEP>'
									str_uname += str(u4.username) + '<SEP>'
							str_x = str_x + '0'
							str_uname = str_uname + 'faltu'
							flag = bytes('YES_GROUP<SEPARATOR>' + str_x + '<SEPARATOR>' + str_uname + '<SEPARATOR>' + grp_name + '<SEPARATOR>faltu', 'utf-8') 
							break
				conn.send(flag)

			if msg_split[0] == 'DIFFIE':
				flag = 0
				for u in user_list:
					if u.username == msg_split[2]:
						print('Server received x.. sending:', msg_split[1])
						u.conn.send(bytes('KEY ' + msg_split[1] + ' faltu', 'utf-8'))
						ack = u.conn.recv(2048)
						print('Server received y.. sending:', ack)
						conn.send(ack)
						flag = 1
						break

			if msg_split[0] == 'SEND':
				usr_or_grp = msg_split[1]
				conn.send(b'ACK')
				msg_type = conn.recv(2048).decode()
				conn.send(b'ACK')

				msg_file = msg_type.split('<SEP>')
				
				if msg_type == 'NO_FILE':
					continue			
				elif msg_file[0] == 'FILE':
					for u in user_list:
						if u.conn == conn and u.login == 1:
							tmp5 = 0
							for usr in user_list:
								if usr.username == usr_or_grp and usr != u:
									itr = int(conn.recv(2048).decode())
									conn.send(bytes(str(u.x) + '<SEPARATOR>' + u.username + '<SEPARATOR>faltu', 'utf-8'))
									usr.conn.send(bytes('FILE<SEPARATOR>' + msg_file[1] + '<SEPARATOR>' + str(itr) + '<SEPARATOR>faltu_again', 'utf-8'))
									for i in range(0, itr):
										b = conn.recv(BUFFER2)
										conn.send(b'ACK')
										b_s = b.split(b'<SEPARATOR>')
										usr.conn.sendall(b)
								
									tmp5 = 1
									break
							if tmp5 == 0:
								pass
					continue

				elif msg_type == 'MSG':
					flag1 = 0
					for u in user_list:
						if u.conn == conn and u.login == 1:
							flag2 = 0
							for usr in user_list:
								if usr.username == usr_or_grp and usr != u and usr.login == 1:
									#conn.send(b'ACK')
									m = bytearray(conn.recv(2048))
									m.extend(b'<SEPARATOR>')
									m.extend(bytes(u.username, 'utf-8'))
									m.extend(b'<SEPARATOR>')
									m.extend(bytes(str(u.x) + '<SEPARATOR>faltu', 'utf-8'))
									#print('m:', m)
									usr.conn.send(m)
									flag2 = 1
									break
							flag1 = 1
							break
					if flag1 == 0:
						conn.send(b'LOGIN_ERROR')
						continue

while True: 
	conn, addr = server.accept() 
	list_of_clients.append(conn) 
	print ("<" + addr[0] + "><" + str(addr[1]) + "> connected") 
	start_new_thread(clientthread,(conn, addr)) 

conn.close() 
server.close() 