import socket, threading

#     A B C D E F G H I J 
# 1                      
# 2                      
# 3                       
# 4                       
# 5                       
# 6                       
# 7                       
# 8                      
# 9                      
# 10


nickname = input( "Choose your nickname: " )
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(( '127.0.0.1' , 7976 ))


def receive () :
    while True :
        try :
            message = client.recv( 1024 ).decode( 'ascii' )
            if message == 'NICKNAME' :
                client.send(nickname.encode( 'ascii' ))
            else :
                print(message)
        except :
            print( "An error occured!" )
            client.close()
            break

def write () :
    while True :
        message = '{}: {}' .format(nickname, input( '' ))
        client.send(message.encode( 'ascii' ))

receive_thread = threading.Thread(target=receive)
receive_thread.start()
write_thread = threading.Thread(target=write)
write_thread.start()