import socket,sys
from time import sleep
import random
from threading import Thread

starting_funds = (
    0,
    5000,
    10000,
    15000
)
players = {} #dictionary to hold the players
questions = []
# setting up the socket
MAXPLAYERS = 3 
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(('127.0.0.1',65353))

class Game:
    global questions
    def __init__(self, player):
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
            self.qlist = list(range(len(questions)))

            #money stage
            self.cleanscreen()
            self.lifeline = 0
            rights = 0
            for _ in range(3):
                self.printplayer("These 3 questions will decide the amount of money you start with")
                rights += self.player_question()
            self.balance = starting_funds[rights]
            if rights == 0:
                self.printplayer("You got no questions right \nGo back to the start")
                continue
            
            #setup phase
            self.cleanscreen()
            msg = f"n@Where would you like to start?#In position 3 with {self.balance}$#In position 2 with {self.balance * 2}$#In position 4 with {self.balance // 2}$"
            answer = ''
            while answer not in ('1','2','3'):
                self.sendto(msg)
                answer = self.player.recv(1024).decode('utf8')
            if answer == '1':
                self.playerpos = 3
            elif answer == '2':
                self.playerpos = 2
                self.balance *= 2
            else:
                self.playerpos = 4
                self.balance //= 2
            
            #chase phase
            self.cleanscreen()
            self.lifeline = 1
            while self.playerpos != 7 and self.playerpos != self.chaserpos:
                if len(self.qlist) == 0: self.qlist = list(range(len(questions)))
                self.playerpos += self.player_question()
                self.chaserpos += random.choice((0,1,1,1))
                if self.playerpos != 7 and self.playerpos != self.chaserpos:
                    self.player_status()
                    self.waitrespond()
                self.cleanscreen()

            #end phase
            self.cleanscreen()
            if self.playerpos == 7:
                self.printplayer("Congratulations you won!!!!!!")
                self.printplayer(f"you won {self.balance}$")
            else:
                self.printplayer("You're a looser")
            self.waitrespond()

    def begining(self):
        self.sendto('b@')
        answer = self.player.recv(1024).decode('utf8')
        if answer=='n':
            self.sendto('q@')
            self.player.close()
            players.pop(self.player)
            sys.exit()

    def waitrespond(self):
        self.sendto('e@')
        self.player.recv(1024).decode('utf8')

    def sendto(self,msg = '\n'):
        self.player.send(bytes(str(msg),"utf8"))
        sleep(0.05)

    def cleanscreen(self):
        self.sendto('w@')

    def printplayer(self,msg):
        self.sendto('p@'+str(msg))

    def player_status(self):
        self.printplayer(f'In the bank you have: {self.balance}$')
        self.printplayer(f'The chaser is on stage: {self.chaserpos}')
        self.printplayer(f'You are on stage: {self.playerpos}')
        self.printplayer(f'Lifelines remaining: {self.lifeline}')
        sleep(0.05)
    
    def player_question(self):
        questionIndex = random.choice(self.qlist)
        prompt, *options = questions[questionIndex]
        mix = [0,1,2,3]
        random.shuffle(mix)
        correct = options[0]
        options[mix[0]],options[mix[1]],options[mix[2]],options[mix[3]] = options
        msg = f'Your quetsion is:\n{prompt}#'+'#'.join(options)
        self.sendto('n@'+msg)
        answer = self.player.recv(1024).decode('utf8')
        while answer == '!lifeline':
            if self.lifeline == 0:
                self.printplayer('Looks like you have no more lifelines left\nLets try that question again')
                self.sendto('n@'+msg)
                answer = self.player.recv(1024).decode('utf8')
            else:
                self.lifeline -= 1
                prompt, *options,_,_ = questions[questionIndex]
                mix = [0,1]
                random.shuffle(mix)
                options[mix[0]],options[mix[1]] = options
                msg = f'{prompt}#'+'#'.join(options)
                self.sendto('n@'+msg)
                answer = self.player.recv(1024).decode('utf8')
        self.qlist.remove(questionIndex)
        return options[int(answer.strip())-1] == correct

def chunkdiv(l,n):
    return [l[i:i+n] for i in range(0,len(l),n)]

def handle_player(player,id):
    #thread that will handle the games for each player
    print(f'player {id} has connected')
    game = Game(player)
    game.run()

def reject_player(player):
    global MAXPLAYERS
    player.send(bytes(str(f"p@There are {MAXPLAYERS} players connected already\n"),"utf8"))
    player.send(bytes(str("q@"),"utf8"))

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
            print("A player is attempting to connect")
            Thread(target=reject_player, args=(client,)).start()


if __name__ == "__main__":
    #main
    with open('questions.txt','r',encoding='utf8') as f:
        questions = chunkdiv(list(map(str.strip,f.readlines())),5)
    server.listen(5)
    print("waiting for connection")
    print(server.getsockname())
    #listen to 5 connections
    ACCEPT_THREAD = Thread(target=accept_conn)
    ACCEPT_THREAD.start() #initiate a thread to handle the connection of players
    ACCEPT_THREAD.join()
    server.close()