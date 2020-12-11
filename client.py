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
        print("quitting")
        global Quit
        Quit = True
    
    elif comm is 'w':
        os.system('cls')

    elif comm is 'b':
        answer = ''
        while answer not in ('yes', 'y' , 'no' , 'n'):
            answer = input("Do you want to enter the chase (y/n)? ")
        sendto(answer[0])
    
    elif comm is 'e':
        input()
        sendto()

    elif comm is 'n':
        answer = '-1'
        prompt, *options = msg.split('#')
        while int(answer) not in range(1,len(options)+1):
            print(f"{prompt}")
            for i,option in enumerate(options):
                print(f"{i+1}) {option}.")
            answer = input(f"And your answer is (1-{len(options)})? ")
            os.system('cls')
            if answer == '!lifeline':
                sendto(answer)
                recive()
                return
        sendto(answer)
   

player = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
player.connect(('127.0.0.1',65353))

while not Quit:
    recive()

print('logging off')
player.close()

while True:
    pass
