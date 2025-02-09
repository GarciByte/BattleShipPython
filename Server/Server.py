import socket
import threading
import json
import random
import time
from Utilities.Player import Player
from Utilities.Ship import Ship


class BattleshipServer:
    def __init__(self, host="127.0.0.1", port=7976):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.players = []

        # Tipos de barcos y su tamaño
        self.required_fleet = {
            "Leviatán": 5,
            "Maremoto": 4,
            "Tritón": 3,
            "Neptuno": 3,
            "Centinela": 2
        }

    # Inicia el servidor y acepta conexiones.
    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(2)
        print(f"Servidor iniciado en {self.host}:{self.port}")

        while True:
            client, addr = self.server_socket.accept()
            print(f"Conexión establecida con {addr}")
            threading.Thread(target=self.handle_client, args=(client,)).start()

    # Envía un mensaje json a un cliente
    def send_json(self, client, data):
        client.send(json.dumps(data).encode("utf-8"))

    # Recibe un mensaje json de un cliente
    def receive_json(self, client):
        return json.loads(client.recv(1024).decode("utf-8"))

    # Envía un mensaje json a todos los clientes
    def broadcast(self, data):
        for p in self.players:
            self.send_json(p.client_socket, data)

    # Maneja la comunicación con un cliente.
    def handle_client(self, client):
        try:
            # Conseguimos el nickname del usuario
            self.send_json(client, {"type": "request", "message": "NICKNAME"})
            nickname = self.receive_json(client)["message"]
            
            # Se muestra el nombre del jugador que se ha conectado
            print(f"El jugador {nickname} se ha conectado.")
            
            # Se envia un mensaje de bienvenida al cliente
            self.send_json(client, {"type": "notification", "message": f"¡Bienvenido al servidor, {nickname}!"})
            
            # Creamos al jugador y lo añadimos a la lista
            player = Player(nickname, client)
            self.players.append(player)

            # Esperamos a que haya dos jugadores antes de continuar
            if len(self.players) < 2:
                self.send_json(client, {"type": "notification", "message": "Esperando otro jugador..."})
                while len(self.players) < 2:
                    time.sleep(0.5)
            
            # Notificamos a ambos jugadores que coloquen los barcos
            if len(self.players) == 2 and not hasattr(self, "ships_placed"):
                self.ships_placed = False
                self.broadcast({"type": "action", "action": "place_ships"})
                
            # Recibimos la flota del jugador
            fleet = self.receive_fleet(client)
            
            # Creamos el barco, le asignamos las coordenadas y lo añadimos a la lista
            for ship_data in fleet:
                ship = Ship(ship_data["name"], ship_data["size"])
                ship.add_coordinates(ship_data["coordinates"])
                player.add_ship(ship)

            # Notificamos que hemos obtenido la flota del jugador
            self.send_json(client, {"type": "notification", "message": "Flota recibida en el servidor, esperando oponente..."})

            # Verificamos si todos los jugadores ya han colocado los barcos
            all_players_ready = all(len(player.ships) > 0 for player in self.players)
            if all_players_ready:
                self.ships_placed = True
                self.start_game() # Comienza el juego

            # Bucle principal del juego
            while True:
                data = self.receive_json(client)
                if data.get("action") == "shoot":
                    self.process_attack(player, data["coordinates"])

        except Exception as e:
            print(f"Error: {str(e)}")
            client.close()

    # Recibe la flota de barcos desde el cliente
    def receive_fleet(self, client):
        fleet_data = self.receive_json(client)
        return fleet_data.get("ships", [])

    # Procesa un ataque
    def process_attack(self, attacker, coord):
        # Se obtiene al jugador que no es el atacante
        opponent = next(player for player in self.players if player != attacker)

        # Se procesa el ataque sobre el oponente obteniendo el barco impactado y su estado
        ship, is_sunk = opponent.receive_attack(coord)
        hit = ship is not None
        sunk_ship_name = ship.name if is_sunk else None

        # Se construye el mensaje de resultado y se notifica a ambos jugadores
        shot_result = {
            "type": "shot_result",
            "coordinates": coord,
            "hit": hit,
            "sunk_ship": sunk_ship_name,
            "attacker": attacker.nickname,
            "defender": opponent.nickname 
        }
        self.broadcast(shot_result)

        # Se verifica si el oponente ha perdido toda su flota
        if opponent.all_ships_sunk():
            self.end_game(attacker)
        else:
            # Se cambia de turno si la partida continúa
            self.send_json(opponent.client_socket, {"type": "action", "action": "your_turn"})
            self.send_json(attacker.client_socket, {"type": "action", "action": "wait"})

    # Iniciar el juego
    def start_game(self):
        # Se elige de forma aleatoria el primer turno
        self.current_turn = random.choice(self.players)
        
        # Se notifica a cada jugador si es su turno o debe esperar
        for player in self.players:
            if player == self.current_turn:
                message = {"type": "action", "action": "your_turn"}
            else:
                message = {"type": "action", "action": "wait"}
            self.send_json(player.client_socket, message)

    # Finalizar el juego
    def end_game(self, winner):
        # Se muestra por pantalla y se notifica a cada jugador el ganador
        print(f"Partida terminada. Ganador: {winner.nickname}.")
        result = {"type": "notification", "message": f"Partida terminada. Ganador: {winner.nickname}."}
        self.broadcast(result)


server = BattleshipServer()
server.start()
