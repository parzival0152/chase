##########################################
#   code made by:                        #
#               Ilay Tzuberi - 211873286 #
#               Omri Baron   - 314838210 #
##########################################
import socket,sys
from time import sleep
import random
from threading import Thread

starting_funds = (
    0,
    5000,
    10000,
    15000
) # touple to hold our starting funds
players = {} #dictionary to hold the players
questions = [] #list to store our questions
MAXPLAYERS = 3 #global variables
ENDGOAL = 7
# setting up the socket
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(('127.0.0.1',65353))

class Game:
    global questions
    def __init__(self, player):
        #init game object with all needed variables
        self.player = player
        self.qlist = list(range(len(questions)))
        self.playerpos = 0
        self.chaserpos = 0
        self.balance = 0
        self.lifeline = 0

    def run(self):
        while True:
            #start phase
            self.cleanscreen()
            self.begining()

            #intoduction
            self.cleanscreen()
            self.printplayer("Welcome to \"The Chase\"")
            self.printplayer("To start the game press Enter")
            self.waitrespond()
            self.qlist = list(range(len(questions))) #reset question bank just in case

            #money stage
            self.cleanscreen()
            self.lifeline = 0 #set lifelines to zero cause we dont give out help to people who are just starting out
            rights = 0 # variable to tell us how wrong/right out player is 
            for _ in range(3): # ask the player 3 questions
                self.printplayer("These 3 questions will decide the amount of money you start with")
                rights += self.player_question() # add up the amount of correct answers he gave
            self.balance = starting_funds[rights] # set his funds to the appropriate amount
            if rights == 0:
                #if the player managed to not get any question right
                self.printplayer("You got no questions right \nGo back to the start") #tell him
                continue # and go the the start
            
            #setup phase
            self.cleanscreen()
            msg = f"n@Where would you like to start?#In position 3 with {self.balance}$#In position 2 with {self.balance * 2}$#In position 4 with {self.balance // 2}$"
            self.sendto(msg) #ask the player where would they like to start
            answer = self.recvfrom() #get their answer
            if answer == '1':
                self.playerpos = 3
            elif answer == '2':
                self.playerpos = 2
                self.balance *= 2
            else:
                self.playerpos = 4
                self.balance //= 2
            #set position and balance accordingly

            #chase phase
            global ENDGOAL
            self.cleanscreen()
            self.lifeline = 1 # give the player 1 lifeline from here on out
            while self.playerpos != ENDGOAL and self.playerpos != self.chaserpos: #while one of our end conditions were not met
                if len(self.qlist) == 0: self.qlist = list(range(len(questions)))
                self.playerpos += self.player_question() #ask the player a question
                self.chaserpos += random.choice((0,1,1,1)) #advance the chaser by 1 w.p. of 75%
                if self.playerpos != ENDGOAL and self.playerpos != self.chaserpos: #if we arent done
                    self.player_status() #print status
                    self.waitrespond()
                self.cleanscreen()

            #end phase
            self.cleanscreen()
            if self.playerpos == ENDGOAL: #if player won
                self.printplayer("Congratulations you won!!!!!!") #announce that he won
                self.printplayer(f"you won {self.balance}$") #display his earnings
            else:
                self.printplayer("You're a looser") #otherwise tell him that he is a loser
            self.waitrespond() #wait to start again

    def begining(self):
        self.playerpos = 0
        self.chaserpos = 0
        #reset all positions
        self.sendto('b@') #send begin instruct command
        answer = self.recvfrom()
        if answer=='n': #if player dosent want to play
            self.sendto('q@') #instruct player to quit
            self.player.close() #close connection
            players.pop(self.player) #remove from memory to free room for more players
            sys.exit() #terminate thread

    def waitrespond(self):
        #this command does nothing but wait for the client to press enter
        #it simply ignores all other input
        self.sendto('e@') #send 'e' instruction
        self.recvfrom() #wait to hear back

    def sendto(self,msg = '\n'):
        self.player.send(bytes(str(msg),"utf8")) #encode message and send it to the player
        sleep(0.05)

    def recvfrom(self):
        temp = '' #make a temp variable
        try:
            temp = self.player.recv(1024).decode('utf8') #try to recive from player
            return temp
        except: #if fails this means that our player disconnected mid game
            self.player.close() #close connection
            players.pop(self.player) #remove from memory to free room for more players
            sys.exit() #terminate thread      

    def cleanscreen(self):
        self.sendto('w@') # send clear screen instruction

    def printplayer(self,msg):
        self.sendto('p@'+str(msg)) #send print instruction followed with the msg to print

    def player_status(self):
        #print all needed variables to the player
        self.printplayer(f'In the bank you have: {self.balance}$')
        self.printplayer(f'The chaser is on stage: {self.chaserpos}')
        self.printplayer(f'You are on stage: {self.playerpos}')
        self.printplayer(f'Lifelines remaining: {self.lifeline}')
        sleep(0.05) #wait 50ms for good measure
    
    def player_question(self):
        questionIndex = random.choice(self.qlist) # get a random question index
        prompt, *options = questions[questionIndex] #get prompt and 
        mix = [0,1,2,3] # create a list of indexes
        random.shuffle(mix) #shuffle them around
        correct = options[0] # the fisrt options is always correct
        options[mix[0]],options[mix[1]],options[mix[2]],options[mix[3]] = options # assaign the options random locations in the list based on the mix
        msg = f'Your quetsion is:\n{prompt}#'+'#'.join(options) #combine the prompt and the options, seperated by '#' to aid in client side seperation
        self.sendto('n@'+msg) #send question command and msg to player
        answer = self.recvfrom() # get answer
        while answer == '!lifeline': #if the player requsted a lifeline
            if self.lifeline == 0: # if player has no lifeline
                self.printplayer('Looks like you have no more lifelines left\nLets try that question again') #tell him that his shit out of luck
                self.sendto('n@'+msg) #ask the question again
                answer = self.recvfrom()#wait for answer
            else: #in the case that he do have a lifeline
                self.lifeline -= 1 #reduce it by one (incase we want to add even more lifelines in the future)
                prompt, *options,_,_ = questions[questionIndex] #get the prompt and options again
                                                                #only this time we ignore 2 options at the back
                mix = [0,1] #this time we mix with 2 places
                random.shuffle(mix)
                options[mix[0]],options[mix[1]] = options #same process of mix and assaign as before
                msg = f'{prompt}#'+'#'.join(options) #create new message
                self.sendto('n@'+msg) #ask the new message
                answer = self.recvfrom() #await answer once more
        self.qlist.remove(questionIndex) #remove question index from the list of possible indecies
        return options[int(answer.strip())-1] == correct #check if the option the player chose is the same as the coeerct one
        #keeping hold of the correct answers index was proving too hard
        #so instead we remember the correct answer and check it against the options the player chose (-1 cause python starts indexing at 0)
        #this function will return a True or False value but because python evaluates them as 1 and 0 we can add it to the player position to make him advance only if he is right

