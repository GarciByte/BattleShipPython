class Player:
    def __init__(self, nickname, client_socket):
        self.nickname = nickname                # Apodo del jugador
        self.client_socket = client_socket      # Socket del cliente
        self.ships = []                         # Lista de barcos del jugador
        self.hits_received = set()              # Coordenadas impactadas por el oponente

    # Añade un barco a la flota del jugador.
    def add_ship(self, ship):
        self.ships.append(ship)

    # Verifica si todos los barcos del jugador están hundidos.
    def all_ships_sunk(self):
        all_sunk = all(ship.is_sunk for ship in self.ships)
        return all_sunk

    # Procesa un ataque en una coordenada.
    def receive_attack(self, coord):
        for ship in self.ships:
            hit = ship.receive_attack(coord)  # Intentar impactar un barco

            if hit:
                is_sunk = ship.is_sunk  # Verificar si el barco se hundió
                return ship, is_sunk

        return None, False  # No hubo impacto
