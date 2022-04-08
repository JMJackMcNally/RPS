#*************************************************************************
#*
#*         Author: Justin Hudoka, Sayan Gonzalez, Jack McNally
#*          Major: Computer Science
#*  Creation Date: 11/26/21
#*       Due Date: 12/2/21
#*         Course: CSC328
#* Professor Name: Dr. Lisa Frye
#*       Filename: client.py
#*        Purpose: Client for the RPS project
#*
#*       Language: Python 3
#*
#**************************************************************************
import sys
import socket
from time import sleep
import library #rock paper scissors library

#prints command-line usage message on incorrect input

##############################################################
#
#   Name: PrintUsageMessage()
#   Description: Prints a usage statement when the command line
#                arguments are incorrect.
#   Parameters: None
#   Return Value: None
#
##############################################################
def PrintUsageMessage():
    print("Format:  python client.py HOSTNAME PORT (optional)")
    print("Example: python client.py acad.kutztown.edu 22")

##############################################################
#
#   Name: CLA_Handling()
#   Description: Takes the command line arguments and assigns
#                them to variables (hostip and port). If
#                the arguments are invalid, PrintUsageMessage()
#                will be called to print a currect usage case.
#   Parameters: None
#   Return Value: hostip - the ip of the host
#                 port - the port to be used
#
##############################################################
def CLA_Handling():
    if((len(sys.argv) == 2) or (len(sys.argv) == 3)):
        Arguments = sys.argv[1:]
        try:
            hostip = socket.gethostbyname(Arguments[0])
        except socket.gaierror: #failed connection
            print("Invalid hostname!")
            exit() #exit program
        try:
            if len(sys.argv) == 3:
                port = int(Arguments[1])
            else: #if no port provided
                port = 50009
        except:
            print("Port must be an integer value!")
    else: #invalid amount of arguments
        print("Invalid number of arguments!")
        PrintUsageMessage()
        exit() #EXIT PROGRAM
    return hostip, port

##############################################################
#
#   Name: ServerConnect(hostip,port)
#   Description: Attempts to connect to the server. Handles
#                nickname setup and everything until the
#                gameplay begins.
#   Parameters: hostip - the ip of the host
#               port - the port to connect to
#   Return Value: s - the socket connection
#                 roundCount - the number of rounds to be played
##############################################################
def ServerConnect(hostip, port):
    connected = False #boolean: if the player is connected
    ready = False #boolean: if the player is ready for gameplay
    unique = False #boolean: if the player's nickname is unique
    connectionAttempts = 1 #current amount of connection attempts
    receivedBOTHPLAYERS = False #if client has received "NICK" from server
    s = library.tcpConnect() #creating socket

    print("Attempting connection to server...")
    while not connected and connectionAttempts < 4:
        try:
            s.connect((hostip, port))
            message = "READY"
            library.send(s, message)
            connected = True
        except Exception as e:
            print("Error connecting to server:", e)
            print("Reattempting connection to server...")
            connectionAttempts += 1
            sleep(5) #wait 5 seconds between attempts
    
    #INFINITE LOOP PREVENTION
    if not connected:
        print("Failed connection attempts exceeded 3. Shutting down.")
        exit()
    
    print("Connection successful!")
    
    print("Waiting for other player to connect...")
    while receivedBOTHPLAYERS == False:
        message = library.recv(s)
        if message.find("BOTHPLAYERS") != -1:
            print("Both players are connected!")
            receivedBOTHPLAYERS = True
    
    
    while connected == True and unique == False: #loop until valid nickname is used
        try:
            nick = input("Please select a unique nickname: ")
            nickSignal = "NICK:"
            nickname = str(nickSignal)+str(nick)
            library.send(s, nickname)
            print("Waiting for server...")
            message = library.recv(s)
            
            if message.find("RETRY") != -1:
                unique = False
                print("That nickname is already being used!")
            elif message.find("READY") != -1:
                unique = True
                print("Nickname validated!")
                break
        except Exception as e:
            print("Error sending nickname to server:", e)

    while ready == False:
        if message.find("GO") != -1: #if "GO" already received
            print("Ready to play!")
            ready = True
        else:
            message = library.recv(s)
            if message.find("GO") != -1:
                print("Ready to play!")
                ready = True
        message_filter = filter(str.isdigit, message) #isolate the round count received with "GO"
        roundCount = "".join(message_filter)
        
    return s, roundCount #returning socket and amount of rounds
    
##############################################################
#
#   Name: GameplayLoop
#   Description: Loop to handle the RPS gameplay. Prints
#                score and ends when the server sends it.
#   Parameters: s - the socket connection to the server
#               roundCount - number of rounds to be played
#   Return Value: None
#
##############################################################
def GameplayLoop(s,roundCount):
    roundsComplete = 1 #number of currently completed rounds
    roundCount = int(roundCount)
    Continue = True #sentinel value bool that's set to false when "SCORE" is received
    while Continue == True:
        validChoice = False #default to false each time
        while validChoice == False:
            choices = input("Please make your selection: \nR - Rock \nP - Paper \nS - Scissors\n")
            choices = choices.upper() #make string uppercase
            if choices != "R" and choices != "P" and choices != "S":
                print("Invalid Input! Please enter R, P, or S.")
            else:
                validChoice = True
        library.send(s, choices) #send to server
        print("Waiting for server...")
        if roundsComplete >= roundCount:
            #checking for score
            Response = library.recv(s) #check for "SCORE"
            #print(Response)
            if Response and Response.find("SCORE:") != -1:
                Continue = False
                break
        roundsComplete += 1
    
    #Printing final score
    Response = Response.replace("SCORE:","")
    
    if Response.find("STOP") != -1: #if the server already sent the stop message
        finalMessage = Response.replace("STOP","")
        print(finalMessage)
        print("Thank you for playing!")
    else:
        print(Response)
        finalMessage = library.recv(s)
        if finalMessage.find("STOP") != -1:
            print("Thank you for playing!")
    return
        
    
#main function
def main():
    hostip, port = CLA_Handling() #command line argument handling
    s,roundCount = ServerConnect(hostip, port) #connect to server and set up nickname
    GameplayLoop(s, roundCount) #play rock paper scissors
    s.close() #close the connection
    exit()

if __name__ == '__main__':
    main()