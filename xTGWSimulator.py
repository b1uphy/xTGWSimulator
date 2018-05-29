#!/usr/bin/python
# -*- coding: utf8 -*-
'''
contact:
bluphy@qq.com
@author: bluphy
Created on 2018-5-29 10:55:20
This is a tbox simulator for help developing the TSP simulator.


'''
import socket,time

#HOST = 'server.natappfree.cc'    # The remote host
#HOST = '47.90.92.56'
HOST = '127.0.0.1'
PORT = 9201             # The same port as used by the server

PLAYBACK_FILE_PATH = 'D:\\bluphy\\Desktop\\bw_gb32960_test.log'
TIMER_MSG_UPLOAD_PERIOD = 1
VIN = 'LXVJ2GFC2GA030003'

gInterrupt_flagstr = ''

def responseCtrl_C(func):
    global gInterrupt_flagstr
    def wrapper(*args, **kw):

        try:
            func(*args, **kw)
        except KeyboardInterrupt:
            print('Interrupt by Ctrl-C')
            gInterrupt_flagstr = 'Ctrl-C'
            return None
        
    return wrapper

def sendMsg(socketinstance,msg):
    try:
        socketinstance.sendall(msg)
    except:
        print('[Warning]:Tx Msg fail:data-->',msg.hex())
        return None
    return 0
    
def cmd_login(socketinstance):
    return sendMsg(socketinstance,b'##\x04\xFELXVJ2GFC2GA030003\x01\x00\x08\x11\x11\x11\x11\x11\x11\x33\x33\x33')
    

def cmd_logout(socketinstance):
    return sendMsg(socketinstance,b'##\x04\xFELXVJ2GFC2GA030003\x01\x00\x08\x11\x11\x11\x11\x11\x11\x33\x33\x33')

    
def createOTAmsgfromGBlog(logline):
    msg = None
    if len(logline)>63:
        data = logline.rsplit(':',1)[-1].strip()
        msg = bytes.fromhex(data)
    return msg

def playback(playback_file_descriptor):
    for line in playback_file_descriptor:
        msg = createOTAmsgfromGBlog(line)        
        yield msg

@responseCtrl_C
def cmd_pb(socketinstance):
    global gInterrupt_flagstr
    with open(PLAYBACK_FILE_PATH) as f:
        for msg in playback(f):
            if msg:
                sendMsg(socketinstance,msg)                  
                time.sleep(TIMER_MSG_UPLOAD_PERIOD)
            
def main():
    global gInterrupt_flagstr
    while True:
        cmd1=input('Please enter cmd:\n\tn: create new connection\n\tquit: quit the program\n?>')
        if cmd1 == 'n':
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                connected = False
                try:
                    s.connect((HOST, PORT))
                    connected =True
                except:
                    print('Connecting failed, retry after 10 seconds')
                    time.sleep(10)
                if connected:   
                    clientinfo = s.getsockname() 
                    while True:
                        if len(gInterrupt_flagstr)>0:                            
                            print('Exit cmd2 loop because of ',gInterrupt_flagstr)
                            gInterrupt_flag = ''
                            
                            break
                        print('client:',clientinfo)
                        cmd2=input('Please enter cmd:\n\tlogin: send login msg\n\tq: quit the program\n?>')
                        if 'q' == cmd2:
                            s.close()
                            break
                        elif 'login' == cmd2:
                            cmd_login(s)
                            
                        elif 'logout' == cmd2:
                            cmd_logout(s)
                            
                        elif 'rt' == cmd2: #realtime
                            pass
                            
                        elif 'bf' == cmd2: #bufa
                            pass
                            
                        elif 'bj' == cmd2: 
                            pass
                            
                        elif 'pb' == cmd2:
                            cmd_pb(s)

                        elif 'hb' == cmd2: #heartbeat
                            pass         
                                
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
