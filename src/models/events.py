
class Event:
    @property
    def get_lobbies(self):
        return "Actualizar lista de partidas"
    
    def end_turn(self):
        return "Terminó turno"

    def winner(self):
        return "Hay Ganador"