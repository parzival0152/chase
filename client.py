import socket,os
from threading import Thread

Quit = False
def sendto(msg = '\n'):
    player.send(bytes(str(msg),"utf8"))

def recive():
    strm = player.recv(1024).decode("utf8")
    [comm , msg] = strm.split('@')
    comm_control(comm,msg)

def comm_control(comm,msg):
    if comm is 'p':
        print(msg)

    elif comm is 'q':
        global Quit
        Quit = True
    
    elif comm is 'w':
        os.system('cls')

    elif comm is 'n':
        answer = ''
        while not answer.isnumeric():
            answer = input(f'{msg}: ')
            if answer == '!status' or answer == '!quit':
                sendto(answer)
                recive()
                return
        sendto(answer)

    elif comm is 'c':
        comm = comm[1:]
        options = comm[comm.index('(')+1:comm.index(')')].split(',')
        answer = ''
        while answer not in options:
            answer = input(f"{msg} ({','.join(options)}): ")
            if answer == '!status' or answer == '!quit':
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
        player.connect(('127.0.0.1',42069))

player = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
begining()

while not Quit:
    recive()

print('logging off')

while True:
    pass
