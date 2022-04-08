#*************************************************************************
#*
#*         Author: Justin Hudoka, Sayan Gonzalez, Jack McNally
#*          Major: Computer Science
#*  Creation Date: 11/26/21
#*       Due Date: 12/2/21
#*         Course: CSC328
#* Professor Name: Dr. Lisa Frye
#*       Filename: server.py
#*        Purpose: Server for the RPS project
#*
#*       Language: Python 3
#*
#**************************************************************************
import socket,threading
import os,sys
import library
from _thread import *
from time import sleep

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
    print("Format:  python server.py ROUND-COUNT PORT (optional)")
    print("Example: python client.py 5 50023")

##############################################################
#
#   Name: CLA_Handling()
#   Description: Takes the command line arguments and assigns
#                them to variables (Round count and port (OPTIONAL)). If
#                the arguments are invalid, PrintUsageMessage()
#                will be called to print a currect usage case.
#   Parameters: None
#   Return Value: round - the # of rounds
#                 port - the port number to be used
#
##############################################################
def CLA_Handling():
    if((len(sys.argv) == 2) or (len(sys.argv) == 3)):
        Arguments = sys.argv[1:]
        try:
            round = Arguments[0]
        except socket.gaierror: #failed connection
            print("Invalid Round Number!")
            exit() #exit program
        try:
            if len(sys.argv) == 3:
                port = int(Arguments[1])
            else: #if no port provided
                port = 50009
                #if port is taken, [Errno 98] will be shown upon socket creation
        except:
            print("Port must be an integer value!")
            PrintUsageMessage()
            exit()
    else: #invalid amount of arguments
        print("Invalid number of arguments!")
        PrintUsageMessage()
        exit() #EXIT PROGRAM
    return round, port

##############################################################
#
#   Name: lookForNick()
#   Description: Scans a message for the "NICK" signal and
#                returns a true boolean (nick) if found,
#                and returns the message without the NICK signal
#
#   Parameters: message - the full message
#               nick - boolean for whether or not a nick was received
#   Return Value: message - the full message
#               nick - boolean for whether or not a nick was received
#
##############################################################
def lookForNick(message,nick):
    if message.find("NICK") != -1:
        message = message.replace("NICK:","")
        nick = True
        return message,nick
    return message,nick
    
##############################################################
#
#   Name: getChoices(connection)
#   Description: Sets the values of a global list storing the RPS
#                choices of both players.
#
#
#   Parameters: connection - the client socket connection
#   Return Value: None, this function changes global values
#
##############################################################
def getChoices(connection):
    #if global choice list already exists
    if "gChoiceList" not in globals():
        global gChoiceList
        gChoiceList = ['','']
    
    userInput = library.recv(connection)
    print("gThreads:", gThreads)
    
    #Identify player and write to the correct index
    threadID = threading.get_ident()
    index = gThreads.index(threadID)
    if index == 0:
        gChoiceList[0] = userInput
        #print(gChoiceList[0])
    elif index == 1:
        gChoiceList[1] = userInput
        #print(gChoiceList[1])
    
    print("gChoiceList in getChoices():", gChoiceList)
    

