# Z0133496 Networks Coursework client.py

# Import modules required.
import socket
import pickle
import sys


# OUTPUT_BOARD (Function will list the array inputted. In this case message boards or 100 most recent messages.)
def output_board(array):
    for x in range(len(array)):
        print("{0}. {1}".format(x + 1, array[x]))


# SEND_MSG (Sends data message to the target address.)
def send_msg(data, target):
    data = pickle.dumps(data)
    target.send(data)


# RECEIVE_MSG (Receives the message from the socket.)
def receive_msg():
    data = sock.recv(4096)
    return pickle.loads(data)


# GET_BOARDS (Requests a list of all the available message boards.)
def get_boards(target):
    msg = ['GET_BOARDS']
    send_msg(msg, target)
    return receive_msg()


# GET_MESSAGES (Requests the messages from the message board passed as a parameter option.)
def get_messages(option, target):
    msg = ['GET_MESSAGES', (boards[1])[int(option) - 1]]
    send_msg(msg, target)
    return receive_msg()


# POST_MESSAGE (Posts a new message to the message board. Asks for Board Number, Msg Title then Msg Content.)
def post_message(target):
    board_no = input('Board Number: ')
    title = input('Title: ')
    content = input('Content: ')
    # Packages message into array then sends it to the Server.
    # Except statements catch if an invalid number is entered for the board number.
    try:
        msg = ['POST', (boards[1])[int(board_no) - 1], title, content]
        send_msg(msg, target)
        return receive_msg()
    except IndexError:
        return ['400 (Invalid Board Number Try Again)']
    except ValueError:
        return ['400 (Invalid Board Number Try Again)']


# DIRECT_INPUT (Once connected, The function directs user input to GET_BOARDS, GET_MESSAGES, POST_MESSAGE or QUITS.)
def direct_input(msg_boards):
    while True:
        try:
            # Waits for user input
            option = input('\nEnter Option [Number, POST, QUIT]: ')

            # IF statement checks the Input is a GET, POST or QUIT.

            # Prints the 100 most recent messages from the chosen message board.
            # Will raise an error if the server does not return with a 200 OK.
            if option.isdigit():
                sub_board = get_messages(option, sock)
                if sub_board[0] == '200 (OK)':
                    print('\nHTTP STATUS CODE: {0}'.format(sub_board[0]))
                    print('100 most recent msgs from board: {0} '.format(msg_boards[int(option) - 1]))
                    output_board(sub_board[1])
                else:
                    raise ValueError('HTTP STATUS CODE {0}'.format(sub_board[0]))

            # Posts the users message to the chosen message board.
            # Will raise an error if the server does not return with a 200 OK.
            elif option.upper() == 'POST':
                response = post_message(sock)
                if response[0] == '201 (Created)':
                    print('\nHTTP STATUS CODE: {0}'.format(response[0]))
                else:
                    raise ValueError('HTTP STATUS CODE {0}'.format(response[0]))

            # Will close the socket connection if the user types in QUIT.
            elif option.upper() == 'QUIT':
                print('\nAttempting Server Disconnect.')
                return

            # Any other input is invalid and the user will be notified.
            else:
                print('\nError: Invalid Option Try Again.')

        # Outputs any Error returned by the server. (Any request that does not send a 200 OK)
        except ValueError as err:
            print('\nError: {0}'.format(err))

        # If socket times out (10 Secs) the client will close the connection.
        except socket.timeout:
            print('\nError: HTTP STATUS CODE 504, Server Timeout (10 secs)')
            return


# Main Program

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Server Address (IP Address, PORT)
server_address = (sys.argv[1], int(sys.argv[2]))

try:
    # Connect the socket to the port where the server is listening. Also sets client timeout to 10 seconds.
    print('\nAttempting to connect to {} on port {}'.format(*server_address))
    sock.connect(server_address)
    sock.settimeout(10)
    print('Connected to {} on port {}'.format(*server_address))

    # Calls the GET_BOARDS function. To find out which boards exist.
    boards = get_boards(sock)

    # Prints the boards returned. Raises an error if the server does not return a 200 OK.
    if boards[0] == '200 (OK)':
        print('\nHTTP STATUS CODE: {0}\nAvailable Boards: '.format(boards[0]))
        output_board(boards[1])
    else:
        raise ValueError('HTTP STATUS CODE {0}'.format(boards[0]))

    # Calls the DIRECT_INPUT function which is the main connection loop.
    direct_input(boards[1])

# Error if server is not running/unavailable.
except ConnectionRefusedError:
    print('\nError: HTTP STATUS CODE 500, Server is not running/unavailable.')

# Outputs any Error returned by the server. (Any request that does not send a 200 OK)
except ValueError as error:
    print('\nError: {0}'.format(error))

# If socket times out (10 Secs) the client will close the connection.
except socket.timeout:
    print('\nError: HTTP STATUS CODE 504, Server Timeout (10 secs)')

# Finally notifies the user the socket is closing and closes the socket.
finally:
    print('\nClosing socket\n')
    sock.close()
