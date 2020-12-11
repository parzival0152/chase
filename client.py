import socket,os
from threading import Thread

Quit = False
def sendto(msg = '\n'): # function to send message to server
    player.send(bytes(str(msg),"utf8")) # send message as bytes. utf8 encoded

# recieve message from server and decodes into message and command then acts accordingly
def recive():
    strm = player.recv(1024).decode("utf8")# decode message recieved from server
    comm , msg = strm.split('@')
    comm_control(comm,msg)# go to comm_control function with decoded command

# follow order according to command 
def comm_control(comm,msg):
    if comm is 'p': #print
        print(msg)

    elif comm is 'q': #quit game
        print("quitting")
        global Quit
        Quit = True
    
    elif comm is 'w': #clear screen "wipe"
        os.system('cls')

    elif comm is 'b': #begin game
        answer = ''
        while answer not in ('yes', 'y' , 'no' , 'n'):
            answer = input("Do you want to enter the chase (y/n)? ")
        sendto(answer[0])
    
    elif comm is 'e': #wait for input and send back
        input()
        sendto()

    elif comm is 'n': #quetion
        answer = '-1'
        prompt, *options = msg.split('#') #load message into prompt and possible answers into options array
        while int(answer) not in range(1,len(options)+1): #until recieved acceptable answer
            print(f"{prompt}") #print question and possible answers
            for i,option in enumerate(options):
                print(f"{i+1}) {option}.")
            answer = input(f"And your answer is (1-{len(options)})? ") #recieve input from player
            os.system('cls') #clear screen
            if answer == '!lifeline': #if chose lifeline send to server and continue
                sendto(answer)
                recive() # recieve new command from server
                return # go back to while loop
        sendto(answer) #if answer was acceptable send to server
   

player = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # create socket for player tcp
player.connect(('127.0.0.1',65353)) # connect to server on ip 127.0.0.1 from port 65353

while not Quit: # until connection ends recieve from server
    recive()

print('logging off') # disconnect message and closing the connection
player.close()

while True:
    pass
