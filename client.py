import socket,os
from threading import Thread

Quit = False
def sendto(msg = '\n'):
    player.send(bytes(str(msg),"utf8"))

def recive():
    strm = player.recv(1024).decode("utf8")
    comm , msg = strm.split('@')
    comm_control(comm,msg)

def comm_control(comm,msg):
    if comm is 'p':
        print(msg)

    elif comm is 'q':
        global Quit
        Quit = True
    
    elif comm is 'w':
        os.system('cls')

    elif comm is 'b':
        begining()
    
    elif comm is 'e':
        input()
        sendto()

    elif comm is 'n':
        answer = ''
        while answer not in ('1','2','3','4'):
            prompt, *options = msg.split('#')
            print(f"Your quetsion is:\n{prompt}")
            for i,option in enumerate(options):
                print(f"{i+1}) {option}.")
            answer = input("And your answer is (1-4)? ")
            os.system('cls')
            if answer == '!lifeline':
                sendto(answer)
                recive()
                return
        sendto(answer)

def begining():
    global Quit
    answer = ''
    while answer not in ('yes', 'y' , 'no' , 'n'):
        answer = input("Do you want to enter the chase (y/n)? ")

    if answer in ('no', 'n'):
        Quit = True
        player.close()

    elif answer in ('yes','y'):
        pass

player = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
player.connect(('127.0.0.1',65353))
begining()

while not Quit:
    recive()

print('logging off')

while True:
    pass