#************************************************************************
#*
#*   Name: setup(message,nickFound,readyUp,Name,ready,unique,evaluated,name,startGame,connection,sentBOTHPLAYERS):
#*   Description: Validates nicknames and sets booleans that help the rest
#*                of the code run and control timing.
#*   Parameters:
#*       message - string: a received message or name
#*       nickFound - boolean: whether or not a nickname has been found
#*       readyUp - boolean: if both clients have sent "READY"
#*       Name - Thread identifier(?) (this variable is a black box, it's never initalized or assigned)
#*       ready - boolean: if nicknames are unique
#*       unique - boolean: if nicknames are unique
#*       evaluated - boolean: if nickname uniqueness has been evaluated at least once
#*       name - list: contains all player nicknames
#*       connection - client socket connection
#*       sentBOTHPLAYERS - boolean: if both players have been sent "READY", signalling their nicknames were
#*                                  verified as unique in a different run of this function
#*
#*   Return:
#*       message - string: a received message or name
#*       nickFound - boolean: whether or not a nickname has been found
#*       readyUp - boolean: if both clients have sent "READY"
#*       Name - Thread identifier(?) (this variable is a black box, it's never initalized or assigned)
#*       ready - boolean: if nicknames are unique
#*       unique - boolean: if nicknames are unique
#*       evaluated - if nickname uniqueness has been evaluated at least once
#*       name - list: contains all player nicknames
#*       startGame - boolean: if all required setup is done and the game loop can start
#*       connection - client socket connection
#*       sentBOTHPLAYERS - boolean: if both players have been sent "READY", signalling their nicknames were
#*                                  verified as unique in a different run of this function
#*
#************************************************************************
def setup(message,nickFound,readyUp,Name,ready,unique,evaluated,name,startGame,connection,sentBOTHPLAYERS):
    nameCheckResult = False #boolean for whether or not a name is unique or not
    
    #If and while, only run before both clients send "READY"
    if message == "READY" and players == 1:
        print("One player ready.")
        pass
    while readyUp == False:
        if message == "READY" and players == 2:
            print("Two players ready.") #this prints twice, once for each client
            readyUp = True
    
    #After both clients are ready, start nickname validation
    #nickFound being true ensures that this is a second run, meaning the message being evaluated
    #is a nickname, and not "READY"
    if readyUp == True:
        if nickFound == True and players == 1:
            print("Ready, one player connected")
        if nickFound == True and Name == 1:
            name.append(message) #append nickname to name list
            print("NAME APPENDED", name)
        if nickFound == True and players == 2:
            Name = 2
            print("Ready, both players connected.")
        
    #GlobalNameList is used because this server was setup without pipes, and Jack (me) is
    #fixing this server from Sayan's code, which uses threads but no pipes.
    #The two clients can't communicate since they're in different threads, so my solution
    #was to create a new GLOBAL list to hold all the nicknames so that the two clients are able to
    #compare nicknames with each other. This is declared within a thread AFTER both clients are connected,
    #that way I can be sure it's happening in thread 2, meaning both threads will have the global variable.
    
    if nickFound == True:
        if "GlobalNameList" not in globals(): #If GlobalNameList does not exist yet
            global GlobalNameList
            GlobalNameList = name
        GlobalNameList.append(message)
        print("Name: ",GlobalNameList)
        
        #this exists because the threads might get desynced otherwise, and waits aren't an option
        #since no threads are ending
        if len(GlobalNameList) != 2 or not GlobalNameList:
            print("Waiting up to 10 seconds for other user's response...")
            sleep(10)

        #Check two nicknames in list for uniqueness.
        if len(GlobalNameList) == 2:
            if GlobalNameList[0] == GlobalNameList[1]:
                nameCheckResult = False
            else:
                nameCheckResult = True
        
        if nameCheckResult == True and len(GlobalNameList) == 2:
            print("NICKNAMES VALIDATED UNIQUE!", GlobalNameList)
            startGame = True
            unique = True
            evaluated = True
        elif nameCheckResult == False and len(GlobalNameList) == 2:
            print("NICKNAMES ARE NOT UNIQUE! Clearing name list...", GlobalNameList)
            GlobalNameList = [] #added by jack
            print("NAME LIST CLEARED!", GlobalNameList) #added by jack
            unique = False
            evaluated = True
            startGame = False
        elif not GlobalNameList: #if globalNameList has already been cleared by the thread that's above
            print("NICKNAMES WERE NOT UNIQUE! Letting the thread that's behind know...")
            unique = False
            evaluated = True
            startGame = False
        
        #Very convenient place to setup these global variables since they have to be declared in a thread to work.
        #These variables have multiple other declaration statements just in case, but this is one place to do them all at once.
        #SETTING UP GLOBAL VALUES FOR GAME LOOP
        if "gThreads" not in globals():
            global gThreads
            gThreads = []
            threadID = threading.get_ident()
            if threadID not in gThreads:
                gThreads.append(threadID)
            print("gThreads:", gThreads)
        if "gChoiceList" not in globals():
            global gChoiceList
            gChoiceList = ['','']
            print("gChoiceList:", gChoiceList)
        if "playerOneCleared" not in globals():
            global playerOneCleared
            playerOneCleared = True
        if "playerTwoCleared" not in globals():
            global playerTwoCleared
            playerTwoCleared = True
                
    return message,nickFound,readyUp,Name,ready,unique,evaluated,name,startGame,connection,sentBOTHPLAYERS


