import socket,sys
from time import sleep
import random
from threading import Thread

def handle_player(player,id):
    #thread that will handle the games for each player
    print(f'player {id} has connected')
         
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

# setting up the socket
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(('127.0.0.1',65353))

players = {} #dictionary to hold the players

if __name__ == "__main__":
    #main
    server.listen(5)
    print("waiting for connection")
    print(server.getsockname())
    #listen to 5 connections
    ACCEPT_THREAD = Thread(target=accept_conn)
    ACCEPT_THREAD.start() #initiate a thread to handle the connection of players
    ACCEPT_THREAD.join()
    server.close()