def chunkdiv(l,n):
    return [l[i:i+n] for i in range(0,len(l),n)] # devide the list l into n sized chunks

def handle_player(player,id):
    #thread that will handle the games for each player
    print(f'player {id} has connected')
    game = Game(player) #create game
    game.run() #run game

def reject_player(player):
    global MAXPLAYERS
    player.send(bytes(str(f"p@There are {MAXPLAYERS} players connected already\n"),"utf8")) # send explenation message
    player.send(bytes(str("q@"),"utf8")) # instruct client to dissconnect
    player.close()
    sys.exit() #terminate thread

def accept_conn():
    #accept thread
    i = 0 #connection counter, used while debugging
    while True:
        client, client_address = server.accept()# accept incoming cennction
        # keep the server reading sonnections
        if len(players)<MAXPLAYERS:
            # connect players if less then 3 players are connected
            i+=1
            players[client] = client_address # store to keep track
            Thread(target=handle_player, args=(client,i,)).start()
            # start another thread to deal with player
        else:
            print("A player is attempting to connect") # print to tell us that someone is attempton connection
            Thread(target=reject_player, args=(client,)).start() # start a thread to handle rejecting this connection


if __name__ == "__main__":
    #main
    with open('questions.txt','r',encoding='utf8') as f: #open questions file
        questions = chunkdiv(list(map(str.strip,f.readlines())),5) #devide lines from files into 5 line chunks
    server.listen(5) #listen to 5 connections
    print("waiting for connection")
    print(server.getsockname())
    ACCEPT_THREAD = Thread(target=accept_conn)
    ACCEPT_THREAD.start() #initiate a thread to handle the connection of players
    ACCEPT_THREAD.join() #join thread so main will not imidiatly die
    server.close()