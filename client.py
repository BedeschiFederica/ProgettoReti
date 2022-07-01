# -*- coding: utf-8 -*-

"""
Federica Bedeschi
Matricola: 0000970417
Email: federica.bedeschi4@studio.unibo.it

------------------------------------------------

UDP client-server architecture for file transfer
------------------------------------------------
                   Client

"""


from socket import AF_INET, socket, SOCK_DGRAM
import tkinter as tkt
import os


# It creates a new empty window
def new_window():
    w = tkt.Toplevel()
    w.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    return w

# It sends a message to the server
def send(message):
    client_socket.sendto(message.encode(), SERVER_ADDRESS)
    
# It receives a message from the server and handles it
def receive():
    try:
        data, server_address = client_socket.recvfrom(BUFSIZ)
        data = data.decode("utf8")
    except:
        data = "Error in receiving the response from the server"
    if data[0] == "1":
       data = "Error: an invalid request was sent"
    elif data[0] == "2":
        data = "Error: the server didn't receive the request"
    if data[0] != "0":
        tkt.messagebox.showerror("Error", data)
        raise Exception(data)
    return data[1:]

# It handles the file listing request
def list_handle():       
    # sending the request
    send("1")
    
    # getting the answer
    data = receive()
    
    # writing the file listing in a new window
    w = new_window()
    w.title("File_listing")
    listing_label = tkt.Label(w, text="File listing:")
    box_scrollbar = tkt.Scrollbar(w, orient='vertical')
    listing_box = tkt.Text(w, yscrollcommand=box_scrollbar.set)
    listing_box.insert(tkt.END, "\n".join(data[1:len(data)-1].split(", ")))
    listing_box.config(state=tkt.DISABLED)
    box_scrollbar.config(command=listing_box.yview)
    
    listing_label.pack()
    box_scrollbar.pack(side=tkt.RIGHT, fill='y')
    listing_box.pack(fill='both', padx=WINDOW_WIDTH/20)

# It handles the get request
def get_handle():
    # creating a new window for the download
    w = new_window()
    w.title("File_download")
    file_name_label = tkt.Label(w, text="File name: ")
    file_name_entry = tkt.Entry(w)
    response_label = tkt.Label(w)
    download_button = tkt.Button(w, text="Download",
                                 command= lambda:
                                     get(file_name_entry, response_label))
    file_name_label.pack()
    file_name_entry.pack()
    download_button.pack()
    response_label.pack()

# It makes the get request
def get(file_name_entry, response_label):
    # sending the request
    send("2" + file_name_entry.get())
    
    # getting the answer
    data = receive()
    
    # signaling an error
    if data[0] == "1":
        response_label.config(text="Could not read file '"
                              + file_name_entry.get() + "'")
        return
    
    # opening a new file
    try:
        fout = open(file_name_entry.get(), "w")
    except:
         response_label.config(text="Error in downloading the file")
         
    # putting the received content in the new file
    try:
        fout.write(data[1:])
        if data[0] == "2":
            while True:
                send("")
                data = receive()
                if data[0] == "1":
                    raise Exception
                fout.write(data[1:])
                if data[0] == "0":
                    break
    except:
        response_label.config(text="Error in downloading the file")
        return
    finally:
        fout.close()
    response_label.config(text="Download done successfully")
    
# It handles the put request
def put_handle():
    # creating a new window for the upload
    w = new_window()
    w.title("File_upload")
    file_path_label = tkt.Label(w, text="File path: ")
    file_path_entry = tkt.Entry(w)
    response_label = tkt.Label(w)
    upload_button = tkt.Button(w, text="Upload",
                                 command= lambda:
                                     put(file_path_entry, response_label))
    file_path_label.pack()
    file_path_entry.pack()
    upload_button.pack()
    response_label.pack()
     
# It makes the put request
def put(file_path_entry, response_label):  
    # opening the file
    try:
        fin = open(file_path_entry.get(), "r")
    except:
        error_message = "Could not read file '" + file_path_entry.get() + "'"
        response_label.config(text=error_message)
        return
    
    # sending the request with the file name
    path_split = file_path_entry.get().split(os.sep)
    send("3" + path_split[len(path_split) - 1])
    receive()
    
    # getting and sending the content of the file
    try:    
        message = ""
        for line in fin:
            # sending more packets if necessary
            if len(message + line) + 1 > BUFSIZ:
                send("2" + message)
                message = ""
                data = receive()
            message += line
    except IOError:
        error_message = "Could not read file '" + file_path_entry.get() + "'"
        response_label.config(text=error_message)
        return
    except:
        error_message = "Error while uploading the file to the server"
        response_label.config(text=error_message)
        return
    send("0" + message) # EOF reached successfully

    # getting and writing the response
    data = receive()
    if data[0] == "0":
        data = "Upload done successfully"
    elif data[0] == "1":
        data = "Error in uploading the file"
    else:
        data = "Protocol error"
    response_label.config(text=data)

# It closes the client (both GUI and socket)
def on_closing():
    window.destroy()
    client_socket.close()


# getting server infos
HOST = input("Insert server host: ")
PORT = input("Insert server port: ")
if not HOST:
    HOST = "localhost"
if not PORT:
    PORT = 53000
else:
    PORT = int(PORT)

# useful constants
BUFSIZ = 1024
SERVER_ADDRESS = (HOST, PORT)

# creating socket
client_socket = socket(AF_INET, SOCK_DGRAM)

# creating Tkinter window
window = tkt.Tk()
window.title("File_Transfer")
WINDOW_WIDTH = int(window.winfo_screenwidth() / 2)
WINDOW_HEIGHT = int(window.winfo_screenheight() / 2)
window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))

# adding buttons
BUTTON_WIDTH = 30
BUTTON_HEIGHT = 4
list_button = tkt.Button(window, text="List files", command=list_handle,
                         width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
list_button.pack(pady = BUTTON_HEIGHT)
get_button = tkt.Button(window, text="Download file", command=get_handle,
                        width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
get_button.pack(pady = BUTTON_HEIGHT)
put_button = tkt.Button(window, text="Upload file", command=put_handle,
                        width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
put_button.pack(pady = BUTTON_HEIGHT)

# adding protocol on closing
window.protocol("WM_DELETE_WINDOW", on_closing)

# executing window
tkt.mainloop()