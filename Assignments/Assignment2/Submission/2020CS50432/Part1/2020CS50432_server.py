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
        s=str(len(Data)+1)+"/"+data[:968]
        Data.append(s)
        data=data[968:]
        j+=1
    s=str(len(Data)+1)+"/"+data
    Data.append(s)
    j+=1
    no_of_packets=j


#=================================================================
#=================================================================

# lock=threading.lock()
threads=[]
no_of_threads=N
bufferSize=1200

def clients(c,addr):
     port=addr[1]
     id=port-5000
     start=id*no_of_packets
     while True:
            message = c.recv(bufferSize).decode()
            message = int(message)
            if message != -1:
                if(start<(id+1)*no_of_packets-1):
                    c.send((str(len(Data))+"?"+Data[start]).encode())
                    start+=1
                else:
                    c.send(("?"+str(len(Data))+"?"+Data[start]).encode())
            else: 
                c.close()
                break

def server_socket():
    localIP     = "127.0.0.1"
    localPort   = 20001
   
    TCPServerSocket = socket(family=AF_INET, type=SOCK_STREAM)
    TCPServerSocket.bind((localIP, localPort))
    TCPServerSocket.listen(1)
   
    while(True): 
        connectionSocket, addr = TCPServerSocket.accept()
        x=threading.Thread(target=clients,args=(connectionSocket,addr,))
        x.start()
       



#=========================================================================
#  UDP Socket to hear Requests
#=========================================================================

def Look(msg,ID):
    localIP     = "127.0.0.1"
    global Buffer
    p=""
    for x in Buffer:
        if x[0]==msg:
            p=x[1]
    if(p==""):
        for i in range(N):
            serverName = "127.0.0.1"
            serverPort = 7000+i
            serverAddressPort   = ("127.0.0.1", serverPort)
            # Create a UDP socket at client side
            
            msgFromClient = str(msg)
            bytesToSend   = str.encode(msgFromClient)
            UDPClientSocket = socket(family=AF_INET, type=SOCK_DGRAM)
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            msgFromServer = UDPClientSocket.recvfrom(bufferSize)[0].decode()
            if(int(msgFromServer)!=-1):
                TCPClientSocket = socket(AF_INET, SOCK_STREAM)
                while True:
                    try:
                        TCPClientSocket.connect((serverName,6000+i))
                        break
                    except:
                        time.sleep(1)
                        continue
                

                TCPClientSocket.send(str(msg).encode())
                server_message = TCPClientSocket.recv(bufferSize)
                p=server_message.decode()
                Buffer.append([msg,p])
                if(len(Buffer)>N):
                    Buffer=Buffer[1:]
                TCPClientSocket.send(str(-1).encode())
                TCPClientSocket.close()
    TCPClientSocket = socket(AF_INET, SOCK_STREAM)
    while True:
        try:
            TCPClientSocket.connect((localIP,10000+ID-1))
            break
        except:
            time.sleep(1)
            continue
    TCPClientSocket.send(p.encode())
    server_message = TCPClientSocket.recv(bufferSize)
    TCPClientSocket.close()
         
        
    return p


def Resp(port):
    localIP     = "127.0.0.1"
    UDPServerSocket = socket(family=AF_INET, type=SOCK_DGRAM)
    UDPServerSocket.bind((localIP, port))

    while(True):
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = int(bytesAddressPair[0].decode())
        address = bytesAddressPair[1]
        ID=address[1]-12000+1
       
        msgFromServer = Look(message,ID)

        msgFromServer = str(-1)
        bytesToSend   = str.encode(msgFromServer)
        UDPServerSocket.sendto(bytesToSend, address) 
       
def manageDataReq():
    for i in range(N):
        x=threading.Thread(target=Resp,args=(9000+i,))
        x.start()


T1=threading.Thread(target=manageDataReq,args=())
T2=threading.Thread(target=server_socket,args=())
T2.start()
T1.start()

