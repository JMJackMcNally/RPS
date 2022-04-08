#!/usr/bin/python
#*************************************************************************
#*
#*         Author: Justin Hudoka, Jack McNally
#*          Major: Computer Science
#*  Creation Date: 11/28/21
#*       Due Date: 12/2/21
#*         Course: CSC328
#* Professor Name: Dr. Lisa Frye
#*       Filename: library.py
#*        Purpose: Custom library of shared functions for the RPS project
#*
#*       Language: Python 3
#*
#**************************************************************************

import sys
import socket

#************************************************************************
#*
#*   Name: tcpConnect()
#*   Description: creates a socket connection
#*   Parameters: None
#*   Return Value:
#*       tcp - the newly created socket
#************************************************************************  
def tcpConnect():
    try:
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except OSError as error:
        print('Socket Creation Error: ', format(error))
        exit(1)
    return tcp
    
#************************************************************************
#*
#*   Name: send(tcp, message)
#*   Description: Sends a message to a recipent while checking for errors
#*                and printing them.
#*   Parameters:
#           tcp - The recipient socket connection
#           message - A value to cast as a string and sent in ascii format.
#*   Return Value: None
#************************************************************************  
def send(tcp, message):
    try:
        string_message = str(message)
        tcp.sendall(string_message.encode('ascii'))
    except OSError as error:
        print('Sending Error: ', format(error))
    return

#************************************************************************
#*
#*   Name: recv(tcp)
#*   Description: Recieves a message from a recipent while checking for errors
#*                and printing them.
#*   Parameters:
#           tcp - The sender's socket connection
#*   Return Value:
#           string_message - The message being sent. Sent as [RECEIVING ERROR]
#                            if an error happens.
#************************************************************************  
def recv(tcp):
    try:
        message = tcp.recv(1024)
        string_message = str(message.decode('ascii'))
    except OSError as error:
        print('Recieving Error: ', format(error))
        string_message = '[RECEIVING ERROR]'
    return string_message