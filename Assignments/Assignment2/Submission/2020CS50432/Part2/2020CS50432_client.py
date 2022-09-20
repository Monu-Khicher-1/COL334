from ast import Return
from re import I
import socket
import threading
from _thread import *
from socket import *
import time
import hashlib
import sys


#=========================
#
localIP="127.0.0.1"
#=========================

N=int(sys.argv[1])
no_of_threads=N
bufferSize=1200
Data={}
PacketsRequired={}
for i in range(no_of_threads):
    Data[i+1]={}

StartOfClients={}
EndOFClients={}
TotalPacketsReq={}

for i in range(N):
    StartOfClients[i+1]=0
    EndOFClients[i+1]=0
    TotalPacketsReq[i+1]=0


def DecodeMsg(msg):
    start=0
    end=0
    TotalPackets=0
    PacketNo=0
    Data=""
    try:
        for i in range(len(msg)):
            if(msg[i]=="&"):
                PacketNo=int(msg[:i])
                msg=msg[i+1:]
                break
    except:
        print("Some exceptions")
   
    try:
        for i in range(len(msg)):
            if(msg[i]=="%"):
                start=int(msg[:i])
                msg=msg[i+1:]
                break
    except:
        print("Some exceptions")
    try:
        for i in range(len(msg)):
            if(msg[i]=="/"):
                end=int(msg[:i])
                msg=msg[i+1:]
                break
    except:
        print("Some exceptions")
    try:
        for i in range(len(msg)):
            if(msg[i]=="?"):
                TotalPackets=int(msg[:i])
                msg=msg[i+1:]
                break
    except:
        print("Some exceptions")
    Data=msg
    
    return [start,end,TotalPackets,PacketNo,Data]

def Required(id):
    for i in range(StartOfClients[id],EndOFClients[id]+1):
        if(i not in list(Data[id].keys())):
            return i 
    return 0

def client(Sport,port):
    serverAddressPort   = ("127.0.0.1", Sport)
    ID=port-5000+1
    UDPClientSocket = socket(family=AF_INET, type=SOCK_DGRAM)
    UDPClientSocket.bind(("127.0.0.1",port))
    done=False
    while(not done):
        if(StartOfClients[ID]==0 and EndOFClients[ID]==0):
            msgFromClient = str(0)
        else:
            x=Required(ID)
            if(x==0):
                done=True
            msgFromClient = str(x)
        bytesToSend   = str.encode(msgFromClient)
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)[0].decode()
        
        msg=DecodeMsg(msgFromServer)
        if(msg[4]!=""):
            StartOfClients[ID]=msg[0]
            EndOFClients[ID]=msg[1]
            TotalPacketsReq[ID]=msg[2]
            Data[ID][msg[3]]=msg[4]
            

def Initialization():
    port=5000
    sport=20000
    threads=[]
    for i in range(N):
        x=threading.Thread(target=client,args=(sport+i,port+i,))
        threads.append(x)
        x.start()
    for i in range(N):
        threads[i].join()

#==============================================================
# N Clients to make Request to the server
#==============================================================

# port from 6000 to 6000+N

def PacketReq(id):
    CurrPackets=list(Data[id].keys())
    CurrPackets.sort()
    size=len(CurrPackets)
    if(CurrPackets[0]>1):
        return CurrPackets[0]-1
    elif(CurrPackets[size-1]<TotalPacketsReq[id]):
        return CurrPackets[size-1]+1
    return 0

RTT=[]
def MakeReq(sport,port):
    global RTT
    ID=port-6000+1
    serverName = "127.0.0.1"
    TCPClientSocket = socket(AF_INET, SOCK_STREAM)
    while(True):
        try:
            TCPClientSocket.connect((serverName,sport))
            break
        except:
            time.sleep(1)
            continue
    # TCPClientSocket.bind((localIP,port))
    done=False
    while(not done):
        x=PacketReq(ID)
        if(x==0):
            done=True
            break
        msg=(str(ID)+"?"+str(x))
        t1=time.time()
        TCPClientSocket.send(msg.encode())
        server_message = TCPClientSocket.recv(bufferSize)
        t2=time.time()
        RTT=RTT+[(t2-t1)]
        
    TCPClientSocket.send(str(-1).encode())
    TCPClientSocket.close()

