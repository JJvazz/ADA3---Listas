# ==============================================================================
# ESTRUCTURA DE DATOS - ARREGLO DE POSTRES CON LISTAS ENLAZADAS
# Alumno: Johan Alexander Coot Vazquez
# ==============================================================================
import gc
import unicodedata
import weakref


def clave(texto):
    """Clave de comparacion: sin espacios extra, sin acentos y sin mayusculas.
    Asi 'Flan', 'flan ' y 'FLAN' se consideran el mismo postre."""
    texto = " ".join(texto.split())
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto.casefold()


def nombre_valido(texto):
    """Valida que el nombre sea una cadena no vacia."""
    return isinstance(texto, str) and clave(texto) != ""


class NodoIngrediente:
    def __init__(self, nombre):
        self.nombre = nombre
        self.siguiente = None          # NIL = None


class ListaIngredientes:
    def __init__(self):
        self.cabeza = None

    def esta_vacia(self):
        return self.cabeza is None

    def existe(self, nombre):
        actual = self.cabeza
        while actual:
            if clave(actual.nombre) == clave(nombre):
                return True
            actual = actual.siguiente
        return False

    def insertar(self, nombre):
        """Inserta al final. Devuelve True si insertó, False si no."""
        if not nombre_valido(nombre):
            print("  [!] Error: el nombre del ingrediente no puede estar vacío.")
            return False
        if self.existe(nombre):
            print(f"  [!] El ingrediente '{nombre}' ya existe en este postre.")
            return False
        nuevo = NodoIngrediente(" ".join(nombre.split()))
        if self.cabeza is None:
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo
        return True

    def eliminar(self, nombre):
        """Elimina un nodo. Devuelve True si lo eliminó, False si no."""
        if self.cabeza is None:
            print("  [!] Error: la lista de ingredientes está vacía.")
            return False
        if clave(self.cabeza.nombre) == clave(nombre):      # primer nodo
            self.cabeza = self.cabeza.siguiente
            return True
        actual = self.cabeza
        while actual.siguiente:
            if clave(actual.siguiente.nombre) == clave(nombre):
                actual.siguiente = actual.siguiente.siguiente
                return True
            actual = actual.siguiente
        print(f"  [!] Error: ingrediente '{nombre}' no encontrado.")
        return False

    def como_lista(self):
        datos, actual = [], self.cabeza
        while actual:
            datos.append(actual.nombre)
            actual = actual.siguiente
        return datos

    def imprimir(self):
        datos = self.como_lista()
        if not datos:
            print("  (Sin ingredientes)")
        else:
            print("  Ingredientes: " + ", ".join(datos))


class Postre:
    def __init__(self, nombre):
        self.nombre = " ".join(nombre.split())
        self.ingredientes = ListaIngredientes()


