import os
import socket
import sys
import threading
import struct

def unpack_request(request):
    opcode_and_length = request[0]
    opcode = opcode_and_length >> 5
    filename_length = opcode_and_length & 0b00011111
    filename = request[1:filename_length+1].decode()

    if opcode == 0: #000 for PUT
        file_size = struct.unpack('I', request[filename_length+1:filename_length+5])[0]
        return opcode, filename, file_size
    if opcode == 1: #001 for GET
        return opcode, filename, None
    

def unpack_request_get(request):
    opcode_and_length = request[0]
    opcode = opcode_and_length >> 5
    filename_length = opcode_and_length & 0b00011111
    filename = request[1:filename_length+1].decode()
    return opcode, filename

def udp_connection(localIP, localPort, bufferSize):
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.bind((localIP, localPort))
    print("UDP server up and listening")

    while True:
            # Receiving filename from the client
            udp_request = UDPClientSocket.recvfrom(bufferSize)
            print(udp_request)
            opcode, filename, file_size = unpack_request(udp_request[0]) 

            if opcode == 0: #000 for PUT
                with open(filename, 'wb') as f:
                    while True:
                        data, addr = UDPClientSocket.recvfrom(bufferSize)
                        if data == b'END':
                            print("File transmission completed")
                            break
                        f.write(data)

            elif opcode == 1: #001 for GET
                with open(filename, 'rb') as f:
                    while True:
                        data = f.read(bufferSize)
                        if not data:
                            break
                        UDPClientSocket.sendto(data, udp_request[1])
                UDPClientSocket.sendto(b'END', udp_request[1])
        



def tcp_connection(localIP, localPort, bufferSize):
    TCPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCPClientSocket.bind((localIP, localPort))
    print("TCP server up and listening")
    while (True):
        TCPClientSocket.listen()
        conn, addr = TCPClientSocket.accept()
        filename = conn.recv(bufferSize).decode()
        print("Filename received:", filename)
        
        with conn:
            with open(filename, 'wb') as f:
                while True:
                    data = conn.recv(bufferSize)
                    if data == b'END':
                        print("File transmission completed")
                        break
                    f.write(data)
        conn.close()

        
if __name__ == "__main__":

    if (len(sys.argv) != 2):
        print("Usage: python server.py <port>")
        sys.exit(1)

    localIP = "127.0.0.1"
    localPort = int(sys.argv[1])
    bufferSize = 1024

    tcp_thread = threading.Thread(target=tcp_connection, args=(localIP, localPort, bufferSize)).start()
    udp_thrread = threading.Thread(target=udp_connection, args=(localIP, localPort, bufferSize)).start()



