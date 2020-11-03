import socket,sys
from time import sleep
import random
from threading import Thread

players = {} #dictionary to hold the players
questions = []
# setting up the socket
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
        self.lifeline = 1

    def run(self):
        pass

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
        self.qlist.remove(questionIndex)
        prompt, *options = questions[questionIndex]
        mix = [0,1,2,3]
        random.shuffle(mix)
        correct = options[0]
        options[mix[0]],options[mix[1]],options[mix[2]],options[mix[3]] = options
        msg = f'{prompt}#'+'#'.join(options)
        self.sendto('n@'+msg)
        answer = self.player.recv(1024).decode('utf8')
        while answer is '!lifeline':
            if self.lifeline == 0:
                self.printplayer('Looks like you have no more lifelines left\nLets try that question again')
                self.sendto('n@'+msg)
                answer = self.player.recv(1024).decode('utf8')
            else:
                pass
        return int(answer.strip()) == correct


def chunkdiv(l,n):
    return [l[i:i+n] for i in range(0,len(l),n)]

def handle_player(player,id):
    #thread that will handle the games for each player
    print(f'player {id} has connected')
    game = Game(player)
    game.run()
         
def accept_conn():
    #accept thread
    i = 0 #connection counter, used while debugging
    while True:
        # keep the server reading sonnections
        while len(players)<3:
            # connect players if less then 2 players are connected
            client, client_address = server.accept() # accept incoming cennction
            i+=1
            players[client] = client_address # store to keep track
            Thread(target=handle_player, args=(client,i,)).start()
            # start another thread to deal with player


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