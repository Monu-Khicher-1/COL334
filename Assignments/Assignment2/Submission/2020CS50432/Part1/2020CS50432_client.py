from ast import Return
from mimetypes import init
import socket
import threading
from _thread import *
from socket import *
import time
import hashlib
import sys
import matplotlib.pyplot as plt



N=int(sys.argv[1])
no_of_threads=N
bufferSize=1200
Data={}
PacketsRequired={}
for i in range(no_of_threads):
    Data[i+1]={}

RTT=[]
counter=5000

#######################################################
# Some Basics Functions
#######################################################

def DecodeMsg(msg):
    last=False
    if(msg[0]=="?"):
        last=True
        msg=msg[1:]
    no_of_packets=0
    try:
        for i in range(len(msg)):
            if(msg[i]=="?"):
                no_of_packets=int(msg[:i])
                msg=msg[i+1:]
                break
    except:
        print("Some exceptions")
    Packet_no=0
    try:
        for i in range(len(msg)):
            if(msg[i]=="/"):
                Packet_no=int(msg[:i])
                msg=msg[i+1:]
                break
    except:
        print("Some exceptions")
    data=msg
    return [last,no_of_packets,Packet_no,data]


#########################################################
# Initialization of Packet Transfer
#########################################################


def clients(port):
    serverName = "127.0.0.1"
    serverPort = 20001
    ID=port-counter+1

    TCPClientSocket = socket(AF_INET, SOCK_STREAM)
    TCPClientSocket.bind(("",port))
    TCPClientSocket.connect((serverName,serverPort))
    done=False
    while(not done):
        TCPClientSocket.send(str(0).encode())
        server_message = TCPClientSocket.recv(1200)
        Decoded=DecodeMsg(server_message.decode())
        if(Decoded[0]):
            done=True
        Data[ID][Decoded[2]]=Decoded[3]
        PacketsRequired[ID]=Decoded[1]
    TCPClientSocket.send(str(-1).encode())
    TCPClientSocket.close()

    
def client_threads():
    threads=[]
    for i in range(no_of_threads):
        x=threading.Thread(target=clients,args=(counter+i,))
        threads.append(x)
        x.start()
    for t in threads:
        t.join()
   


# wait clients to join... 

####################################################################
# Client UDP Packet request to the server
####################################################################
#
def PacketReq(id):
    CurrPackets=list(Data[id].keys())
    CurrPackets.sort()
    size=len(CurrPackets)
    if(CurrPackets[0]>1):
        return CurrPackets[0]-1
    elif(CurrPackets[size-1]<PacketsRequired[id]):
        return CurrPackets[size-1]+1
    return 0
RTT=[]
# Make Request on ports=9000+_
def makeReq(Sport,port):
    global RTT
    ID=port-12000+1
    serverAddressPort   = ("127.0.0.1", Sport)
    # Create a UDP socket at client side
    while(True):
        p=PacketReq(ID)
        if(p==0):
            break
        t1=time.time()
        UDPClientSocket = socket(family=AF_INET, type=SOCK_DGRAM)
        UDPClientSocket.bind(("127.0.0.1",port))
        msgFromClient = str(p)
        bytesToSend   = str.encode(msgFromClient)
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        t2=time.time()
        RTT=RTT+[(t2-t1)]
def Req():
    t1=time.time()
    client_threads()
    threads=[]
    for i in range(N):
        x=threading.Thread(target=makeReq,args=(9000+i,12000+i))
        threads.append(x)
        x.start()
    for t in threads:
        t.join()
    t2=time.time()
    print()
    print("================================================================")
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
            print(filename+"     MD5 sum:  ",hash)
        except:
            print("Can't open the file.")
    print()
    print("================================================================")
    print("Sum of RTT:                  ",sum(RTT))
    print("Total Packets:               ",len(RTT))
    Av=sum(RTT)/len(RTT)
    print("Average RTT:                 ",Av)
    # plt.plot(RTT)
    # plt.show()
    print("Time Taken:                   "+str(t2-t1)+" secs")
    print("================================================================")
    print()


