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
    elif opcode == 1 or opcode == 3:
        request = struct.pack('B', opcode_and_length) + filename

    return request

def create_request_change_name(opcode, filename, new_filename):
    opcode_and_length = (opcode << 5) + len(filename)
    filename = filename.encode('utf-8')
    new_filename = new_filename.encode('utf-8')
    request = struct.pack('B', opcode_and_length) + filename + new_filename
    return request

def create_request_help(opcode):
    opcode_and_length = (opcode << 5)
    request = struct.pack('B', opcode_and_length)
    return request

def get_opcode_and_length(response: bytes):
    opcode_and_length = response[0]
    return opcode_and_length

def unpack_request_summary(response, filename_length):
    filename = response[1:filename_length+1].decode()
    file_size = struct.unpack('I', response[filename_length+1:filename_length+5])[0]
    return filename, file_size

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

                # receive response from server
                response, _ = UDPServerSocket.recvfrom(bufferSize)
                opcode_and_length = get_opcode_and_length(response)
                opcode = opcode_and_length >> 5
                filename_length = opcode_and_length & 0b00011111

                if opcode == 1: # 001 for GET
                    # receive file over UDP
                    filename, file_size = unpack_request_summary(response, filename_length)
                    print(filename, file_size)

                    with open(filename, 'wb') as f:
                        while True:
                            data, addr = UDPServerSocket.recvfrom(bufferSize)
                            if data == b'END':
                                print("File download completed")
                                break
                            f.write(data)
                
                elif opcode == 3: # 011 for file not found
                    print("Error: File does not exist")
            
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

                # receive response from server
                response, _ = UDPServerSocket.recvfrom(bufferSize)
                response = int.from_bytes(response, 'big')
                
                response_opcode = response >> 5

                if response_opcode == 0:
                    print("File upload successful")
                else:
                    print("Error: File transmission unsuccessful")
                
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
        # SUMMARY
        #------------------------------------------------------------
        elif command.startswith("summary"):
            filename = command.split()[1]
            opcode = 3
            request = create_request(opcode, filename)
            print(request)

            # ~~~~~~~~~~~~~~~~~~~~~
            # UDP
            # ~~~~~~~~~~~~~~~~~~~~~
            if conn_type == "UDP":
                # send request to server
                UDPServerSocket.send(request)

                # receive file over UDP
                response_summary = UDPServerSocket.recv(bufferSize)
                print(response_summary)
                opcode_and_length = get_opcode_and_length(response_summary)
                opcode = opcode_and_length >> 5
                filename_length = opcode_and_length & 0b00011111

                if opcode == 2: # 010 for successful summary
                    filename, filesize = unpack_request_summary(response_summary, filename_length)

                    with open(filename, 'wb') as f:
                        while True:
                            data, addr = UDPServerSocket.recvfrom(bufferSize)
                            if data == b'END':
                                print("Summary downloaded successfully\n")
                                break
                            f.write(data)
                    
                    with open(filename, 'rt') as f:
                        data = f.read()
                        print(data)
                
                elif opcode == 3: # 011 for file not found
                    print("Error: File does not exist")

        #------------------------------------------------------------
        # CHANGE FILENAME
        #------------------------------------------------------------   
        elif command.startswith("change"):
            filename = command.split()[1]
            new_filename = command.split()[2]
            opcode = 2 # 010 for change
            request = create_request_change_name(opcode, filename, new_filename)
            print(request)

            # ~~~~~~~~~~~~~~~~~~~~~
            # UDP
            # ~~~~~~~~~~~~~~~~~~~~~
            if conn_type == "UDP":
                # Send file over UDP
                UDPServerSocket.send(request)
            
                # receive response from server
                response, _ = UDPServerSocket.recvfrom(bufferSize)
                response = int.from_bytes(response, 'big')

                response_opcode = response >> 5
                
                if response_opcode == 0:
                    print("Filename changed from", filename, "to", new_filename)
                elif response_opcode == 5:
                    print("Error: Filename change unsuccessful")
                elif response_opcode == 3:
                    print("Error: Filename change unsuccessful. File does not exist")

        #------------------------------------------------------------
        # HELP
        #------------------------------------------------------------       
        elif command == "help":
            opcode = 4 # 100 for help
            request = create_request_help(opcode)
            print(request)

            # ~~~~~~~~~~~~~~~~~~~~~
            # UDP
            # ~~~~~~~~~~~~~~~~~~~~~
            
            UDPServerSocket.send(request)

            # receive response from server
            response, _ = UDPServerSocket.recvfrom(bufferSize)
            opcode_and_length = get_opcode_and_length(response)
            opcode = opcode_and_length >> 5
            data_length = opcode_and_length & 0b00011111

            if opcode == 6:
                data = response[1:data_length+1].decode()
                print(data)
            
            else:
                print("Error: Unknown request.")


            # ~~~~~~~~~~~~~~~~~~~~~
            # TCP
            # ~~~~~~~~~~~~~~~~~~~~~


        elif command == "bye":
            print("myftp> Session is terminated.")
            break
        else:
            print("Error: Unknown request.")

main()
