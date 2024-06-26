import os
import socket
import sys
import threading
import struct

#===============================================================================
# This server program is designed to receive requests from clients and perform 
# the following operations:
# PUT: Receives a file from the client and saves it in the server
# GET: Sends a file to the client
# CHANGE: Changes the name of a file in the server
# SUMMARY: Sends a summary file to the client containing the minimum, maximum and average of the numbers in the file
# HELP: Sends a help message to the client
# The server can handle both TCP and UDP connections and can run concurrently
#===============================================================================


#===============================================================================
# Utility functions
#===============================================================================

def get_opcode_and_length(request):
    opcode_and_length = request[0]
    return opcode_and_length

def unpack_request_put(request, filename_length):
    filename = request[1:filename_length+1].decode()
    file_size = struct.unpack('I', request[filename_length+1:filename_length+5])[0]
    return filename, file_size

def unpack_request_get(request, filename_length):
    filename = request[1:filename_length+1].decode()
    return filename

def unpack_request_change(request, filename_length):
    filename = request[1:filename_length+1].decode()
    new_filename = request[filename_length+1:].decode()
    return filename, new_filename

def unpack_request_summary(request, filename_length):
    filename = request[1:filename_length+1].decode()
    return filename

def create_request(opcode, filename):
    opcode_and_length = (opcode << 5) + len(filename)
    filename = filename.encode('utf-8')
    file_size = os.path.getsize(filename)
    request = struct.pack('B', opcode_and_length) + filename + struct.pack('I', file_size)
    return request

#===============================================================================
# UDP
#===============================================================================
def udp_connection(localIP, localPort, bufferSize):
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.bind((localIP, localPort))
    print("UDP server up and listening")

    while True:
            # Receiving filename from the client
            udp_request = UDPClientSocket.recvfrom(bufferSize)
            if debug: print(udp_request)
            opcode_ang_length = get_opcode_and_length(udp_request[0]) 
            opcode = opcode_ang_length >> 5
            filename_length = opcode_ang_length & 0b00011111

            #------------------------------------------------------------
            # PUT
            #------------------------------------------------------------        
            if opcode == 0: #000 for PUT
                filename, file_size = unpack_request_put(udp_request[0], filename_length)
                with open(filename, 'wb') as f:
                    while True:
                        data, addr = UDPClientSocket.recvfrom(bufferSize)
                        if data == b'END':
                            if debug: print("File transmission completed")
                            break
                        f.write(data)

                # checking if transmission successful and sending response
                if os.path.getsize(filename) == file_size:
                    response = 0 # 000 for successful transmission
                else:
                    response = 7 # 111 for unsuccessful transmission
                    
                # convert to bytes
                response = response << 5
                response = response.to_bytes(1, 'big')
                UDPClientSocket.sendto(response, udp_request[1])



            #------------------------------------------------------------
            # GET
            #------------------------------------------------------------
            elif opcode == 1: #001 for GET
                filename = unpack_request_get(udp_request[0], filename_length)
                

                # checking to see if file exists
                if os.path.isfile(filename):
                    response = create_request(1, filename)
                    if debug: print(response)
                    UDPClientSocket.sendto(response, udp_request[1])

                    # sending file to client
                    with open(filename, 'rb') as f:
                        while True:
                            data = f.read(bufferSize)
                            if not data:
                                break
                            UDPClientSocket.sendto(data, udp_request[1])
                    UDPClientSocket.sendto(b'END', udp_request[1])

                else:
                    response = 3 # 011 for file does not exist
                    response = response << 5
                    response = response.to_bytes(1, 'big')
                    UDPClientSocket.sendto(response, udp_request[1])
                
                
                

            #------------------------------------------------------------
            # CHANGE FILENAME
            #------------------------------------------------------------
            elif opcode == 2: #011 for CHANGE
                filename, new_filename = unpack_request_change(udp_request[0], filename_length)
                
                # checking to see if file exists
                if os.path.isfile(filename):

                    os.rename(filename, new_filename)
                    if debug: print("Filename changed from", filename, "to", new_filename)

                    # send response
                    if os.path.isfile(new_filename) and not os.path.isfile(filename):
                        response = 0 # 000 for successful transmission
                    else:
                        response = 5 # 101 for unsuccessful name change
                else:
                    response = 3 # 011 for file does not exist

                # convert to bytes
                response = response << 5
                response = response.to_bytes(1, 'big')
                UDPClientSocket.sendto(response, udp_request[1])

            #------------------------------------------------------------
            # SUMMARY
            #------------------------------------------------------------
            elif opcode == 3: #011 for SUMMARY
                filename = unpack_request_summary(udp_request[0], filename_length)

                # checking to see if file exists
                if os.path.isfile(filename):
                    with open (filename, 'rt') as f:
                        data = f.read()
                        data = data.split()
                        data = [int(i) for i in data] # convert strings to integers

                        minimum = min(data)
                        maximum = max(data)
                        average = sum(data) / len(data)

                        if debug:
                            print("Minimum:", minimum)
                            print("Maximum:", maximum)
                            print("Average:", average)

                        response_filename = "summary.txt"
                        # writing to new file

                        with open(response_filename, 'w') as f:
                            f.write("Minimum: " + str(minimum) + "\n")
                            f.write("Maximum: " + str(maximum) + "\n")
                            f.write("Average: " + str(average) + "\n")
                        
                        response = create_request(2, response_filename) # 010 for SUMMARY
                        if debug: print(response)
                        UDPClientSocket.sendto(response, udp_request[1])
                        # sending summary file to client
                        with open(response_filename, 'rb') as f:
                            while True:
                                data = f.read(bufferSize)
                                if not data:
                                    break
                                UDPClientSocket.sendto(data, udp_request[1])
                        UDPClientSocket.sendto(b'END', udp_request[1])   

                        # deleting summary file
                        os.remove(response_filename)                 

                else:
                    response = 3 # 011 for file does not exist
                    response = response << 5
                    response = response.to_bytes(1, 'big')
                    UDPClientSocket.sendto(response, udp_request[1])
            #------------------------------------------------------------
            # HELP
            #------------------------------------------------------------
            elif opcode == 4: #100 for HELP
                response = 6 # 110 for help
                response = response << 5
                help_message = "PUT\nGET\nCHANGE\nSUMMARY\nHELP"
                response += len(help_message)
                response = response.to_bytes(1, 'big')
            
                response = response + help_message.encode('utf-8')

                UDPClientSocket.sendto(response, udp_request[1])

            #------------------------------------------------------------
            # UNKNOWN REQUEST
            #------------------------------------------------------------
            else:
                if debug: print("Error: Unknown request")
                response = 4 # 100 for unknown request
                response = response << 5
                response = response.to_bytes(1, 'big')
                UDPClientSocket.sendto(response, udp_request[1])


