import socket
import threading
import json

########################
#   0 1 2 3 4 5 6 7 8 9
# A
# B
# C
# D
# E
# F
# G
# H
# I
# J

nickname = input("Elige tu apodo: ")
host = "127.0.0.1"
port = 7976

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))


def receive():
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            message_data = json.loads(message)

            if "type" in message_data:

                # Apodo
                if (message_data["type"] == "request" and message_data["message"] == "NICKNAME"):
                    client.send(json.dumps({
                        "type": "nickname", 
                        "message": nickname
                        }).encode("utf-8"))

                # Notificación
                elif message_data["type"] == "notification":
                    print(message_data["message"])

                # Acción
                elif message_data["type"] == "action":

                    # Colocar barcos
                    if message_data["action"] == "place_ships":
                        place_ships()

        except:
            print("Se ha producido un error.")
            client.close()
            break


def place_ships():
    barcos = input("Barcos: ")

    ships = {
        "Barco 1": ["A1", "A2", "A3", "A4", "A5"],
        "Barco 2": ["B1", "B2", "B3", "B4"],
        "Barco 3": ["C1", "C2", "C3"],
        "Barco 4": ["D1", "D2", "D3"],
        "Barco 5": ["E1", "E2"],
    }

    message_data = {"player": nickname, "ships": ships}

    client.send(json.dumps(message_data).encode("utf-8"))


receive_thread = threading.Thread(target=receive)
receive_thread.start()
