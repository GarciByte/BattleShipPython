import socket
import threading
import json
from Utilities.Ship import Ship


class BattleshipClient:
    def __init__(self):
        self.nickname = input("Elige tu apodo: ")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(("127.0.0.1", 7976))
        self.ships = []
        self.attack_board = {}

    # Inicia el cliente
    def start(self):
        threading.Thread(target=self.listen_server).start()

    # Escucha mensajes del servidor
    def listen_server(self):
        while True:
            try:
                data = self.receive_json()
                self.handle_message(data)
            except Exception as e:
                print(f"Error: {str(e)}")
                self.socket.close()
                break

    # Recibe un mensaje json del servidor
    def receive_json(self):
        return json.loads(self.socket.recv(1024).decode("utf-8"))

    # Envía un mensaje json al servidor
    def send_json(self, data):
        self.socket.send(json.dumps(data).encode("utf-8"))

    # Maneja los mensajes recibidos del servidor
    def handle_message(self, data):
        match data:
            # Envia el nickname del usuario
            case {"type": "request", "message": "NICKNAME"}:
                self.send_json({"type": "nickname", "message": self.nickname})

            # Acciones del jugador
            case {"type": "action", "action": action}:
                match action:
                    # Colocar los barcos
                    case "place_ships":
                        self.place_ships()
                    # Manejar el turno del jugador
                    case "your_turn":
                        self.handle_turn()
                    # Mensaje de espera
                    case "wait":
                        print("\nEsperando turno del oponente...")

            # Mostrar notificaciones
            case {"type": "notification", "message": message}:
                print(f"\n{message}")

            # Mostrar el resultado de un disparo
            case {"type": "shot_result"}:
                self.show_shot_result(data)

    # Colocar los barcos.
    def place_ships(self):
        print("\nElige las coordenadas para colocar tus barcos:")
        
        # Tipos de barcos y su tamaño
        ship_types = {
            "Leviatán": 5,
            "Maremoto": 4,
            "Tritón": 3,
            "Neptuno": 3,
            "Centinela": 2
        }

        # Lista de coordenadas ya ocupadas y lista de barcos colocados
        existing_coords = []
        placed_ships = []

        # Mostrar el tablero inicial
        self.print_board(existing_coords)

        # Iterar sobre cada barco que se debe colocar
        for ship_name, ship_size in ship_types.items():
            
            # Se repite hasta que se coloque el barco correctamente
            while True:
                print(f"\n{ship_name} ({ship_size} celdas)")
                input_coords = []

                # Se pide una coordenada para cada celda del barco
                for i in range(ship_size):
                    
                    # Se repite hasta que la coordenada sea válida
                    while True:
                        user_input = input(f"Coordenada {i + 1}: ").upper()
                        
                        # Se comprueba si esa coordenada es válida
                        if self.validate_coordinate(user_input):
                            # Si es válida, se guarda y se sale del bucle
                            input_coords.append(user_input)
                            break
                        else:
                            print("La coordenada no es válida. Ejemplo: A1")

                # Se crea un barco temporal
                temp_ship = Ship(ship_name, ship_size)
                
                # Se intenta asignar las coordenadas al barco temporal
                is_valid_coords = temp_ship.add_coordinates(input_coords, existing_coords)
                
                # Si son válidas, se agrega el barco a la flota y se actualizan las coordenadas ocupadas
                if is_valid_coords:
                    print(f"\n{ship_name} colocado correctamente.")
                    self.ships.append(temp_ship)
                    existing_coords.extend(input_coords)
                    placed_ships.append(ship_name)
                    self.print_board(existing_coords)
                    break  # Sale del bucle para pasar al siguiente barco
                else:
                    print("Las coordenadas no son válidas o están superpuestas.")

        print("\nBarcos colocados correctamente.")
        self.send_fleet() # Se envía la flota completa al servidor

    # Muestra el tablero del jugador (para colocar los barcos)
    def print_board(self, existing_coords=None):
        print("\n  1 2 3 4 5 6 7 8 9 10")
        
        for row in "ABCDEFGHIJ":
            print(row, end=" ")
            
            for col in range(1, 11):
                coord = f"{row}{col}"
                
                if existing_coords and coord in existing_coords:
                    print("■", end=" ")  # Barco
                else:
                    print(".", end=" ")  # Agua
            print()
            
    # Muestra el tablero del jugador (para disparar a los barcos del oponente)
    def print_attack_board(self):
        print("\n  1 2 3 4 5 6 7 8 9 10")
        
        for row in "ABCDEFGHIJ":
            print(row, end=" ")
            
            for col in range(1, 11):
                coord = f"{row}{col}"
                
                if coord in self.attack_board:
                    if self.attack_board[coord] == "hit":
                        symbol = "X" # Coordenada de barco tocado
                    
                    elif self.attack_board[coord] == "miss":
                        symbol = "O" # Coordenada que es agua 
                else:
                    symbol = "." # Coordenada sin descubrir
                    
                print(symbol, end=" ")
            print()
            
    # Comprobar si una coordenada es válida
    def validate_coordinate(self, coord):
        try:
            row = coord[0].upper() # Obtener la fila
            col = int(coord[1:]) # Obtener la columna
            is_row_valid = ("A" <= row) and (row <= "J") # Comprueba si la fila es válida
            is_col_valid = (1 <= col) and (col <= 10) # Comprueba si la columna es válida
            return is_row_valid and is_col_valid

        except Exception:
            return False

    # Envía la flota completa del jugador al servidor
    def send_fleet(self):
        ships_data = []
        for ship in self.ships:
            ship_info = {
                "name": ship.name,
                "size": ship.size,
                "coordinates": ship.coordinates,
            }
            ships_data.append(ship_info)

        fleet_data = {
            "player": self.nickname,
            "ships": ships_data,
        }
        self.send_json(fleet_data)

    # Maneja el turno del jugador
    def handle_turn(self):
        print("\n¡ES TU TURNO!")
        self.print_attack_board() # Se muestra el estado actual del tablero
        
        while True:
            # Pedir la coordenada a la que se va a disparar
            user_input = input("\nIngresa la coordenada a la que vas a disparar: ").upper()
            
            # Se comprueba si esa coordenada es válida
            if self.validate_coordinate(user_input):
                
                # Si es válida, se envía al servidor y se sale del bucle
                self.send_json({"action": "shoot", "coordinates": user_input})
                break
            else:
                print("La coordenada no es válida. Ejemplo: A1")

    # Muestra el resultado de un disparo y actualiza el tablero
    def show_shot_result(self, data):
        
        # Se extraen los datos
        hit_occurred = data["hit"]
        coordinate = data["coordinates"]
        sunk_ship = data["sunk_ship"]
        attacker = data.get("attacker", "")
        
        # Se actualiza el tablero
        if attacker == self.nickname:
            if hit_occurred:
                self.attack_board[coordinate] = "hit"
            else:
                self.attack_board[coordinate] = "miss"
            self.print_attack_board()

        # Se construye el mensaje
        if hit_occurred:
            message = f"¡IMPACTO en {coordinate}!"
            if sunk_ship:
                message += f"\n\n¡El barco {sunk_ship} de {data['defender']} se ha hundido!"
        else:
            message = f"¡AGUA en {coordinate}!"

        # Mostrar el mensaje
        print(f"\n{message}")


client = BattleshipClient()
client.start()