def ReqPacket():
    t1=time.time()
    Initialization()
    Port=6000
    Sport=21000
    threads=[]
    for i in range(N):
        x=threading.Thread(target=MakeReq,args=(Sport+i,Port+i))
        threads.append(x)
        x.start()
    for t in threads:
        t.join()
    t2=time.time()
    print()
    print("==========================================================")
    print()
    for i in range(N):
        Filedata=Data[i+1]
        s=""
        for j in range(len(Filedata)):
            s+=Filedata[j+1]
        try:
            filename="out"+str(i+1)+".txt"
            foo=open(filename,'w')
            foo.write(s)
            foo.close()
            hash = hashlib.md5(open(filename, 'r').read().encode()).hexdigest()
            print(filename+"    MD5 sum:    ",hash)
        except:
            print("Can't open the file.")
    print()
    print("=========================================================")
    print("Sum of RTT:             ",sum(RTT))
    print("Total Packets:          ",len(RTT))
    Av=sum(RTT)/len(RTT)
    print("Average RTT:            ",Av)
    print("Time Taken:              "+str(t2-t1)+" secs")
    print("=========================================================")
    print()
    print("Done.")

#=============================================================
# UDP Socket to Recieve Packets (Hear at Port 7000)
#=============================================================

def Store(m,id):
    PacketNo=0
    try:
        for i in range(len(m)):
            if(m[i]=="&"):
                PacketNo=int(m[:i])
                m=m[i+1:]
                break
    except:
        print("Some error")
    if(PacketNo!=0):
        Data[id][PacketNo]=m
    return


def recvSocket(port):
    ID=port-7000+1
        
    UDPServerSocket = socket(family=AF_INET, type=SOCK_DGRAM)
    UDPServerSocket.bind((localIP,port))
    
    while(True):
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = (bytesAddressPair[0].decode())
        address = bytesAddressPair[1]
        Store(message,ID)
        msgFromServer = "1"
        bytesToSend   = str.encode(msgFromServer)
        
       
        UDPServerSocket.sendto(bytesToSend, address) 


def RecvMsg():
    threads=[]
    for i in range(N):
        x=threading.Thread(target=recvSocket,args=(7000+i,))
        threads.append(x)
        x.start()

#=====================================================================
# TCP Socket to hear Request for packets
#=====================================================================


def clientSocket(port):
    TCPServerSocket = socket(family=AF_INET, type=SOCK_STREAM)
    TCPServerSocket.bind((localIP, port))
    TCPServerSocket.listen(1)
    ID=port-8000+1
   

    while(True):
        connectionSocket, addr = TCPServerSocket.accept()
        while True:
            message = connectionSocket.recv(bufferSize).decode()
            message = int(message)
            
            if message != -1:
                if(message in list(Data[ID].keys())):
                    connectionSocket.send(str(1).encode())
                else:
                    connectionSocket.send(str(0).encode())
            else: 
                connectionSocket.close()
                break
def HearReq():
    threads=[]
    for i in range(N):
        x=threading.Thread(target=clientSocket,args=(8000+i,))
        threads.append(x)
        x.start()

#=======================================================
# UDP Socket for sending Requested Data
#=======================================================

def socketRes(port):
    UDPServerSocket =socket(family=AF_INET, type=SOCK_DGRAM)
    UDPServerSocket.bind((localIP,port))
    ID=port-9000+1
    while(True):
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = int(bytesAddressPair[0].decode())
        address = bytesAddressPair[1]

        msgFromServer = str(message)+"&"+Data[ID][message]
        bytesToSend   = str.encode(msgFromServer)
        UDPServerSocket.sendto(bytesToSend, address) 

def Res():
    threads=[]
    for i in range(N):
        x=threading.Thread(target=socketRes,args=(9000+i,))
        threads.append(x)
        x.start()
#======================================================

T1=threading.Thread(target=Res,args=())
T2=threading.Thread(target=HearReq,args=())
T3=threading.Thread(target=RecvMsg,args=())
T4=threading.Thread(target=ReqPacket,args=())
T1.start()
T2.start()
T3.start()
T4.start()


