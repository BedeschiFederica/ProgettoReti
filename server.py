# -*- coding: utf-8 -*-

"""
Federica Bedeschi
Matricola: 0000970417
Email: federica.bedeschi4@studio.unibo.it

------------------------------------------------

UDP client-server architecture for file transfer
------------------------------------------------
                   Server

"""


from socket import AF_INET, socket, SOCK_DGRAM
import os


# It waits an answer from the client
# Returns the message received
def receive(client_address):
    server_socket.settimeout(1)
    while True:
        try:
            data, addr = server_socket.recvfrom(BUFSIZ)
        except:
            server_socket.settimeout(None)
            raise Exception
        if addr == client_address:
            server_socket.settimeout(None)
            return data.decode("utf8")

# It waits for the requests
def waiting_requests():
    while True:
        # waiting a request
        print("waiting for a request...")
        try:
            data, client_address = server_socket.recvfrom(BUFSIZ)
            
            # decoding message
            data = data.decode("utf8")
            
            # handling request
            message_to_send = "0"
            if data[0] == "1":
                # listing files
                message_to_send += list_files()
            elif data[0] == "2":
                # getting the file content
                message_to_send += get_file(data[1:], client_address)
            elif data[0] == "3":                
                # putting the file
                message_to_send += put_file(data[1:], client_address)
            else:
                message_to_send = "1" # invalid request
        except:
            message_to_send = "2" # error in receiving the request
            
        # sending answer
        server_socket.sendto(message_to_send.encode(), client_address)

# It lists the files
def list_files():
    return str(os.listdir(DIR))

# It gets the requested file and sends it
def get_file(file_name, client_address):
    # opening the file
    try:
        fin = open(DIR + file_name, "r")
    except:
        return "1" # error
    
    # getting and sending the content of the file
    try:
        message = ""
        for line in fin:
            # sending more packets if necessary
            if len(message + line) + 2 > BUFSIZ:
                server_socket.sendto(("02" + message).encode(), client_address)
                message = ""
                receive(client_address)
            message += line
    except:
        return "1" # error
    finally:
        fin.close()
    return "0" + message # EOF reached successfully

# It puts locally the file received
def put_file(file_name, client_address):   
    # waiting for file content
    server_socket.sendto(("0").encode(), client_address)
    data = receive(client_address)
    
    # opening a new file
    try:
        fout = open(DIR + file_name, "w")
    except:
        return "1"
    
    # putting the received content in the new file
    try:
        fout.write(data[1:])
        # handling more packets
        if data[0] == "2":
            while True:
                server_socket.sendto(("0").encode(), client_address)
                data = receive(client_address)
                fout.write(data[1:])
                if data[0] == "0":
                    break
    except:
        return "1"
    finally:
        fout.close()
    return "0"


# useful constants
HOST = ''
PORT = 53000
BUFSIZ = 1024
ADDR = (HOST, PORT)
DIR = "." + os.sep + "Files" + os.sep

# creating socket
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(ADDR)

if __name__ == "__main__":
    waiting_requests()