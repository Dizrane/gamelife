import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from game_model import GameModel
from life_file import LifeFileIO


class GameOfLifeGUI:
    """Tkinter-интерфейс игры «Жизнь».

    Класс отвечает только за презентацию и пользовательский ввод.
    Вся игровая логика делегирована GameModel,
    файловые операции — LifeFileIO.
    """

    MIN_CELL_SIZE = 5
    DEFAULT_CELL_SIZE = 20
    DEFAULT_DELAY_MS = 100
    DEFAULT_SPEED = 10
    GRID_COLOR = "#333333"
    ALIVE_COLOR = "#00FF00"
    BG_COLOR = "black"

    def __init__(self):
        self._model = GameModel()
        self._cell_size = self.DEFAULT_CELL_SIZE
        self._update_delay = self.DEFAULT_DELAY_MS
        self._is_running = False
        self._animation_id = None

        self._root = tk.Tk()
        self._root.title("Game of Life - Conway's Game")
        self._root.geometry("1200x900")

        self._build_ui()
        self._bind_events()
        self._draw_grid()

    # ---------- UI construction ----------

    def _build_ui(self) -> None:
        self._build_toolbar()
        self._build_speed_panel()
        self._build_stats_panel()
        self._build_canvas()

    def _build_toolbar(self) -> None:
        frame = ttk.Frame(self._root)
        frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        buttons = [
            ("▶ Старт", self._start_game),
            ("⏸ Стоп", self._stop_game),
            ("⏩ Шаг", self._next_step),
            ("🗑 Очистить", self._clear_field),
            ("🎲 Случайно", self._random_fill),
            ("💾 Сохранить", self._save_to_file),
            ("📂 Загрузить", self._load_from_file),
            ("🔄 Сброс", self._reset_game),
        ]
        for text, command in buttons:
            ttk.Button(frame, text=text, command=command).pack(side=tk.LEFT, padx=2)

    def _build_speed_panel(self) -> None:
        frame = ttk.Frame(self._root)
        frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(frame, text="Скорость:").pack(side=tk.LEFT, padx=5)
        self._speed_var = tk.IntVar(value=self.DEFAULT_SPEED)
        scale = ttk.Scale(
            frame, from_=1, to=20, orient=tk.HORIZONTAL,
            variable=self._speed_var, command=self._change_speed,
        )
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self._speed_label = ttk.Label(frame, text=f"{self._update_delay} мс")
        self._speed_label.pack(side=tk.LEFT, padx=5)

    def _build_stats_panel(self) -> None:
        frame = ttk.Frame(self._root)
        frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self._name_label = ttk.Label(frame, text=f"Имя: {self._model.name}")
        self._name_label.pack(side=tk.LEFT, padx=10)

        self._iteration_label = ttk.Label(frame, text="Итерация: 0")
        self._iteration_label.pack(side=tk.LEFT, padx=10)

        self._alive_label = ttk.Label(frame, text="Живых клеток: 0")
        self._alive_label.pack(side=tk.LEFT, padx=10)

        self._rule_label = ttk.Label(frame, text=f"Правило: {self._model.rule.to_string()}")
        self._rule_label.pack(side=tk.LEFT, padx=10)

    def _build_canvas(self) -> None:
        canvas_frame = ttk.Frame(self._root)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._canvas = tk.Canvas(canvas_frame, bg=self.BG_COLOR, highlightthickness=0)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ---------- Event bindings ----------

    def _bind_events(self) -> None:
        self._canvas.bind("<Configure>", self._on_canvas_resize)
        self._canvas.bind("<Button-1>", self._on_cell_click)
        self._canvas.bind("<B1-Motion>", self._on_cell_drag)

        self._root.bind("<space>", lambda e: self._toggle_game())
        self._root.bind("<Right>", lambda e: self._next_step())
        self._root.bind("<c>", lambda e: self._clear_field())
        self._root.bind("<r>", lambda e: self._random_fill())
        self._root.bind("<s>", lambda e: self._save_to_file())
        self._root.bind("<l>", lambda e: self._load_from_file())
        self._root.bind("<F11>", self._toggle_fullscreen)

    # ---------- Layout ----------

    def _on_canvas_resize(self, _event) -> None:
        self._recalculate_cell_size()
        self._draw_grid()

    def _recalculate_cell_size(self) -> None:
        size = self._model.size
        canvas_w = self._canvas.winfo_width()
        canvas_h = self._canvas.winfo_height()
        if canvas_w > 1 and canvas_h > 1:
            self._cell_size = max(
                self.MIN_CELL_SIZE,
                min(canvas_w // size, canvas_h // size),
            )

    def _toggle_fullscreen(self, _event=None) -> None:
        is_full = self._root.attributes("-fullscreen")
        self._root.attributes("-fullscreen", not is_full)

    # ---------- Drawing ----------

    def _draw_grid(self) -> None:
        self._canvas.delete("all")
        size = self._model.size
        cell = self._cell_size
        total = size * cell

        for i in range(size + 1):
            self._canvas.create_line(i * cell, 0, i * cell, total, fill=self.GRID_COLOR)
            self._canvas.create_line(0, i * cell, total, i * cell, fill=self.GRID_COLOR)

        for row, col in self._model.alive_cells():
            x1 = col * cell
            y1 = row * cell
            self._canvas.create_rectangle(
                x1, y1, x1 + cell - 1, y1 + cell - 1,
                fill=self.ALIVE_COLOR, outline="",
            )

        self._update_stats()

    def _update_stats(self) -> None:
        self._iteration_label.config(text=f"Итерация: {self._model.iteration}")
        self._alive_label.config(text=f"Живых клеток: {self._model.alive_count()}")
        self._name_label.config(text=f"Имя: {self._model.name}")
        self._rule_label.config(text=f"Правило: {self._model.rule.to_string()}")

    # ---------- Mouse input ----------

    def _on_cell_click(self, event) -> None:
        col = int(self._canvas.canvasx(event.x) // self._cell_size)
        row = int(self._canvas.canvasy(event.y) // self._cell_size)
        size = self._model.size
        if 0 <= row < size and 0 <= col < size:
            self._model.toggle_cell(row, col)
            self._draw_grid()

    def _on_cell_drag(self, event) -> None:
        self._on_cell_click(event)

    # ---------- Simulation control ----------

    def _start_game(self) -> None:
        if not self._is_running:
            self._is_running = True
            self._animate()

    def _stop_game(self) -> None:
        self._is_running = False
        if self._animation_id is not None:
            self._root.after_cancel(self._animation_id)
            self._animation_id = None

    def _toggle_game(self) -> None:
        if self._is_running:
            self._stop_game()
        else:
            self._start_game()

    def _next_step(self) -> None:
        self._model.compute_iteration()
        self._draw_grid()

    def _animate(self) -> None:
        if not self._is_running:
            return
        self._model.compute_iteration()
        self._draw_grid()
        self._animation_id = self._root.after(self._update_delay, self._animate)

    def _change_speed(self, value) -> None:
        speed = max(1, int(float(value)))
        self._update_delay = max(1, int(1000 / speed))
        self._speed_label.config(text=f"{self._update_delay} мс")

    # ---------- Field actions ----------

    def _clear_field(self) -> None:
        self._model.clear()
        self._draw_grid()

    def _random_fill(self) -> None:
        self._model.randomize()
        self._draw_grid()

    def _reset_game(self) -> None:
        self._stop_game()
        self._model = GameModel()
        self._draw_grid()

    # ---------- File I/O ----------

    def _save_to_file(self) -> None:
        filename = filedialog.asksaveasfilename(
            defaultextension=".cells",
            filetypes=[("Life files", "*.cells"), ("All files", "*.*")],
        )
        if not filename:
            return
        try:
            LifeFileIO.save(self._model, filename)
            messagebox.showinfo("Успех", f"Сохранено в {filename}")
        except OSError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def _load_from_file(self) -> None:
        filename = filedialog.askopenfilename(
            filetypes=[("Life files", "*.cells"), ("All files", "*.*")],
        )
        if not filename:
            return
        try:
            self._stop_game()
            self._model = LifeFileIO.load(filename)
            self._draw_grid()
            messagebox.showinfo("Успех", f"Загружено из {filename}")
        except (OSError, ValueError) as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

    # ---------- Public ----------

    def run(self) -> None:
        self._root.mainloop()


if __name__ == "__main__":
    GameOfLifeGUI().run()
