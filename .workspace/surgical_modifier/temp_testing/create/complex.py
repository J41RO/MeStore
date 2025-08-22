class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.config = {}

    def connect(self):
        """Conectar a la base de datos"""
        print("Conectando...")
        return True

    def disconnect(self):
        """Desconectar"""
        pass