##############################################################
#
#   Name: gameLoop()
#   Description: Use a global list storing the RPS choices of 
#                both players to determine the score of a round.
#
#
#   Parameters: None, this function uses global values
#   Return Value: None, this function changes global values
#
##############################################################
def gameLoop():
    score = ''
    '''
    #if "gChoiceList" not in globals():
    #    global gChoiceList
    #    gChoiceList = choiceList
    #choiceList = gChoiceList
    #print("choiceList in gameLoop:", choiceList)
    
    #code below is in case a timing error left one choice index empty,
    #could be choiceList the parameter or gChoiceList the global variable
    #a timing error would most likely result in an index being blank, so this replaces blank
    #indices with full ones
    if choiceList != gChoiceList:
        if '' in choiceList:
            if '' not in gChoiceList:
                choiceList = gChoiceList
            elif '' == choiceList[0] and '' != gChoiceList[0]:
                choiceList[0] = gChoiceList[0]
            elif '' == choiceList[1] and '' != gChoiceList[1]:
                choiceList[1] = gChoiceList[1]
        elif '' in gChoiceList:
            if '' not in choiceList:
                gChoiceList = choiceList
            elif '' == gChoiceList[0] and '' != choiceList[0]:
                gChoiceList[0] = choiceList[0]
            elif '' == gChoiceList[1] and '' != choiceList[1]:
                gChoiceList[1] = ChoiceList[1]
    '''       
    
    #The above section of code, which I shouldn't leave in, but am anyway, is a good demonstration
    #of the specific issues with timing these concurrent threads without pipes. This code was typed out
    #to help save indices that got reinitalized early, it relied on me passing a global variable as a regular argument,
    #and then using it as a backup in case the global variable indices got reinitialized mid-evaluation.
    #Thing is, that actually slowed my code down by the few milliseconds it takes to get the threads desynced,
    #so ultimately it was better to scrap it.
                
    playerOne = gChoiceList[0] #Player One's choice
    playerTwo = gChoiceList[1] #Player Two's choice
    print("gChoiceList in gameLoop:", gChoiceList)
    
    if playerOne != '' and playerTwo != '': #if player choices aren't empty
        if playerOne == 'R' and playerTwo == 'R':
            score = 0
            return score
        elif playerOne == 'R' and playerTwo == 'P':
            score = 2
            return score
        elif playerOne == 'R' and playerTwo == 'S':
            score = 1
            return score
        elif playerOne == 'P' and playerTwo == 'R':
            score = 1
            return score
        elif playerOne == 'P' and playerTwo == 'P':
            score = 0
            return score
        elif playerOne == 'P' and playerTwo == 'S':
            score = 2
            return score
        elif playerOne == 'S' and playerTwo == 'R':
            score = 2
            return score
        elif playerOne == 'S' and playerTwo == 'P':
            score = 1
            return score
        elif playerOne == 'S' and playerTwo == 'S':
            score = 0
            return score
    if score != '':
        return score
    else:
        print("Score is empty! One of the player choice values cleared early.")
        return score
    
