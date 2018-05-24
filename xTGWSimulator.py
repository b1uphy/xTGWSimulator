#Echo client program
import socket,time

#HOST = 'server.natappfree.cc'    # The remote host
#HOST = '47.90.92.56'
HOST = '127.0.0.1'
PORT = 9201             # The same port as used by the server
i=1
textin=str(i)
time.sleep(0.003)
#	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
#		s.sendall(b'##\x04\xFELXVJ2GFC2GA030003\x01\x08\x11\x11\x11\x11\x11\x11\x33\x33\x33')
#s.sendall(textin.encode('utf8'))
data = s.recv(1024)
print('Received', repr(data.decode('utf8')))
time.sleep(300)
