import os
import socket
import sys
import threading


def udp_connection(localIP, localPort, bufferSize):
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.bind((localIP, localPort))
    print("UDP server up and listening")

    while True:
            # Receiving filename from the client
            udp_request = UDPClientSocket.recvfrom(bufferSize)
            filename = udp_request[0].decode()
            print("Filename received:", filename)

            # Create file and save data
            with open(filename, 'wb') as f:
                print("File opened")
                while True:
                    data, _ = UDPClientSocket.recvfrom(bufferSize)
                    if data == b'END':
                        print("File transmission completed")
                        break
                    f.write(data)
        



def tcp_connection(localIP, localPort, bufferSize):
    TCPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCPClientSocket.bind((localIP, localPort))
    print("TCP server up and listening")
    while (True):
        TCPClientSocket.listen()
        conn, addr = TCPClientSocket.accept()

        with conn:
            while True:
                data = conn.recv(16)
                if not data:
                    break
                print(data.decode())
        
    
        
if __name__ == "__main__":

    if (len(sys.argv) != 2):
        print("Usage: python server.py <port>")
        sys.exit(1)

    localIP = "127.0.0.1"
    localPort = int(sys.argv[1])
    bufferSize = 1024

    tcp_thread = threading.Thread(target=tcp_connection, args=(localIP, localPort, bufferSize)).start()
    udp_thrread = threading.Thread(target=udp_connection, args=(localIP, localPort, bufferSize)).start()



