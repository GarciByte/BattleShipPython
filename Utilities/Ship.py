class Ship:
    def __init__(self, name, size):
        self.name = name        # Nombre del barco
        self.size = size        # Tamaño del barco
        self.coordinates = []   # Coordenadas del barco
        self.hits = set()       # Coordenadas impactadas del barco

    # Verifica si el barco está completamente hundido.
    @property
    def is_sunk(self):
        return len(self.hits) == self.size

    # Añade y comprueba las coordenadas del barco.
    def add_coordinates(self, coordinates, existing_coords=[]):

        are_valid = self.validate_coordinates(coordinates)
        has_overlap = self.check_overlap(coordinates, existing_coords)

        if are_valid and not has_overlap:
            self.coordinates = coordinates
            return True

        return False

    # Comprueba las coordenadas del barco.
    def validate_coordinates(self, coords):
        rows, cols = self.extract_rows_and_cols(coords)

        if self.are_coords_horizontal(rows):
            return self.are_cols_consecutive(cols)

        if self.are_coords_vertical(cols):
            return self.are_rows_consecutive(rows)

        return False

    # Extrae las filas y columnas de las coordenadas.
    def extract_rows_and_cols(self, coords):
        rows = []
        cols = []

        for c in coords:
            row = c[0].upper()  # Convertir a mayúscula
            col = int(c[1:])  # Convertir a número
            rows.append(row)
            cols.append(col)

        return rows, cols

    # Verifica si las coordenadas están en la misma fila.
    def are_coords_horizontal(self, rows):
        unique_rows = set(rows)
        return len(unique_rows) == 1

    # Verifica si las coordenadas están en la misma columna.
    def are_coords_vertical(self, cols):
        unique_cols = set(cols)
        return len(unique_cols) == 1

    # Verifica si las columnas son consecutivas.
    def are_cols_consecutive(self, cols):
        sorted_cols = sorted(cols)  # Ordenar la lista
        min_col = min(sorted_cols)
        max_col = max(sorted_cols)
        expected_cols = list(range(min_col, max_col + 1))  # Lista esperada

        return sorted_cols == expected_cols

    # Verifica si las filas son consecutivas.
    def are_rows_consecutive(self, rows):
        row_numbers = [ord(r) for r in rows]  # Convertir letras a valores ASCII
        sorted_rows = sorted(row_numbers)
        min_row = min(sorted_rows)
        max_row = max(sorted_rows)
        expected_rows = list(range(min_row, max_row + 1))  # Lista esperada

        return sorted_rows == expected_rows

    # Verifica si hay superposición entre nuevas coordenadas y las existentes.
    def check_overlap(self, new_coords, existing_coords):
        for coord in new_coords:
            if coord in existing_coords:
                return True

        return False

    # Registra un impacto en el barco.
    def receive_attack(self, coord):
        hit_successful = coord in self.coordinates

        if hit_successful:
            self.hits.add(coord)

        return hit_successful