class SistemaPostres:
    def __init__(self):
        self.POSTRES = []              # arreglo principal (ordenado)

    def buscar_postre(self, nombre):
        if not nombre_valido(nombre):
            return None
        for p in self.POSTRES:
            if clave(p.nombre) == clave(nombre):
                return p
        return None

    # d. Alta de un postre con todos sus ingredientes
    def alta_postre(self, nombre, lista_inicial, permitir_repetido=False):
        if not nombre_valido(nombre):
            print("[!] Error: el nombre del postre no puede estar vacío.")
            return False
        if self.buscar_postre(nombre) and not permitir_repetido:
            print(f"[!] Error: el postre '{nombre}' ya existe. Alta cancelada.")
            return False
        nuevo = Postre(nombre)
        for ing in lista_inicial:
            nuevo.ingredientes.insertar(ing)
        if nuevo.ingredientes.esta_vacia():
            print(f"[~] Aviso: '{nombre}' se registra sin ingredientes.")
        # inserción manteniendo orden alfabético
        pos = len(self.POSTRES)
        for i in range(len(self.POSTRES)):
            if clave(nuevo.nombre) < clave(self.POSTRES[i].nombre):
                pos = i
                break
        self.POSTRES.insert(pos, nuevo)
        print(f"[*] Postre '{nuevo.nombre}' dado de ALTA exitosamente.")
        return True

    # e. Baja de un postre con todos sus ingredientes
    def baja_postre(self, nombre):
        if not self.POSTRES:
            print("[!] Error: el arreglo POSTRES está vacío.")
            return False
        for i in range(len(self.POSTRES)):
            if clave(self.POSTRES[i].nombre) == clave(nombre):
                del self.POSTRES[i]
                print(f"[*] Postre '{nombre}' y todos sus ingredientes dados de BAJA.")
                return True
        print(f"[!] Error: el postre '{nombre}' no existe en el arreglo.")
        return False

    # a. Imprimir los ingredientes de un postre
    def imprimir_ingredientes(self, nombre):
        postre = self.buscar_postre(nombre)
        if postre is None:
            print(f"[!] Error: el postre '{nombre}' no existe.")
            return False
        print(f"Postre: {postre.nombre}")
        postre.ingredientes.imprimir()
        return True

    # b. Insertar un ingrediente en un postre
    def insertar_ingrediente(self, nombre_postre, ingrediente):
        postre = self.buscar_postre(nombre_postre)
        if postre is None:
            print(f"[!] Error: el postre '{nombre_postre}' no existe.")
            return False
        if postre.ingredientes.insertar(ingrediente):   # solo si realmente insertó
            print(f"[*] Ingrediente '{ingrediente}' añadido a '{postre.nombre}'.")
            return True
        return False

    # c. Eliminar un ingrediente de un postre
    def eliminar_ingrediente(self, nombre_postre, ingrediente):
        postre = self.buscar_postre(nombre_postre)
        if postre is None:
            print(f"[!] Error: el postre '{nombre_postre}' no existe.")
            return False
        if postre.ingredientes.eliminar(ingrediente):
            print(f"[*] Ingrediente '{ingrediente}' eliminado de '{postre.nombre}'.")
            return True
        return False

    # ---- Punto 2: eliminar repetidos ----------------------------------------
    def eliminar_repetidos_incorrecto(self):
        """VERSIÓN CON ERROR (solo demostración): 'for' + del sobre la misma lista."""
        for i in range(len(self.POSTRES)):          # len se calcula UNA sola vez
            if i > 0 and clave(self.POSTRES[i].nombre) == clave(self.POSTRES[i - 1].nombre):
                del self.POSTRES[i]                 # el arreglo se encoge...

    def eliminar_repetidos(self, fusionar=True):
        """VERSIÓN CORRECTA: 'while' con índice manual.
        Como POSTRES está ordenado, los repetidos son adyacentes.
        Si fusionar=True, los ingredientes del repetido pasan al original."""
        print("\n[*] Iniciando depuración (eliminar repetidos)...")
        if len(self.POSTRES) < 2:
            print("[*] Nada que depurar (menos de 2 postres).")
            return []
        eliminados = []
        i = 1
        while i < len(self.POSTRES):
            anterior, actual = self.POSTRES[i - 1], self.POSTRES[i]
            if clave(anterior.nombre) == clave(actual.nombre):
                if fusionar:
                    for ing in actual.ingredientes.como_lista():
                        anterior.ingredientes.insertar(ing)
                eliminados.append(weakref.ref(actual.ingredientes))
                print(f"    - Eliminando repetido: '{actual.nombre}'")
                del self.POSTRES[i]     # NO se incrementa i: todo se recorrió a la izquierda
            else:
                i += 1
        print("[*] Depuración completada.")
        return eliminados

    def mostrar(self):
        print("Arreglo POSTRES:")
        if not self.POSTRES:
            print("  (vacío)")
        for p in self.POSTRES:
            ings = ", ".join(p.ingredientes.como_lista()) or "(sin ingredientes)"
            print(f"  - {p.nombre}: {ings}")


