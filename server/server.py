import os
import socket
import sys
import threading
import struct

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


#------------------------------------------------------------
# UDP
#------------------------------------------------------------
def udp_connection(localIP, localPort, bufferSize):
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.bind((localIP, localPort))
    if debug: print("UDP server up and listening")

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
                with open(filename, 'rb') as f:
                    while True:
                        data = f.read(bufferSize)
                        if not data:
                            break
                        UDPClientSocket.sendto(data, udp_request[1])
                UDPClientSocket.sendto(b'END', udp_request[1])

            #------------------------------------------------------------
            # CHANGE FILENAME
            #------------------------------------------------------------
            elif opcode == 2: #011 for CHANGE
                filename, new_filename = unpack_request_change(udp_request[0], filename_length)
                os.rename(filename, new_filename)
                if debug: print("Filename changed from", filename, "to", new_filename)

            #------------------------------------------------------------
            # SUMMARY
            #------------------------------------------------------------
            elif opcode == 3: #011 for SUMMARY
                filename = unpack_request_summary(udp_request[0], filename_length)
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

                    # convert to bytes
                    minimum_bytes = minimum.to_bytes(4, 'big')
                    maximum_bytes = maximum.to_bytes(4, 'big')
                    average_bytes = str(average).encode()

                    # send minimum, maximum, and average to client
                    UDPClientSocket.sendto(minimum_bytes, udp_request[1])
                    UDPClientSocket.sendto(maximum_bytes, udp_request[1])
                    UDPClientSocket.sendto(average_bytes, udp_request[1])

        
#------------------------------------------------------------
# TCP
#------------------------------------------------------------
def tcp_connection(localIP, localPort, bufferSize):
    TCPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCPClientSocket.bind((localIP, localPort))
    if debug: print("TCP server up and listening")
    while (True):
        TCPClientSocket.listen()
        conn, addr = TCPClientSocket.accept()
        filename = conn.recv(bufferSize).decode()
        if debug: print("Filename received:", filename)
        
        with conn:
            with open(filename, 'wb') as f:
                while True:
                    data = conn.recv(bufferSize)
                    if data == b'END':
                        if debug: print("File transmission completed")
                        break
                    f.write(data)
        conn.close()

        
if __name__ == "__main__":

    if (len(sys.argv) != 3):
        print("Usage: python server.py <port> <debug>")
        sys.exit(1)

    localIP = "127.0.0.1"
    localPort = int(sys.argv[1])
    debug = bool(int(sys.argv[2]))
    bufferSize = 1024

    tcp_thread = threading.Thread(target=tcp_connection, args=(localIP, localPort, bufferSize)).start()
    udp_thrread = threading.Thread(target=udp_connection, args=(localIP, localPort, bufferSize)).start()



