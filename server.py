# Z0133496 Networks Coursework server.py

# Import modules required.
import datetime
import os
import socket
import pickle
import sys
import threading


# Add Underscore
def add_underscore(message):
    return message.replace(" ", "_")


# Delete Underscore
def del_underscore(message):
    return message.replace("_", " ")


# SEND_MSG (Sends data message to the target address.)
def send_msg(data, target):
    msg = pickle.dumps(data)
    target.send(msg)
    return data


# RECEIVE_MSG (Receives the message from the connection.)
def receive_msg(client):
    data = client.recv(4096)
    return pickle.loads(data)


# Appends a log to the log file, server.log
def write_log(req_type, status, ip_address, port):
    file = open("server.log", "a")
    # writes: IP address and port | Date and time | Request Type | Success or failure.
    file.write('| ' + ip_address + ':' + str(port) + ' | ' + datetime.datetime.now().strftime(
        "%a %d %b %H:%M:%S %Y") + ' | ' + req_type + ' | ' + status + ' |\n')
    file.close()


# GET_BOARDS (Returns a list of the message boards within the board folder and replaces underscores with spaces.)
def get_boards():
    try:
        boards = os.listdir("board")
        boards.sort(key=str.lower)
        for i in range(len(boards)):
            boards[i] = del_underscore(boards[i])
        if boards:
            return ['200 (OK)', boards]
        else:
            return ['404 (NOT FOUND)', []]

    # Will return an Error if unable to list boards.
    except OSError:
        return ['400 (Request GET_BOARDS Failed - Unable To List Boards)', []]


# GET_MESSAGES (Returns the 100 most recent messages from the chosen message board.)
def get_messages(board_title):
    try:
        files = os.listdir("board/{0}".format(board_title))
        files.sort(key=str.lower)
        files.reverse()

        # Max number of messages sent is 100 or the number of messages in the board.
        if len(files) < 100:
            no_msgs = len(files)
        else:
            no_msgs = 100

        # Appends the messages to the messages array to be sent to the client. Also gets replaces the underscores.
        messages = []
        for current_msg in range(no_msgs):
            current_file = open("board/{0}/{1}".format(board_title, files[current_msg]), "r")
            messages.append(del_underscore(files[current_msg]) + ' : ' + del_underscore(current_file.read()))
            current_file.close()
        return ['200 (OK)', messages]

    # Will return an Error if message board not found.
    except OSError:
        return ['404 (Request GET_MESSAGES Failed - Board Not Found)']


# POST_MESSAGE (Adds a new message to the message board.)
def post_message(board_title, post_title, message_content):
    try:
        file = open(
            "board/{0}/{1}-{2}".format(board_title, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), post_title),
            "w+")
        file.write(message_content)
        file.close()
        return ['201 (Created)']
    except OSError:
        return ['404 (Request POST_MESSAGE Failed - Unable To Post New Message)']


# CONNECTION (Connection thread, The main code loop that is run when a client connects.)
def connection(client, client_address):
    try:
        print('\nConnection From', client_address)

        # Wait for data from client.
        while True:
            try:
                # Data received from client is stored in variable 'data', empty Response variable.
                data, response = receive_msg(client), []
                if data:
                    # If GET_BOARDS
                    if data[0] == 'GET_BOARDS':
                        response = send_msg(get_boards(), client)
                    # If GET_MESSAGES
                    elif data[0] == 'GET_MESSAGES':
                        response = send_msg(get_messages(add_underscore(data[1])), client)
                    # If POST_MESSAGE
                    elif data[0] == 'POST':
                        response = send_msg(post_message(add_underscore(data[1]), add_underscore(data[2]), data[3]),
                                            client)
                    # Writes Logs
                    write_log(data[0], response[0], client_address[0], client_address[1])
            except EOFError:
                # No Data supplied hence will begin connection close.
                return

    finally:
        # Closes the connection to the client terminating the thread.
        client.close()
        print('\nConnection Closed With: ', client_address)


# CONNECTION_WAIT (Waiting for connection, will spawn a new thread (CONNECTION) if a client connects.)
def connection_wait(client_connection):
    print('\nWaiting For A Connection')
    while True:
        client, client_address = client_connection.accept()
        t = threading.Thread(target=connection, args=(client, client_address))
        t.start()


# Main Program

try:
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Server Address (IP Address, PORT)
    server_address = (sys.argv[1], int(sys.argv[2]))

    # Binds the socket to the port
    print('Starting Up On {} Port {}'.format(*server_address))
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(5)

    # Check If the board folder is empty, If it is it will raise an error.
    if len(get_boards()[1]) == 0:
        raise ValueError('HTTP STATUS CODE 500 (No Message Boards Defined).')

    # Run Connection Wait Function. Which will wait for client connections.
    connection_wait(sock)

# Error if address is already in use, the port is unavailable or busy.
except OSError as e:
    print('\nError: HTTP STATUS CODE 500 (Address Already In Use - Unavailable/Busy Port)')

# Outputs any Error returned in this case if no message boards are defined.
except ValueError as error:
    print('\nError: {0}'.format(error))
