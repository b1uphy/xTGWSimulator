#Echo client program
import socket,time

#HOST = 'server.natappfree.cc'    # The remote host
#HOST = '47.90.92.56'
HOST = '127.0.0.1'
PORT = 9201             # The same port as used by the server

PLAYBACK_FILE_PATH = 'D:\\bluphy\\Desktop\\bw_gb32960_test.log'

def responseCtrl_C(func):
    def wrapper(*args, **kw):

        try:
            func(*args, **kw)
        except KeyboardInterrupt:
            return None
        
    return wrapper
 


def createOTAmsgfromGBlog(logline):
    msg = None
    if len(logline)>63:
        msg = bytes.fromhex(logline[45:-1])
    return msg

def playback(playback_file_descriptor):
    for line in playback_file_descriptor:
        msg = createOTAmsgfromGBlog(line)
        yield msg

@responseCtrl_C
def cmd_pb(socketinstance):
    with open(PLAYBACK_FILE_PATH) as f:
        for msg in playback(f):
            if msg:
                socketinstance.sendall(msg)
                #time.sleep(1)

       
def main():
    while True:
        cmd1=input('Please enter cmd:\n\tnew: create new connection\n\tquit: quit the program\n?>')
        if cmd1 == 'new':
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                clientinfo = s.getsockname() 
                while True:
                    print('client:',clientinfo)
                    cmd2=input('Please enter cmd:\n\tlogin: send login msg\n\tq: quit the program\n?>')
                    if 'q' == cmd2:
                        s.close()
                        break
                    elif 'login' == cmd2:
                        s.sendall(b'##\x04\xFELXVJ2GFC2GA030003\x01\x08\x11\x11\x11\x11\x11\x11\x33\x33\x33')
                        
                    elif 'logout' == cmd2:
                        pass
                        
                    elif 'rt' == cmd2:
                        pass
                        
                    elif 'bf' == cmd2:
                        pass
                        
                    elif 'bj' == cmd2:
                        pass
                        
                    elif 'pb' == cmd2:
                        cmd_pb(s)         
                            
                    else:
                        s.sendall((cmd2+'\n').encode('utf8'))
        elif cmd1 == 'quit':
            break
        #   
        #   data = s.recv(1024)
        #   print('Received', repr(data.decode('utf8')))
        #time.sleep(300)


if __name__ == '__main__':
    main()
