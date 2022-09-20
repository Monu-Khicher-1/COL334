import socket
from socket import *
import threading
from _thread import *
import time
import sys


#=======================================================
#=======================================================
#
#   Data Send : Application Layer Packet: If last packet=> ?
#
#
#=======================================================
# File Reading
#=======================================================

Buffer=[]

#=======================================================
lock=threading.Lock()

N=int(sys.argv[1])
text_file = open("./A2_small_file.txt", "r")
data = text_file.read()
text_file.close()
size=len(data)
# print(data)

bytes = len(data.encode('utf-8'))

data_size_for_each_client=(size+N-1)//N 
initial_data_transfer_to_clients=list()
start=0
for i in range(N):
    end=start+data_size_for_each_client                     
    if(end>size):
        end=size
    initial_data_transfer_to_clients.append(data[start:end])
    start=end 

packet_size = data_size_for_each_client//968 
no_of_packets=0

Data=[]
for i in range(N):
    data=initial_data_transfer_to_clients[i]
    j=0
    while(len(data)>968):
        s=data[:968]
        Data.append(s)
        data=data[968:]
        j+=1
    s=data
    Data.append(s)
    j+=1
    no_of_packets=j


#=================================================================
#=================================================================
localIP     = "127.0.0.1"
bufferSize  = 1200
#================================================================
#  Initializing file transfer.
#================================================================

# Packet sent format: packetNumber&start%end/total?data

def format(ID,p):
    if(p==0):
        start=no_of_packets*(ID-1)
        end=no_of_packets*ID
        return str(start+1)+"&"+str(start+1)+"%"+str(end)+"/"+str(len(Data))+"?"+Data[start]
    else:
        start=no_of_packets*(ID-1)
        end=no_of_packets*ID
        return str(p)+"&"+str(start+1)+"%"+str(end)+"/"+str(len(Data))+"?"+Data[p-1]



def server_socket(port):
    UDPServerSocket = socket(family=AF_INET, type=SOCK_DGRAM)
    UDPServerSocket.bind((localIP, port))

    while(True):

        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = int(bytesAddressPair[0].decode())
        address = bytesAddressPair[1]
        port=address[1]
        ID=port-5000+1

        msgFromServer = format(ID,message)
        bytesToSend   = str.encode(msgFromServer)
       
        UDPServerSocket.sendto(bytesToSend, address) 

def Initialization():
    port=20000
    threads=[]
    for i in range(N):
        x=threading.Thread(target=server_socket,args=(port+i,))
        threads.append(x)
        x.start()

# Initialization()

#===========================================================================
# N Sockets for Hearing TCP Requests from the Clients
#===========================================================================
# port=21000 to 21000+N

def Get(m,id):
    global Buffer
    p=""
    for x in Buffer:
        if(m==x[0]):
            p=x[1]
    if(p==""):
        for i in range(N):
            port=8000+i
            TCPClientSocket = socket(AF_INET, SOCK_STREAM)
            TCPClientSocket.connect((localIP,port))

            TCPClientSocket.send(str(m).encode())
            server_message = TCPClientSocket.recv(bufferSize).decode()
            msg=int(server_message)
            TCPClientSocket.send(str(-1).encode())
            TCPClientSocket.close()
            if(msg==1):
                ID=i
                UDPClientSocket = socket(family=AF_INET, type=SOCK_DGRAM)
                msgFromClient = str(m)
                bytesToSend   = str.encode(msgFromClient)
                UDPClientSocket.sendto(bytesToSend, (localIP,9000+i))
                # UDPClientSocket.timeout(2000)
                msgFromServer = UDPClientSocket.recvfrom(bufferSize)[0].decode()
                
                if(len(msgFromServer)>5):
                    p=msgFromServer
                    if([m,p] not in Buffer):
                        Buffer.append([m,p])
                        if(len(Buffer)>N):
                                Buffer=Buffer[1:]
                    break
            

    if(p!=""):
        UDPClientSocket = socket(family=AF_INET, type=SOCK_DGRAM)
        UDPClientSocket.bind(("127.0.0.1",22000+id))
        
        msgFromClient = p
        bytesToSend   = str.encode(msgFromClient)
        UDPClientSocket.sendto(bytesToSend,(localIP, 7000+id-1))

        msgFromServer = int(UDPClientSocket.recvfrom(bufferSize)[0].decode())
            # if(msgFromClient==1):
            #     break
    
    # Sending packet p to client id  through udp.
    
        return "Sent"
    return "Not Sent"


def HearReq(port):
    TCPServerSocket = socket(family=AF_INET, type=SOCK_STREAM)
    TCPServerSocket.bind((localIP, port))
    TCPServerSocket.listen(1)
    while(True):
        connectionSocket, addr = TCPServerSocket.accept()
        ID=0
        while True:
            message = connectionSocket.recv(bufferSize).decode()
            try:
                for i in range(len(message)):
                    if(message[i]=="?"):
                        ID=int(message[:i])
                        message=message[i+1:]
                        break
                message = int(message)
            except:
                print("Some exceptions")
                        
            if message != -1 and ID!=0:
                msg=Get(message,ID)
                connectionSocket.send(msg.encode())
            else: 
                connectionSocket.close()
                break

def MainSockets():
    threads=[]
    for i in range(N):
        x=threading.Thread(target=HearReq,args=(21000+i,))
        threads.append(x)
        x.start()


#================================================================


T1=threading.Thread(target=Initialization,args=())
T2=threading.Thread(target=MainSockets,args=())

T1.start()
T2.start()