'''

Python BFS search environment

Creado por Fabián Hevia

'''

import random
from typing import Tuple, List, Dict, Iterator, Optional

def menu():
    print("\nBienvenido a Python BFS search environment\n")

    while True:
        entrada = input("Indica el ancho del grid (entre 3 y 200): ")
        
        # Valida que realmente sea número
        try:
            a = int(entrada)
        except ValueError:
            print("Por favor ingresa un número entero válido.")
            continue

        # Valida el rango del grid
        if 3 <= a <= 200:
            return a
        else:
            print("El número debe estar entre 3 y 200. Intenta de nuevo.")

Cell = Tuple[int, int]
Event = Dict[str, object]

class Grid:
    def __init__(self, n):

        # Crea los atributos de la clase

        self.n = n
        self.start = (0, 0)
        self.goal = (n - 1, n - 1)

        self.cells = {
            # Donde r = row, c = col
            (r, c): {
                "wall_up": True,
                "wall_down": True,
                "wall_left": True,
                "wall_right": True
            }
            for r in range(n)
            for c in range(n)
        }

    def in_bounds(self, r, c):
        # Dentro de los limites tendriamos a 0 <= row < n y 0 <= col < n
        return 0 <= r < self.n and 0 <= c < self.n

    def neighbors(self, r, c):
        # Representamos posibles con las 4 posiciones posibles
        posibles = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        return [(rr, cc) for (rr, cc) in posibles if self.in_bounds(rr, cc)]
    
    def remove_wall(self, a: Cell, b: Cell) -> None:
        (ar, ac), (br, bc) = a, b
        if ar == br:
            # movimiento horizontal
            if ac + 1 == bc:
                # b está a la derecha de a
                self.cells[a]["wall_right"] = False
                self.cells[b]["wall_left"] = False
            elif ac - 1 == bc:
                # b está a la izquierda de a
                self.cells[a]["wall_left"] = False
                self.cells[b]["wall_right"] = False
        elif ac == bc:
            # movimiento vertical
            if ar + 1 == br:
                # b está abajo de a
                self.cells[a]["wall_down"] = False
                self.cells[b]["wall_up"] = False
            elif ar - 1 == br:
                # b está arriba de a
                self.cells[a]["wall_up"] = False
                self.cells[b]["wall_down"] = False
        else:
            # no adyacentes — no hacemos nada
            pass
    
    def recursive_backtracker(self, seed: Optional[int] = None, yield_events: bool = False) -> Optional[Iterator[Event]]:
        """
        Genera un laberinto usando recursive backtracker (DFS con stack).
        Si yield_events == True, devuelve un iterador (generator) que
        emite eventos dict por cada carve/backtrack.
        Si yield_events == False, simplemente ejecuta la generación y retorna None.
        """

        rng = random.Random(seed)

        visited = set()
        stack: List[Cell] = [self.start]
        visited.add(self.start)

        # Si queremos yieldear eventos, definimos el generator
        def generator():
            # Evento inicial opcional
            yield {"event": "start", "cell": self.start, "visited_count": len(visited), "stack_depth": len(stack)}

            while stack:
                current = stack[-1]
                r, c = current

                # Vecinos que aún no han sido visitados
                nbrs = [nb for nb in self.neighbors(r, c) if nb not in visited]

                if nbrs:
                    chosen = rng.choice(nbrs)
                    self.remove_wall(current, chosen)
                    visited.add(chosen)
                    stack.append(chosen)

                    # Emitir evento de carve
                    yield {
                        "event": "carve",
                        "from": current,
                        "to": chosen,
                        "visited_count": len(visited),
                        "stack_depth": len(stack)
                    }
                else:
                    # Backtrack
                    popped = stack.pop()
                    yield {
                        "event": "backtrack",
                        "cell": popped,
                        "visited_count": len(visited),
                        "stack_depth": len(stack)
                    }

            yield {"event": "done", "visited_count": len(visited), "stack_depth": 0}

        if yield_events:
            return generator()
        else:
            for _ in generator():
                pass
            return None

def main():
    n = menu()
    grid = Grid(n)

    generar = grid.recursive_backtracker(seed=1234, yield_events=True)
    for environment in generar:
        print(environment)
main()