#************************************************************************
#*
#*   Name: threaded_client
#*   Description: Calls setup(), getChoices(), and gameLoop().
#*                Handles the bulk of variables and controls the
#*                flow of the program through booleans
#*   Parameters:
#*       connection - the client socket
#*       ready - global variable for player count(?)
#*   Return Value: None
#*
#************************************************************************    
def threaded_client(connection,ready):
    name = [] #A list to hold nicknames that were passed through
    unique = False #bool to determine if a name was a unique or not
    readyUp = False #If both players send the ready message
    Name = 0 #Amount of names(????????????????????????) i don't know what this is -Jack
             #found out later, this is actually the thread identifier for setup(), somehow
    nickFound = False #if "NICK:" is found in a message
    evaluated = False #if uniqueness has been tested, this prevents "RETRY" or "READY" from
                      #being sent to the client without testing first. - added by jack
    startGame = False #if the server is ready to enter the gameplay loop
    playerOneScore = 0 #Score of Player One for the Game loop
    score = 0 #Score for an individual round, if 1, player 1 wins, if 2 player 2 wins, if 0 draw
    playerTwoScore = 0 #Score of Player Two for the game loop
    scoreMessage = '' #The final score of the game, sent as a message to the clients.
    
    sentBOTHPLAYERS = False #variable added by jack, true if "BOTHPLAYERS" has been sent to the client.
                            #BOTHPLAYERS signals that both players have sent the "READY" flag.
                            #The reason this is sent is so the clients can send their nicknames
                            #without causing timing issues.
    
    bothPLAYERSCHOSE = False #variable added by jack, true if "PLAYERSCHOSE" has been sent to the client.
                             #BOTHPLAYERS signals that both players have sent valid RPS inputs.
                             #This is to prevent timing issues in the gameplay loop.
    Finished = False #Boolean signalling the game's completion

    while True:
        message = library.recv(connection) #receiving a message
        
        message,nickFound=lookForNick(message,nickFound) # Function that looks
                                                         # for a nickname before
                                                         # sending it to the if loops
        print("Message received: "+message)
        # If the server is not ready to start the game
        if startGame == False:
            #Function to help establish connections, verify nicknames
            message,nickFound,readyUp,Name,ready,unique,evaluated,name,startGame,connection,sentBOTHPLAYERS = setup(message,nickFound,readyUp,Name,ready,unique,evaluated,name,startGame,connection,sentBOTHPLAYERS)
            
            #Signals to the client that both player are connected
            if sentBOTHPLAYERS == False:
                print("SENDING \"BOTHPLAYERS\" TO CLIENT")
                reply = "BOTHPLAYERS"
                library.send(connection, reply)
                sentBOTHPLAYERS = True
                print("SENT \"BOTHPLAYERS\" TO CLIENT")
            
            #Signals to the client that their nickname wasn't unique
            if sentBOTHPLAYERS == True and unique == False and evaluated == True:
                print("SENDING \"RETRY\" TO CLIENT")
                reply = "RETRY"
                library.send(connection, reply)
            
            #Signals to the client that their nickname was unique
            if unique == True:
                    print("SENDING \"READY\" TO CLIENT")
                    reply = "READY"
                    library.send(connection, reply)
                    print("SENT \"READY\" TO CLIENT")
                    startGame = True
        
        #if both nicknames unique and that game isn't completed yet
        if startGame == True and Finished == False:
            reply = "GO"+str(round) #passing the round count to the client so it knows when to check for "SCORE"
            library.send(connection, reply)
            print("SENT \"GO\" TO CLIENT")
            
            #assign threadIDs to global threads list
            #to be used for player identification
            threadID = threading.get_ident()
            if threadID not in gThreads:
                gThreads.append(threadID)
            print("gThreads:", gThreads)
            
            #for loop to play as many rounds as specifed
            for counter in range(0, int(round)):
                #declaration for global variables in case of a timing error
                if "gChoiceList" not in globals():
                    global gChoiceList
                    gChoiceList = ['','']
                if "playerOneCleared" not in globals():
                    global playerOneCleared
                    playerOneCleared = True
                if "playerTwoCleared" not in globals():
                    global playerTwoCleared
                    playerTwoCleared = True
                
                bothPLAYERSCHOSE = False #initialized as false at the start of each run
                getChoices(connection)
                
                #while true, if gchoice is 2 elements, and if neither index is empty and both have been cleared
                while True:
                    if len(gChoiceList) == 2:
                        if gChoiceList[0] != '' and gChoiceList[1] != '' and playerOneCleared == True and playerTwoCleared == True:
                            bothPLAYERSCHOSE = True
                            playerOneCleared == False #initializing for next run
                            playerTwoCleared == False #these two variables exist to prevent keep this while loop busy
                                                      #to prevent timing issues.
                            score = gameLoop() 
                            #gameLoop returns score as 0, 1, 2, or None
                            break
                
                if bothPLAYERSCHOSE == True:
                    #score = 0 means draw, 1 means player 1 win, 2 means player 2 win, None means an index value was blank
                    
                    #If score is 1, add a point to playerOne
                    if score == 1:
                        playerOneScore +=1
                        print("Player 1 wins round ", counter+1)
                    #If score is 2, add a point to player Two
                    elif score == 2:
                        playerTwoScore +=1
                        print("Player two wins round ", counter+1)
                    #If it is 0, then it is a draw, no one gets anything
                    else:
                        print("Round ", counter, " was a draw.")
                        playerOneScore += 0
                        playerTwoScore += 0
                    print("Current Score:   P1:", playerOneScore," P2:", playerTwoScore)
                
                #clear out the choice in the player's gChoiceList index
                threadID = threading.get_ident()
                index = gThreads.index(threadID)
                if index == 0:
                    print("Clearing choice index 0")
                    gChoiceList[0] = ''
                    #print(gChoiceList[0])
                    playerOneCleared = True
                elif index == 1:
                    print("Clearing choice index 1")
                    gChoiceList[1] = ''
                    #print(gChoiceList[1])
                    playerTwoCleared = True
            
            
                if playerOneCleared == False or playerOneCleared == False:
                    print("Waiting for client choices to be cleared.")
                    while playerOneCleared == False or playerTwoCleared == False:
                        sleep(1)
            
            #Display score server-side and prepare the score message for clients
            Finished = True
            if playerOneScore > playerTwoScore:
                print("Player One wins!")
                scoreMessage = "Player One wins!\n"
            elif playerTwoScore > playerOneScore:
                print("Player Two wins!")
                scoreMessage = "Player Two wins!\n"
            else:
                print("Draw!")
                scoreMessage = "Draw!\n"
                
            #sending score message to clients
            print("Player One Score: ",playerOneScore,"\nPlayer Two Score: ",playerTwoScore)
            scoreMessage += ("SCORE:Player One Score: " + str(playerOneScore) + "\nPlayer Two Score: " + str(playerTwoScore) +"STOP")
            library.send(connection, scoreMessage)  
            #ServerSocket.close(connection)
            #ServerSocket.close()
            #ServerSocket.shutdown(connection)
            
            break
            #connection.close()
        
        #If no message is found.
        if not message:
            break

round, port = CLA_Handling()
ServerSocket = socket.socket()
host = socket.gethostbyname("acad.kutztown.edu")

list = [] #unused(?)
players = 0 #player counter
ready = False #if both nicknames are unique (player has received ready)
startGame = False #if the game is ready to be started
playerOne = '' #unused? thread identifier apparently
playerTwo = '' #unused? thread identifier apparently

#bind
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))
    exit()

print('Waiting for players to join!')
ServerSocket.listen(2) #Wait for 2 players to join, 2 players are max

#PARENT
while True:
    #threads = []
    Client, address = ServerSocket.accept()
    print('ip: ' + address[0] + ':' + str(address[1]))

    start_new_thread(threaded_client, (Client, players ))
    players += 1
    
    print('Player ' + str(players) + ': Joined')
    
ServerSocket.close()

if __name__ == '__main__':
    main()