# ==============================================================================
# EJECUCIÓN Y PRUEBAS DE VALIDACIÓN
# ==============================================================================
if __name__ == "__main__":
    s = SistemaPostres()

    print("=== CASOS LÍMITE CON ARREGLO VACÍO ===")
    s.baja_postre("Flan")
    s.imprimir_ingredientes("Flan")

    print("\n=== INCISO D: ALTA ===")
    s.alta_postre("Pastel de Chocolate", ["Harina", "Huevos", "Cacao"])
    s.alta_postre("Flan", ["Leche", "Huevos", "Azúcar", "Vainilla"])
    # minúscula + ingrediente repetido dentro de la lista inicial
    s.alta_postre("arroz con leche", ["Arroz", "Leche", "Canela", "Leche"])
    s.alta_postre("Gelatina", [])                    # sin ingredientes
    s.alta_postre("   ", ["Agua"])                   # nombre vacío
    s.alta_postre("FLAN", ["Agua"])                  # repetido (mayúsculas): se rechaza
    s.mostrar()

    print("\n=== INCISO A: IMPRIMIR ===")
    s.imprimir_ingredientes("Pastel de Chocolate")
    s.imprimir_ingredientes("flan")                  # no distingue mayúsculas
    s.imprimir_ingredientes("Gelatina")              # lista vacía
    s.imprimir_ingredientes("Tiramisú")              # no existe

    print("\n=== INCISO B: INSERTAR INGREDIENTE ===")
    s.insertar_ingrediente("Flan", "Leche Condensada")   # correcto
    s.insertar_ingrediente("Flan", "leche")              # repetido (ya no dice 'añadido')
    s.insertar_ingrediente("Flan", "   ")                # vacío
    s.insertar_ingrediente("Tiramisú", "Café")           # postre inexistente
    s.insertar_ingrediente("Gelatina", "Grenetina")      # a lista vacía

    print("\n=== INCISO C: ELIMINAR INGREDIENTE ===")
    s.eliminar_ingrediente("Arroz con leche", "Canela")  # intermedio
    s.eliminar_ingrediente("Arroz con leche", "Arroz")   # primer nodo
    s.eliminar_ingrediente("Arroz con leche", "Pasas")   # no existe
    s.eliminar_ingrediente("Arroz con leche", "Leche")   # último nodo -> lista vacía
    s.eliminar_ingrediente("Arroz con leche", "Leche")   # lista ya vacía
    s.eliminar_ingrediente("Tiramisú", "Café")           # postre inexistente
    s.mostrar()

    print("\n=== PUNTO 2: ELIMINAR REPETIDOS ===")
    # Se fuerzan repetidos (permitir_repetido=True) para poder probar el subprograma
    s.alta_postre("Flan", ["Agua", "Caramelo"], permitir_repetido=True)
    s.alta_postre("Flan", ["Huevos", "Sal"], permitir_repetido=True)
    s.mostrar()

    print("\n--- Versión INCORRECTA (for + del) ---")
    copia = SistemaPostres()
    for p in s.POSTRES:
        copia.POSTRES.append(p)
    try:
        copia.eliminar_repetidos_incorrecto()
    except IndexError as e:
        print(f"[ERROR] IndexError: {e}")
        print("        El 'for' siguió con el tamaño original, pero el arreglo ya se había encogido.")

    print("\n--- Versión CORRECTA (while + índice manual) ---")
    del copia        # soltamos la copia de demostración (si no, sigue referenciando nodos)
    refs = s.eliminar_repetidos(fusionar=True)
    s.mostrar()

    gc.collect()
    print("\n¿Qué pasó con las listas de los repetidos eliminados?")
    for r in refs:
        print("  Lista liberada por el recolector de basura:", r() is None)

    print("\n=== INCISO E: BAJA ===")
    s.baja_postre("flan")
    s.baja_postre("Flan")                            # ya no existe
    s.mostrar()
