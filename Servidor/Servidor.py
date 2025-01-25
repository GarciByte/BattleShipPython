import socket
import threading
import json

host = "127.0.0.1"
port = 7976

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(2)

clients = []
nicknames = []
players_ships = []

game_started = False

first_player = None
first_player_nickname = None
first_player_ships = None

second_player = None
second_player_nickname = None
second_player_ships = None


def handle(client):
    global first_player, first_player_nickname, first_player_ships
    global second_player, second_player_nickname, second_player_ships

    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            message_data = json.loads(message)

            if "ships" in message_data:
                print(f"Barcos del jugador {message_data['player']} obtenidos.")
                players_ships.append({
                    "player": message_data["player"],
                    "ships": message_data["ships"],
                })

                if len(players_ships) == 2:
                    print("Los barcos de ambos jugadores se han obtenido.")
                    first_player = players_ships[0]
                    first_player_nickname = first_player["player"]
                    first_player_ships = first_player["ships"]

                    second_player = players_ships[1]
                    second_player_nickname = second_player["player"]
                    second_player_ships = second_player["ships"]

                    print(f"Barcos del jugador {first_player_nickname}:")
                    for barco, posiciones in first_player_ships.items():
                        print(f"{barco}: {posiciones}")

                    print(f"Barcos del jugador {second_player_nickname}:")
                    for barco, posiciones in second_player_ships.items():
                        print(f"{barco}: {posiciones}")

        except:
            print("Se ha producido un error.")
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break


def receive():
    print(f"Servidor iniciado en {host}:{port}")
    global game_started

    while True:
        if len(clients) < 2:
            client, address = server.accept()
            print(f"Conexión establecida con {address}")

            # Apodo
            client.send(json.dumps({"type": "request", "message": "NICKNAME"}).encode("utf-8"))
            nickname_data = json.loads(client.recv(1024).decode("utf-8"))

            if nickname_data["type"] == "nickname":
                nickname = nickname_data["message"]
                nicknames.append(nickname)
                clients.append(client)
                print(f"Jugador {nickname} conectado.")

                client.send(json.dumps({
                    "type": "notification",
                    "message": f"¡Bienvenido al servidor {nickname}! Esperando otro jugador...",
                }).encode("utf-8"))

                thread = threading.Thread(target=handle, args=(client,))
                thread.start()

        if len(clients) == 2 and not game_started:
            print("Hay 2 jugadores, el juego va a comenzar.")
            
            for client in clients:
                
                client.send(json.dumps({
                    "type": "notification",
                    "message": "El juego ha comenzado. Prepárate para colocar tus barcos.",
                }).encode("utf-8"))

                client.send(json.dumps({
                    "type": "action",
                    "action": "place_ships"
                }).encode("utf-8"))
                
                game_started = True


receive()
