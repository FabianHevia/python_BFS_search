'''

Python BFS search environment

Creado por Fabián Hevia

'''

import random
import tkinter as tk
from typing import Tuple, List, Dict, Iterator, Optional, Any
from tkinter import ttk

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

        self.playing = True

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
            # Movimiento horizontal
            if ac + 1 == bc:
                # b está a la derecha de a
                self.cells[a]["wall_right"] = False
                self.cells[b]["wall_left"] = False
            elif ac - 1 == bc:
                # b está a la izquierda de a
                self.cells[a]["wall_left"] = False
                self.cells[b]["wall_right"] = False

        elif ac == bc:
            # Movimiento vertical
            if ar + 1 == br:
                # b está abajo de a
                self.cells[a]["wall_down"] = False
                self.cells[b]["wall_up"] = False
            elif ar - 1 == br:
                # b está arriba de a
                self.cells[a]["wall_up"] = False
                self.cells[b]["wall_down"] = False

        else:
            # No adyacentes, entonces no hace nada
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

# Visualizador del Grid
class MainWindow(tk.Tk):
    def __init__(self, n):
        super().__init__()
        self.title("Python BFS search environment")
        self.geometry("900x700")

        # Estados Runtime
        self.GRID_ROWS = n
        self.PADDING = n
        self.CELL_PX = 0

        self.grid = None  # Se asigna durante la ejeción
        self.gen: Optional[Iterator] = None
        self.playing: bool = False
        self.after_id: Optional[Any] = None
        self.delay_ms: int = 100
        self.draw_items: Dict[str, int] = {}
        self.BATCH_SIZE = 10

        # UI
        self.setup_ui()
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.status_label.config(text="Estado: Ingrese semilla y genere laberinto.")

    # UI setup
    def setup_ui(self):

        # Espacio principal para las acciones dentro del canvas
        self.control_frame = tk.Frame(self, bg="#f0f0f0", pady=6)
        self.control_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(self.control_frame, text="Tamaño (n):").pack(side=tk.LEFT, padx=4)
        self.size_spin = tk.Spinbox(self.control_frame, from_=3, to=200, width=5, command=self.on_size_change)
        self.size_spin.delete(0, "end")
        self.size_spin.insert(0, str(self.GRID_ROWS))
        self.size_spin.pack(side=tk.LEFT, padx=4)

        # Importamos la semilla
        tk.Label(self.control_frame, text="Semilla:").pack(side=tk.LEFT, padx=4)
        self.seed_entry = tk.Entry(self.control_frame, width=10)
        self.seed_entry.pack(side=tk.LEFT, padx=4)

        # Boton para regenerar el grid
        self.btn_generate = tk.Button(self.control_frame, text="Generar Nuevo", command=self.on_generate)
        self.btn_generate.pack(side=tk.LEFT, padx=6)

        # Botones que controlan la ejecución
        self.btn_play = tk.Button(self.control_frame, text="Play", command=self.on_play)
        self.btn_play.pack(side=tk.LEFT, padx=6)
        self.btn_pause = tk.Button(self.control_frame, text="Pause", command=self.on_pause)
        self.btn_pause.pack(side=tk.LEFT, padx=6)
        self.btn_step = tk.Button(self.control_frame, text="Step", command=self.on_step)
        self.btn_step.pack(side=tk.LEFT, padx=6)
        self.btn_reset = tk.Button(self.control_frame, text="Reset", command=self.on_reset)
        self.btn_reset.pack(side=tk.LEFT, padx=6)

        tk.Label(self.control_frame, text="Velocidad:").pack(side=tk.LEFT, padx=4)
        self.speed_slider = tk.Scale(self.control_frame, from_=1, to=200, orient=tk.HORIZONTAL, command=self.on_speed_change)
        self.speed_slider.set(100)
        self.speed_slider.pack(side=tk.LEFT, padx=6)

        # Canvas del contenido principal
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Status
        self.status_label = tk.Label(self, text="Estado: ...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    # Handlers
    def on_size_change(self):
        try:
            v = int(self.size_spin.get())
            self.GRID_ROWS = max(3, v)
        except Exception:
            pass

    def on_speed_change(self, val):
        try:
            v = int(val)
            self.delay_ms = max(1, int(1000 * (1 - v / 200)))
        except Exception:
            self.delay_ms = 100

    def on_canvas_configure(self, event):
        # Recalcular tamaño de las celdas y redesenerizar
        width = event.width
        height = event.height
        size_px = min(width, height) - 2 * self.PADDING
        self.CELL_PX = max(4, size_px // self.GRID_ROWS)
        self.draw_grid()  # redibuja según self.grid (si existe)

    # ---------------- Generación / control ----------------
    def on_generate(self):

        # Reset visual y estado
        self.on_reset()

        # Leer el tamaño y semilla del grid
        try:
            n = int(self.size_spin.get())
        except Exception:
            n = self.GRID_ROWS
        self.GRID_ROWS = n

        seed_text = self.seed_entry.get().strip()
        seed_val: Optional[int] = None
        if seed_text != "":
            try:
                seed_val = int(seed_text)
            except ValueError:
                # si no es entero, optar por None (aleatorio) o hash
                seed_val = abs(hash(seed_text)) & 0x7FFFFFFF

        # Crea el modelo
        self.grid = Grid(self.GRID_ROWS)

        # Dibuja la malla base (todas las paredes)
        self.draw_grid()

        # Obtener el generator del grid (yield_events=True)
        self.gen = self.grid.recursive_backtracker(seed=seed_val, yield_events=True)
        self.status_label.config(text=f"Generador listo. Semilla: {seed_text or 'None'}")

    def on_play(self):
        if self.gen is None:
            self.status_label.config(text="Error: Primero genere un laberinto.")
            return
        if not self.playing:
            self.playing = True
            self.status_label.config(text="Estado: Corriendo simulación.")
            self._schedule_next()

    def _schedule_next(self):
        if self.playing and self.gen is not None:
            self.after_id = self.after(self.delay_ms, self._batch_consume)

    def _batch_consume(self):
        if self.gen is None:
            self.playing = False
            return

        try:
            for _ in range(self.BATCH_SIZE):
                ev = next(self.gen)
                self.process_event(ev)
            # todavía hay eventos
            self._schedule_next()

        except StopIteration:
            self.playing = False
            self.gen = None
            self.status_label.config(text="Estado: Generación completada.")
            self.after_id = None

    def on_step(self):
        if self.gen is None or self.playing:
            return
        try:
            ev = next(self.gen)
            self.process_event(ev)
            self.status_label.config(text="Estado: Paso individual ejecutado.")
        except StopIteration:
            self.gen = None
            self.status_label.config(text="Estado: Generación completada (último paso).")

    def on_pause(self):
        if self.playing:
            self.playing = False
            if self.after_id is not None:
                try:
                    self.after_cancel(self.after_id)
                except Exception:
                    pass
                self.after_id = None
            self.status_label.config(text="Estado: Pausado.")

    def on_reset(self):
        self.on_pause()
        self.canvas.delete("all")
        self.draw_items = {}
        self.gen = None
        self.grid = None

    # Drawing
    def cell_to_px(self, r: int, c: int):
        x0 = self.PADDING + c * self.CELL_PX
        y0 = self.PADDING + r * self.CELL_PX
        x1 = x0 + self.CELL_PX
        y1 = y0 + self.CELL_PX
        return x0, y0, x1, y1

    def draw_grid(self):

        # Dibujar grid vacío
        self.canvas.delete("all")
        self.draw_items = {}

        if self.grid is None:
            for r in range(self.GRID_ROWS):
                for c in range(self.GRID_ROWS):
                    x0, y0, x1, y1 = self.cell_to_px(r, c)
                    rect_id = self.canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="#ddd")
                    self.draw_items[f"cell-{r}-{c}-bg"] = rect_id
            return

        for r in range(self.GRID_ROWS):
            for c in range(self.GRID_ROWS):
                x0, y0, x1, y1 = self.cell_to_px(r, c)
                rect_id = self.canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="")
                self.draw_items[f"cell-{r}-{c}-bg"] = rect_id

                # Dibujar muros en todas las direcciones
                cell = self.grid.cells[(r, c)]

                if cell.get("wall_up", True):
                    lid = self.canvas.create_line(x0, y0, x1, y0, width=2)
                    self.draw_items[f"wall-{r}-{c}-up"] = lid
                if cell.get("wall_down", True):
                    lid = self.canvas.create_line(x0, y1, x1, y1, width=2)
                    self.draw_items[f"wall-{r}-{c}-down"] = lid
                if cell.get("wall_left", True):
                    lid = self.canvas.create_line(x0, y0, x0, y1, width=2)
                    self.draw_items[f"wall-{r}-{c}-left"] = lid
                if cell.get("wall_right", True):
                    lid = self.canvas.create_line(x1, y0, x1, y1, width=2)
                    self.draw_items[f"wall-{r}-{c}-right"] = lid

        # Resaltar start y goal
        if hasattr(self.grid, "start"):
            sr, sc = self.grid.start
            if f"cell-{sr}-{sc}-bg" in self.draw_items:
                self.canvas.itemconfigure(self.draw_items[f"cell-{sr}-{sc}-bg"], fill="#58fc70")
        if hasattr(self.grid, "goal"):
            gr, gc = self.grid.goal
            if f"cell-{gr}-{gc}-bg" in self.draw_items:
                self.canvas.itemconfigure(self.draw_items[f"cell-{gr}-{gc}-bg"], fill="#ff3f3f")

    def remove_wall_visual(self, a: Cell, b: Cell):
        # Oculta el muro correspondiente entre a y b

        ar, ac = a
        br, bc = b

        if ar == br:
            if ac + 1 == bc:
                k1 = f"wall-{ar}-{ac}-right"
                k2 = f"wall-{br}-{bc}-left"
                for k in (k1, k2):
                    if k in self.draw_items:
                        try:
                            self.canvas.delete(self.draw_items[k])
                        except Exception:
                            pass
                        del self.draw_items[k]
            elif ac - 1 == bc:
                k1 = f"wall-{ar}-{ac}-left"
                k2 = f"wall-{br}-{bc}-right"
                for k in (k1, k2):
                    if k in self.draw_items:
                        try:
                            self.canvas.delete(self.draw_items[k])
                        except Exception:
                            pass
                        del self.draw_items[k]
        elif ac == bc:
            if ar + 1 == br:
                k1 = f"wall-{ar}-{ac}-down"
                k2 = f"wall-{br}-{bc}-up"
                for k in (k1, k2):
                    if k in self.draw_items:
                        try:
                            self.canvas.delete(self.draw_items[k])
                        except Exception:
                            pass
                        del self.draw_items[k]
            elif ar - 1 == br:
                k1 = f"wall-{ar}-{ac}-up"
                k2 = f"wall-{br}-{bc}-down"
                for k in (k1, k2):
                    if k in self.draw_items:
                        try:
                            self.canvas.delete(self.draw_items[k])
                        except Exception:
                            pass
                        del self.draw_items[k]

    def process_event(self, event: Dict):
        ev_type = event.get("event")

        # Resaltar start
        if ev_type == "start":
            cell = event.get("cell")

            if cell:
                r, c = cell
                key = f"cell-{r}-{c}-bg"

                if key in self.draw_items:
                    self.canvas.itemconfigure(self.draw_items[key], fill="#58fc70")

            self.status_label.config(text=f"Start carving at {event.get('cell')}")

        elif ev_type == "carve":

            a = event.get("from")
            b = event.get("to")

            if a and b:
                # Eliminar muro entre a y b
                self.remove_wall_visual(a, b)

                # Colorear la celda b como visitada
                kb = f"cell-{b[0]}-{b[1]}-bg"

                if kb in self.draw_items:
                    self.canvas.itemconfigure(self.draw_items[kb], fill="#e8f8e8")

            self.status_label.config(text=f"Carve {a} -> {b} (visited {event.get('visited_count')})")

        elif ev_type == "backtrack":
            cell = event.get("cell")

            if cell:
                kr = f"cell-{cell[0]}-{cell[1]}-bg"
                if kr in self.draw_items:
                    # color sutil para backtrack
                    self.canvas.itemconfigure(self.draw_items[kr], fill="#f6f6f6")

            self.status_label.config(text=f"Backtrack {cell}")

        elif ev_type == "done":
            self.status_label.config(text=f"Done. visited {event.get('visited_count')}")

            # Resaltar goal
            if self.grid and hasattr(self.grid, "goal"):
                gr, gc = self.grid.goal
                key = f"cell-{gr}-{gc}-bg"
                if key in self.draw_items:
                    self.canvas.itemconfigure(self.draw_items[key], fill="#ff3f3f")
        else:
            # evento desconocido (seguramente el generador cambió la forma)
            self.status_label.config(text=f"Evento desconocido: {event}")

def main():
    n = menu()
    grid = Grid(n)

    generar = grid.recursive_backtracker(seed=1234, yield_events=True)
    '''
    for environment in generar:
        print(environment)
    '''

    app = MainWindow(n)
    app.mainloop()
        
main()

