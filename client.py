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

    elif comm is 'n':
        answer = ''
        while not answer.isnumeric():
            answer = input(f'{msg}: ')
            if answer == '!status' or answer == '!quit':
                sendto(answer)
                recive()
                return
        sendto(answer)

    elif comm is 'w':
        os.system('cls')

    elif comm[0] is 'c':
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

player = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
player.connect((socket.gethostname(),42069))

while not Quit:
    recive()

print('logging off')

while True:
    pass