#===============================================================================
# TCP
#===============================================================================
def tcp_connection(localIP, localPort, bufferSize):
    TCPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCPClientSocket.bind((localIP, localPort))
    print("TCP server up and listening")
    while (True):
        TCPClientSocket.listen(1)
        connection, address = TCPClientSocket.accept()
        if debug: print("Connection from", address)
        while (True):
            # Receiving filename from the client
            tcp_request = connection.recv(bufferSize)
            if debug: print(tcp_request)
            opcode_ang_length = get_opcode_and_length(tcp_request) 
            opcode = opcode_ang_length >> 5
            filename_length = opcode_ang_length & 0b00011111
            if debug: print("Opcode:", opcode)

            #------------------------------------------------------------
            # PUT
            #------------------------------------------------------------        
            if opcode == 0:
                filename, file_size = unpack_request_put(tcp_request, filename_length)
                with open(filename, 'wb') as f:
                    while True:
                        data = connection.recv(bufferSize)
                        if b'END' in data:
                            # Find the index of b'END' in data
                            end_index = data.index(b'END')
                            # Write everything before b'END' to the file
                            f.write(data[:end_index])
                            if debug: print("File transmission completed")
                            break
                        f.write(data)

                # checking if transmission successful and sending response
                if os.path.getsize(filename) == file_size:
                    response = 0 # 000 for successful transmission
                else:
                    response = 7 # 111 for unsuccessful transmission
                
                # convert to bytes
                if debug: print (filename)
                if debug: print (os.path.getsize(filename))
                if debug: print (file_size)
                if debug: print(response)
                response = response << 5
                response = response.to_bytes(1, 'big')
                connection.send(response)

            #------------------------------------------------------------
            # GET
            #------------------------------------------------------------
            elif opcode == 1:
                filename = unpack_request_get(tcp_request, filename_length)

                # checking to see if file exists
                if os.path.isfile(filename):
                    response = create_request(1, filename)
                    if debug: print(response)
                    connection.send(response)

                    # sending file to client
                    with open(filename, 'rb') as f:
                        while True:
                            data = f.read(bufferSize)
                            if not data:
                                break
                            connection.send(data)
                    connection.send(b'END')

                else:
                    response = 3 # 011 for file does not exist
                    # convert to bytes
                    response = response << 5
                    response = response.to_bytes(1, 'big')
                    connection.send(response)

            #------------------------------------------------------------
            # CHANGE FILENAME
            #------------------------------------------------------------
            elif opcode == 2:
                filename, new_filename = unpack_request_change(tcp_request, filename_length)

                # checking to see if file exists

                if os.path.isfile(filename):
                    os.rename(filename, new_filename)
                    if debug: print("Filename changed from", filename, "to", new_filename)

                    # send response
                    if os.path.isfile(new_filename) and not os.path.isfile(filename):
                        response = 0 # 000 for successful transmission
                    else:
                        response = 5 # 101 for unsuccessful name change

                else:
                    response = 3

                # convert to bytes
                response = response << 5
                response = response.to_bytes(1, 'big')
                connection.send(response)



            #------------------------------------------------------------
            # SUMMARY
            #------------------------------------------------------------
            
            elif opcode == 3:
                filename = unpack_request_summary(tcp_request, filename_length)

                # checking to see if file exists
                if os.path.isfile(filename):
                    with open (filename, 'rt') as f:
                        data = f.read()
                        data = data.split()
                        data = [int(i) for i in data]
                
                        minimum = min(data)
                        maximum = max(data)
                        average = sum(data) / len(data)

                        if debug:
                            print("Minimum:", minimum)
                            print("Maximum:", maximum)
                            print("Average:", average)

                        response_filename = "summary.txt"

                        # writing to new file
                        with open(response_filename, 'w') as f:
                            f.write("Minimum: " + str(minimum) + "\n")
                            f.write("Maximum: " + str(maximum) + "\n")
                            f.write("Average: " + str(average) + "\n")

                        response = create_request(2, response_filename)
                        if debug: print(response)

                        connection.send(response)
                        # sending summary file to client
                        with open(response_filename, 'rb') as f:
                            while True:
                                data = f.read(bufferSize)
                                if not data:
                                    break
                                connection.send(data)
                        connection.send(b'END')

                        # deleting summary file
                        os.remove(response_filename)

                else:
                    response = 3
                    response = response << 5
                    response = response.to_bytes(1, 'big')
                    connection.send(response)

            #------------------------------------------------------------
            # HELP
            #------------------------------------------------------------
            elif opcode == 4:
                response = 6 # 110 for help
                response = response << 5
                help_message = "PUT\nGET\nCHANGE\nSUMMARY\nHELP"
                response += len(help_message)
                response = response.to_bytes(1, 'big')
            
                response = response + help_message.encode('utf-8')

                connection.send(response)

            #------------------------------------------------------------
            # CLOSE CONNECTION
            #------------------------------------------------------------
            elif opcode == 5:
                if debug: print("Closing TCP connection with " + str(address))
                response = 7 # 111 for closing connection
                response = response << 5
                response = response.to_bytes(1, 'big')
                connection.send(response)

                connection.close()
                break

#===============================================================================
# Main
#===============================================================================    
if __name__ == "__main__":

    debug = False

    if (len(sys.argv) == 3):
        if sys.argv[2] == "-d":
            debug = True
        else:
            print("Usage: python server.py <port> [-d]")
            sys.exit(1)
    elif (len(sys.argv) != 2):
        print("Usage: python server.py <port> [-d]")
        sys.exit(1)

    localIP = "127.0.0.1"
    localPort = int(sys.argv[1])
    bufferSize = 1024

    # creating threads for TCP and UDP connections so that they can run concurrently and clients can connect to either
    tcp_thread = threading.Thread(target=tcp_connection, args=(localIP, localPort, bufferSize)).start()
    udp_thrread = threading.Thread(target=udp_connection, args=(localIP, localPort, bufferSize)).start()



