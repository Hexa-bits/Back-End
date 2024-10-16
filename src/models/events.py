class Event:
    @property
    def get_lobbies(self):
        return "Actualizar lista de partidas"
    
    @property
    def end_turn(self):
        return "Terminó turno"
    
    @property
    def leave_lobby(self):
        return "Se unió/abandonó jugador en lobby"
    
    @property
    def cancel_lobby(self):
        return "La partida se canceló"
    
    @property
    def get_winner(self):
        return "Hay Ganador"
    
    @property
    def get_tablero(self):
        return "Hay modificación de Tablero"

    @property
    def get_cartas_mov(self):
        return "Actualizar cartas de movimientos"
    
    @property
    def start_partida(self):
        return "La partida inició"
    
    @property
    def join_game(self):
        return "Se unió/abandonó jugador en lobby"
