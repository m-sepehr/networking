import os
import sys
import socket

bufferSize = 1024

# TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# TCPServerSocket.connect((localIP, localPort))
# print("TCP server up and listening")

# # send message fom client to server
# message = "hello"
# bytesToSend = str.encode(message)
# TCPServerSocket.send(bytesToSend)

def main():
    first_start = True
    cli_text = "myftp> Press 1 for TCP, Press 2 for UDP: "
    conn_type = ""
    while True:
        command = input(cli_text).strip()
        if (first_start):
            cli_text = "myftp> "
            first_start = False
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
                pass
            else:
                # UDP selected
                # Create a datagram socket
                UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                # Bind to address and ip
                UDPServerSocket.connect((localIP, localPort))
                print("myftp> Session has been established using UDP.")
                conn_type = "UDP"
                pass
        elif command.startswith("get"):
            # Extract filename and call get_file
            pass
        elif command.startswith("put"):
            filename = command.split()[1]

            if conn_type == "UDP":
                # Send file over UDP
                UDPServerSocket.send(filename.encode())

                with open(filename, 'rb') as f:
                    while True:
                        data = f.read(bufferSize)
                        if not data:
                            break
                        UDPServerSocket.send(data)
                # Send end-of-transmission signal
                UDPServerSocket.send(b'END')
                pass
        elif command.startswith("change"):
            # Extract filenames and call change_file
            pass
        elif command == "help":
            # he
            pass
        elif command == "bye":
            print("myftp> Session is terminated.")
            break
        else:
            print("myftp> Unknown command.")

main()