# ---------------Code for making Req for all clients---------------

#
####################################################################
# Clients TCP Socket for data rquest for packet p
####################################################################

def reqthread(connectionSocket,ID):
        message = connectionSocket.recv(bufferSize).decode()
        message = int(message)
        if message != -1:
            if (message in list(Data[ID].keys())):
                connectionSocket.send((str(message)+"/"+Data[ID][message]).encode())
            else:
                connectionSocket.send((str(message)+"/").encode())
        connectionSocket.close()
        
def req(port):
    ID=port-6000+1
    localIP     = "127.0.0.1"
    TCPServerSocket = socket(family=AF_INET, type=SOCK_STREAM)
    TCPServerSocket.bind((localIP,port))
    TCPServerSocket.listen(1)
    # print("TCP server"+str(ID)+" up and listening")

    while(True):
        connectionSocket, addr = TCPServerSocket.accept()
        x=threading.Thread(target=reqthread,args=(connectionSocket,ID))
        x.start()
        

def DataReq():
    threads=[]
    port=6000
    for i in range(no_of_threads):
        x=threading.Thread(target=req,args=(port+i,))
        threads.append(x)
        x.start()

#=====================================================================
# UDP Socket to hear request for packet
#=====================================================================

def reqpackets(ID,bytesAddressPair,UDPServerSocket):
        message = int(bytesAddressPair[0].decode())
        address = bytesAddressPair[1]

        msgFromServer = str(-1)
        if(message in list(Data[ID].keys())):
            msgFromServer = "1"
        bytesToSend   = str.encode(msgFromServer)
        UDPServerSocket.sendto(bytesToSend, address) 


def ReqForPackets(port):
    localIP     = "127.0.0.1"
    ID=port-7000+1

    UDPServerSocket = socket(family=AF_INET, type=SOCK_DGRAM)
    UDPServerSocket.bind((localIP, port))

    # print("UDP server up and listening")

    while(True):
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        x=threading.Thread(target=reqpackets,args=(ID,bytesAddressPair,UDPServerSocket,))
        x.start()
        

def HearForPacketReq():
    threads=[]
    port=7000
    for i in range(no_of_threads):
        x=threading.Thread(target=ReqForPackets,args=(port+i,))
        threads.append(x)
        x.start()

#===============================================================
# TCP Socket to Recive msg
#===============================================================
def Read(msg):
    Packets_No=0
    try:
        for i in range(len(msg)):
            if(msg[i]=="/"):
                Packets_No=int(msg[:i])
                msg=msg[i+1:]
                break
    except:
        print("Some exceptions")
    data=msg
    return [Packets_No,data]


def Recvmsg(port):
    ID=port-10000+1
    localIP     = "127.0.0.1"
    TCPServerSocket = socket(family=AF_INET, type=SOCK_STREAM)
    TCPServerSocket.bind((localIP,port))
    TCPServerSocket.listen(1)
    threads=[]
    while(True):
        connectionSocket, addr = TCPServerSocket.accept()
        message = connectionSocket.recv(bufferSize).decode()
        try:
            if len(message) > 5:
                s=Read(message)
                Data[ID][s[0]]=s[1]
        except:
            print("Error!")
        connectionSocket.send(str(-1).encode())
        connectionSocket.close()
        
          

        
def RecvPackets():
    threads=[]
    port=10000
    for i in range(no_of_threads):
        x=threading.Thread(target=Recvmsg,args=(port+i,))
        threads.append(x)
        x.start()

T1=threading.Thread(target=HearForPacketReq,args=())
T2=threading.Thread(target=RecvPackets,args=())
T3=threading.Thread(target=DataReq,args=())
T4=threading.Thread(target=Req,args=())
T1.start()
T2.start()
T3.start()
T4.start()
