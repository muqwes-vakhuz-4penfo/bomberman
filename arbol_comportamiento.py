# arbol_comportamiento.py

class Nodo:
    def __init__(self):
        pass

    def ejecutar(self):
        pass

class Selector(Nodo):
    def __init__(self, hijos):
        super().__init__()
        self.hijos = hijos

    def ejecutar(self):
        for hijo in self.hijos:
            if hijo.ejecutar():
                return True
        return False

class Secuencia(Nodo):
    def __init__(self, hijos):
        super().__init__()
        self.hijos = hijos

    def ejecutar(self):
        for hijo in self.hijos:
            if not hijo.ejecutar():
                return False
        return True

class Accion(Nodo):
    def __init__(self, accion):
        super().__init__()
        self.accion = accion

    def ejecutar(self):
        return self.accion()
