import os
import sys
import socket
import struct

bufferSize = 1024

def create_request(opcode, filename):

    opcode_and_length = (opcode << 5) + len(filename)
    filename = filename.encode('utf-8')
    

    if opcode == 0:
        file_size = os.path.getsize(filename)
        request = struct.pack('B', opcode_and_length) + filename + struct.pack('I', file_size)
    elif opcode == 1:
        request = struct.pack('B', opcode_and_length) + filename

    return request

def create_request_change_name(opcode, filename, new_filename):
    opcode_and_length = (opcode << 5) + len(filename)
    filename = filename.encode('utf-8')
    new_filename = new_filename.encode('utf-8')
    request = struct.pack('B', opcode_and_length) + filename + new_filename
    return request


def main():
    first_start = True
    cli_text = "myftp> Press 1 for TCP, Press 2 for UDP: "
    conn_type = ""
    while True:
        command = input(cli_text).strip()
        if (first_start):
            cli_text = "myftp> "
            first_start = False
        
        #------------------------------------------------------------
        # TCP or UDP
        #------------------------------------------------------------
        if command == "1" or command == "2":
            address = input("myftp> Provide IP address and Port number separated by a space: ").split()
            localIP = address[0]
            localPort = address[1]
            localPort = int(localPort)

            if command == "1":
                # TCP selected
                TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                TCPServerSocket.connect((localIP, localPort))
                print("myftp> Session has been established using TCP.")
                conn_type = "TCP"
                
            else:
                # UDP selected
                # Create a datagram socket
                UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                # Bind to address and ip
                UDPServerSocket.connect((localIP, localPort))
                print("myftp> Session has been established using UDP.")
                conn_type = "UDP"

        #------------------------------------------------------------
        # GET
        #------------------------------------------------------------ 
        elif command.startswith("get"):
            filename = command.split()[1]
            opcode = 1 # 001 for get

            request = create_request(opcode, filename)
            print(request)

            # ~~~~~~~~~~~~~~~~~~~~~
            # UDP
            # ~~~~~~~~~~~~~~~~~~~~~
            if conn_type == "UDP":
                # receive file over UDP
                UDPServerSocket.send(request)
                with open(filename, 'wb') as f:
                    while True:
                        data, addr = UDPServerSocket.recvfrom(bufferSize)
                        if data == b'END':
                            print("File transmission completed")
                            break
                        f.write(data)
            
            # ~~~~~~~~~~~~~~~~~~~~~
            # TCP
            # ~~~~~~~~~~~~~~~~~~~~~
            


        #------------------------------------------------------------
        # PUT
        #------------------------------------------------------------
        elif command.startswith("put"):
            filename = command.split()[1]
            opcode = 0 # 000 for put
            

            request = create_request(opcode, filename)
            print(request)

            # ~~~~~~~~~~~~~~~~~~~~~
            # UDP
            # ~~~~~~~~~~~~~~~~~~~~~
            if conn_type == "UDP":
                # Send file over UDP
                UDPServerSocket.send(request)

                with open(filename, 'rb') as f:
                    while True:
                        data = f.read(bufferSize)
                        if not data:
                            break
                        UDPServerSocket.send(data)
                # Send end-of-transmission signal
                UDPServerSocket.send(b'END')
                
            # ~~~~~~~~~~~~~~~~~~~~~
            # TCP
            # ~~~~~~~~~~~~~~~~~~~~~
            elif conn_type == "TCP":
                # Send file over TCP
                TCPServerSocket.send(filename.encode())

                with open(filename, 'rb') as f:
                    while True:
                        data = f.read(bufferSize)
                        if not data:
                            break
                        TCPServerSocket.send(data)
                TCPServerSocket.send(b'END')
         
        #------------------------------------------------------------
        # CHANGE FILENAME
        #------------------------------------------------------------   
        elif command.startswith("change"):
            filename = command.split()[1]
            new_filename = command.split()[2]
            opcode = 3 # 011 for change
            request = create_request_change_name(opcode, filename, new_filename)
            print(request)

            # ~~~~~~~~~~~~~~~~~~~~~
            # UDP
            # ~~~~~~~~~~~~~~~~~~~~~
            if conn_type == "UDP":
                # Send file over UDP
                UDPServerSocket.send(request)

                    
        elif command == "help":
            # he
            pass
        elif command == "bye":
            print("myftp> Session is terminated.")
            break
        else:
            print("myftp> Unknown command.")

main()
