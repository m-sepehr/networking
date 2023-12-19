# Networking Client and Server Programs

These programs facilitate file operations such as file transfers, renaming, and summarizing over TCP and UDP protocols.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Server Program](#server-program)
  - [Starting the Server](#starting-the-server)
  - [Server Operations](#server-operations)
- [Client Program](#client-program)
  - [Starting the Client](#starting-the-client)
  - [Using the Client](#using-the-client)
  - [Supported Commands](#supported-commands)
  - [Example Usage](#example-usage)
  - [Closing the Client](#closing-the-client)
- [Notes](#notes)
- [Troubleshooting](#troubleshooting)
- [Security Warning](#security-warning)

## Prerequisites

Before running the client and server programs, ensure you have the following:
- Python 3.x installed on your system.

## Server Program

### Starting the Server

To start the server, navigate to the directory containing the server script and run the following command:
```
python server.py <port> [-d]
```
Replace `<port>` with the port number you want the server to listen on. The optional `-d` flag can be used to start the server in debug mode, which will print additional information to the console.

For example:
```
python server.py 12345 -d
```
### Server Operations

The server program will automatically handle incoming client requests for supported operations over TCP and UDP. There is no further interaction required.

## Client Program

### Starting the Client

To start the client, navigate to the directory containing the client script and run the following command:
Replit
```
python client.py [-d]
```
The optional `-d` flag can be used to start the client in debug mode, which will print additional information to the console.

### Using the Client

Once the client starts, it will prompt you to choose between TCP and UDP for the session. Input `1` for TCP or `2` for UDP.

#### Establishing a Session

After choosing the protocol, you will be prompted to enter the server's IP address and port number, separated by a space.

Example:

```
myftp> Provide IP address and Port number separated by a space: 127.0.0.1 12345
```
### Supported Commands

- `get <filename>`: Downloads a file from the server.
- `put <filename>`: Uploads a file to the server.
- `change <old_filename> <new_filename>`: Changes the name of a file on the server.
- `summary <filename>`: Requests a summary of the file contents from the server.
- `help`: Requests help information from the server.
- `bye`: Closes the session with the server.

### Example Usage

To get a file named `example.txt` from the server:
```
myftp> get example.txt
```
To upload a file named `example.txt` to the server:

```
myftp> put example.txt
```
To change a file's name from `old.txt` to `new.txt` on the server:

```
myftp> change old.txt new.txt
```

To get a summary of `data.txt` from the server:

```
myftp> summary data.txt
```

To request help information:

```
myftp> help
```

To close the session:

```
myftp> bye
```

### Closing the Client

To exit the client program, simply use the `bye` command to close the session or use `Ctrl+C` if you need to force an exit.

## Notes

- Ensure that the client and server are both running when attempting to establish a session.
- Files to be uploaded using the `put` command must be present in the client's current directory.
- Files downloaded using the `get` command will be saved to the client's current directory.
- The `change` command will only work if the specified file exists on the server.
- The `summary` command expects the file to contain numerical data for summarization.

## Troubleshooting

If you encounter any issues:
- Check that the server is running and listening on the correct port.
- Ensure there are no network connectivity issues between the client and server.
- Verify that the correct IP address and port number are used when starting the client session.
- Use the debug mode `-d` to obtain more detailed output for troubleshooting.

## Security Warning

These programs do not implement encryption or authentication and should not be used to transfer sensitive data over untrusted networks.
