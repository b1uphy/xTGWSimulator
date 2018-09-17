#!/usr/bin/python
# -*- coding: utf8 -*-
'''
contact:
bluphy@qq.com
@author: bluphy
Created on 2018-5-29 10:55:20
This is a tbox simulator for help developing the TSP simulator.


'''
#修改包的检索路径，以便引入xOTAGB
import sys  
sys.path.append("D:\\bluphy\\vscwork\\PythonSpace")
 
import socket,time,threading
from  xTSPSimulator.xOTAGB import calBCCChk, createOTAGBMsg, genGBTime

#### <Config>
#HOST = 'server.natappfree.cc'    # The remote host
#HOST = '47.90.92.56'
# HOST = '127.0.0.1'
HOST = '192.168.1.14'
PORT = 9201             # The same port as used by the server

#PLAYBACK_FILE_PATH = 'D:\\bluphy\\Desktop\\bw_gb32960_test.log'
PLAYBACK_FILE_PATH = 'D:\\work\\4.TBox legacy\\S5N1\\log\\20180427_S5N1过检\\bw_gb32960_test.log'
TIMER_MSG_UPLOAD_PERIOD = 1
VIN = b'LXVJ2GFC2GA030003'
ICCID = b'89860617010001351357'
#### </Config>

gInterrupt_flagstr = ''
gConnected_flag = False
gSocket = None
gFlowNum = 1

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

#### <Service>
def createSocket(host=HOST,port=PORT):
    global gSocket, gConnected_flag
    print('Creating socket...')
    try:
        gSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #gSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,)
        gSocket.connect((host,port))
        gSocketName = gSocket.getsockname()
        print('Client info: ',gSocketName)
        gConnected_flag = True
    except:
        print('Connecting failed, retry after 10 seconds')
        time.sleep(10)

def closeSocket():
    global gSocket, gConnected_flag
    if gSocket:
        gSocket.close()
        gConnected_flag =False
        gSocket = None
        print('TCP连接已断开')
    
def prepareSocket(host=HOST,port=PORT):
    print('function = getsocket')
    global gSocket, gConnected_flag
    if not gConnected_flag:
        print('Soket is not initiated. Now create the soclet.')
        createSocket()
    else:
        error = gSocket.getsockopt(socket.SOL_SOCKET,socket.SO_ERROR)
        if error == 0:
            try:
                gSocket.sendall(b'')
                print('Connection is OK')
            #except ConnectionAbortedError:
            #except ConectionResetError:
            except:
                gConnected_flag = False
                createSocket()
        else:
            print('Connection is not ready, prepairing...')
            try:
                gSocket.close()                
            except OSError:
                pass
            gConnected_flag = False
            createSocket()
            
@responseCtrl_C
def daemonSocket():
    while True:
        pass

            
def sendMsg(msg):
    global gSocket,gConnected_flag
    print('sending msg: ', msg[:24].hex())
    
    #retryflag = True
    delay = 1
    prepareSocket()
    try:
        wresult = gSocket.sendall(msg)
        result = 0        
        #retryflag = False
    except:
        gConnected_flag =False
        #retryflag = True            
        print('[Warning]:Tx Msg fail:data-->',msg.hex())
        print('Retry after {0} seconds...'.format(delay))
        time.sleep(delay)
        delay = 10
        result = -1
    finally:
        print('cmd= ',msg[2])
        if msg[2] == 4:
            print('Wait to close socket...')
            time.sleep(0.03)
            closeSocket()
        return result

def readMsg():
    global gSocket,gConnected_flag
    while True:
        msg = None 
        if gConnected_flag:
            try:
                msg = gSocket.recv(1024)
                print('rx: ',msg,'\n?>',end='')
            except:
                gConnected_flag =False
            else:
                if msg == b'':
                    gConnected_flag = False
    
        
def createOTAmsgfromGBlog(logline):
    msg = None
    if len(logline)>63:
        data = logline.rsplit(':',1)[-1].strip()
        msg = bytes.fromhex(data)
    return msg

#### </Service>

#### <APP>


def cmd_login():
    '''
    232301FE4C58564433473242364A4130303032303501001E12041B09281F000438393836303631373031303030313335313335370100E7
    '''
    global gFlowNum
    if gFlowNum >= 65535: 
        gFlowNum = 1
    msg = createOTAGBMsg(b'\x01', b'\xFE', VIN, 1, 30, genGBTime()+gFlowNum.to_bytes(2,'big')+ICCID+b'\x01\x00')
    
    return sendMsg(msg)
    

def cmd_logout():
    global gFlowNum
    msg = createOTAGBMsg(b'\x04', b'\xFE', VIN, 1, 8, genGBTime()+gFlowNum.to_bytes(2,'big'))
    gFlowNum =gFlowNum + 1
    return sendMsg(msg)
    
    
def cmd_rt():
    return sendMsg(b'##\x01\xFELXVJ2GFC2GA030003\x01\x00\x08\x11\x11\x11\x11\x11\x11\x33\x33\x33')

def cmd_bf():
    return sendMsg(b'##\x01\xFELXVJ2GFC2GA030003\x01\x00\x08\x11\x11\x11\x11\x11\x11\x33\x33\x33')

def playback(playback_file_descriptor):
    for line in playback_file_descriptor:
        #print(line[:52])
        msg = createOTAmsgfromGBlog(line)        
        yield msg

@responseCtrl_C
def cmd_pb():
    global gInterrupt_flagstr
    try:
        with open(PLAYBACK_FILE_PATH) as f:
            for msg in playback(f):
                if msg:
                    sendMsg(msg)
                    time.sleep(TIMER_MSG_UPLOAD_PERIOD)
    except FileNotFoundError:
        print('ERROR:file does not exist.')

#### </APP>  
            
def main():
    global gInterrupt_flagstr, gConnected_flag, gSocket
    while True:
        cmd1=input('Please enter cmd:\n\tn: create new connection\n\tm: manual mode\n\ta: auto mode\n\tpb: playback log file\n\tquit: quit the program\n?>')
        readthread = threading.Thread(target=readMsg,name= 'thread_1')	
        readthread.setDaemon(True)
        readthread.start()
        if cmd1 == 'm':
            while True:
                if len(gInterrupt_flagstr)>0:                            
                    print('Exit cmd2 loop because of ',gInterrupt_flagstr)
                    gInterrupt_flagstr = ''
                    break
                cmd2=input('Please enter cmd:\n\tin: send login msg\n\tout: send logout msg\n\tq: quit the program\n?>')
                if 'q' == cmd2:
                    closeSocket()
                    break
                elif 'in' == cmd2: #登入
                    while(cmd_login()<0):                       
                        pass
                    
                elif 'out' == cmd2: #登出
                    cmd_logout()
                    
                elif 'rt' == cmd2: #实时
                    pass
                    
                elif 'bf' == cmd2: #补发
                    pass
                    
                elif 'bj' == cmd2: #报警
                    pass
                    
                elif 'hb' == cmd2: #心跳
                    pass         
                        
                else:
                    pass
                    #gSocket.sendall((cmd2+'\n').encode('utf8'))

        elif 'a' == cmd1:
            pass

        elif 'pb' == cmd1: #回放
            cmd_pb()


        elif cmd1 == 'quit':
            break
        #   
        #   data = s.recv(1024)
        #   print('Received', repr(data.decode('utf8')))
        #time.sleep(300)


if __name__ == '__main__':
    main()
