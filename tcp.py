"""
- NOTE: REPLACE 'N' Below with your section, year, and lab number
- CS2911 - 0NN
- Fall 202N
- Lab N
- Names:
  -
  -

A simple TCP server/client pair.

The application protocol is a simple format: For each file uploaded, the client first sends four
(big-endian) bytes indicating the number of lines as an unsigned binary number.

The client then sends each of the lines, terminated only by '\\n' (an ASCII LF byte).

The server responds with 'A' when it accepts the file.

Then the client can send the next file.


Introduction: (Describe the lab in your own words)




Summary: (Summarize your experience with the lab, what you learned, what you liked, what you disliked, and any suggestions you have for improvement)




"""

# import the 'socket' module -- not using 'from socket import *' in order to selectively use items with 'socket.' prefix
import socket
import struct
import time
import sys

global filename

# Port number definitions
# (May have to be adjusted if they collide with ports in use by other programs/services.)
TCP_PORT = 12100

# Address to listen on when acting as server.
# The address '' means accept any connection for our 'receive' port from any network interface
# on this system (including 'localhost' loopback connection).
LISTEN_ON_INTERFACE = ''

# Address of the 'other' ('server') host that should be connected to for 'send' operations.
# When connecting on one system, use 'localhost'
# When 'sending' to another system, use its IP address (or DNS name if it has one)
# OTHER_HOST = '155.92.x.x'
OTHER_HOST = 'localhost'


def main():
    """
    Allows user to either send or receive bytes
    """
    # Get chosen operation from the user.
    action = input('Select "(1-TS) tcpsend", or "(2-TR) tcpreceive":')
    # Execute the chosen operation.
    if action in ['1', 'TS', 'ts', 'tcpsend']:
        tcp_send(OTHER_HOST, TCP_PORT)
    elif action in ['2', 'TR', 'tr', 'tcpreceive']:
        tcp_receive(TCP_PORT)
    else:
        print('Unknown action: "{0}"'.format(action))


def tcp_send(server_host, server_port):
    """
    - Send multiple messages over a TCP connection to a designated host/port
    - Receive a one-character response from the 'server'
    - Print the received response
    - Close the socket

    :param str server_host: name of the server host machine
    :param int server_port: port number on server to send to
    """
    print('tcp_send: dst_host="{0}", dst_port={1}'.format(server_host, server_port))
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((server_host, server_port))

    num_lines = int(input('Enter the number of lines you want to send (0 to exit):'))

    while num_lines != 0:
        print('Enter all the lines of your message:')
        tcp_socket.sendall(b'\x00\x00')
        time.sleep(1)  # Just to mess with your servers. :-)
        tcp_socket.sendall(b'\x00' + bytes((num_lines,)))

        # Enter the lines of the message. Each line will be sent as it is entered.
        for line_num in range(0, num_lines):
            line = input('')
            tcp_socket.sendall(line.encode() + b'\n')

        print('Done sending. Awaiting reply.')
        response = tcp_socket.recv(1)
        if response == b'A':  # Note: == in Python is like .equals in Java
            print('File accepted.')
        else:
            print('Unexpected response:', response)

        num_lines = int(input('Enter the number of lines you want to send (0 to exit):'))

    tcp_socket.sendall(b'\x00\x00')
    time.sleep(1)  # Just to mess with your servers. :-)  Your code should work with this line here.
    tcp_socket.sendall(b'\x00\x00')
    response = tcp_socket.recv(1)
    if response == b'Q':  # Reminder: == in Python is like .equals in Java
        print('Server closing connection, as expected.')
    else:
        print('Unexpected response:', response)

    tcp_socket.close()


def tcp_receive(listen_port):
    """
    - Listen for a TCP connection on a designated "listening" port
    - Accept the connection, creating a connection socket
    - Print the address and port of the sender
    - Repeat until a zero-length message is received:
      - Receive a message, saving it to a text-file (1.txt for first file, 2.txt for second file, etc.)
      - Send a single-character response 'A' to indicate that the upload was accepted.
    - Send a 'Q' to indicate a zero-length message was received.
    - Close data connection.

    :param int listen_port: Port number on the server to listen on
    """

    print('tcp_receive (server): listen_port={0}'.format(listen_port))
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind((LISTEN_ON_INTERFACE, listen_port))
    listen_socket.listen(1)
    (data_socket, sender_address) = listen_socket.accept()
    print(sender_address)
    num_lines = number_of_lines(data_socket)

    # while num_lines != 0:
    if num_lines == 0:
        data_socket.sendall(b'Q')
    else:
        message_reader(data_socket, num_lines)
        data_socket.sendall(b'A')
        num_lines = number_of_lines(data_socket)


# Add more methods here (Delete this line)

def number_of_lines(data_socket):
    """
    This method reads the first 4 bytes of the message and converts them into an int, that is the number of times
    that the code \x0a can be read in the message before it quits
    :param data_socket:
    :return: returns the number of times \x0a can be read
    author: Tyler Cernik
    """
    byte_counter = b''
    for x in range(0, 4):
        byte_counter += next_byte(data_socket)
    return int.from_bytes(byte_counter, 'big')


def message_reader(data_socket, num_lines):
    """
    This method uses the number_of_lines() method to get the number of times to read \x0a in the file, and then
    reads the message from the client. It then creates a text file with the sent message in proper format
    :param data_socket: Data socket
    :param num_lines: number times the reader can read \x0a
    :return: writes the message to a file
    """

    global filename
    byte_message = b''

    while num_lines > 0:
        byte_holder = next_byte(data_socket)
        byte_message += byte_holder
        if byte_holder == b'\x0a':
            num_lines -= 1
    print(byte_message.decode())


"""
    f = open((str(filename) + '.txt'), 'w+')
    f.write(byte_message.decode('ASCII'))
    f.close()
    filename += 1
"""


def next_byte(data_socket):
    """
    Read the next byte from the socket data_socket.

    Read the next byte from the sender, received over the network.
    If the byte has not yet arrived, this method blocks (waits)
      until the byte arrives.
    If the sender is done sending and is waiting for your response, this method blocks indefinitely.

    :param data_socket: The socket to read from. The data_socket argument should be an open tcp
                        data connection (either a client socket or a server data socket), not a tcp
                        server's listening socket.
    :return: the next byte, as a bytes object with a single byte in it
    """
    return data_socket.recv(1)


# Invoke the main method to run the program.
main()
