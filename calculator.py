import tkinter as tk

GAP = 12
SIDE_PAD = 16

# iPhone-size window (iPhone 15/16).
WINDOW_W = 390
WINDOW_H = 740
COLS = 4
ROWS = 5

# Square button cell that exactly fills the width with even gaps.
CELL = (WINDOW_W - 2 * SIDE_PAD - (COLS - 1) * GAP) // COLS

UTILITY_BG = "#A5A5A5"
UTILITY_FG = "#000000"
NUMBER_BG = "#333333"
NUMBER_FG = "#FFFFFF"
OP_BG = "#FF9F0A"
OP_FG = "#FFFFFF"
OP_ACTIVE_BG = "#FFFFFF"
OP_ACTIVE_FG = "#FF9F0A"

FONT = "Hanken Grotesk"


class AppleCalculator:
    def __init__(self, root):
        self.root = root
        root.title("Calculator")
        root.configure(bg="#000000")
        root.geometry(f"{WINDOW_W}x{WINDOW_H}")
        root.resizable(False, False)

        self.expression = "0"
        self.last_operand = None
        self.last_operation = None
        self.start_new_number = False
        self.op_widgets = {}
        self.canvases = []

        self.grid_w = COLS * CELL + (COLS - 1) * GAP
        self.grid_h = ROWS * CELL + (ROWS - 1) * GAP

        self._build_layout()
        self.root.after(50, self._draw_all)

    def _build_layout(self):
        # Display area at top.
        self.display = tk.Label(
            self.root,
            text="0",
            bg="#000000",
            fg="#FFFFFF",
            font=(FONT, 78),
            anchor="e",
        )
        self.display.place(x=20, y=0, relwidth=1.0, width=-40, height=WINDOW_H - self.grid_h - 16)

        # Centered button grid at bottom.
        self.grid_frame = tk.Frame(self.root, bg="#000000")
        gf_x = (WINDOW_W - self.grid_w) // 2
        gf_y = WINDOW_H - self.grid_h - 16
        self.grid_frame.place(x=gf_x, y=gf_y, width=self.grid_w, height=self.grid_h)

        rows = [
            [("AC", "utility"), ("+/-", "utility"), ("%", "utility"), ("÷", "op")],
            [("7", "number"), ("8", "number"), ("9", "number"), ("×", "op")],
            [("4", "number"), ("5", "number"), ("6", "number"), ("-", "op")],
            [("1", "number"), ("2", "number"), ("3", "number"), ("+", "op")],
            [("0", "number"), (".", "number"), ("=", "op")],
        ]

        for r, row in enumerate(rows):
            placed = 0
            for label, kind in row:
                span = 2 if label == "0" else 1
                self._make_button(self.grid_frame, label, kind, r, placed, span)
                placed += span

    def _make_button(self, parent, label, kind, r, c, span):
        canvas = tk.Canvas(
            parent,
            bg="#000000",
            highlightthickness=0,
            bd=0,
        )
        # Exact placement: each cell is CELL square with GAP between.
        w = CELL * span + (span - 1) * GAP
        x = c * (CELL + GAP)
        y = r * (CELL + GAP)
        canvas.place(x=x, y=y, width=w, height=CELL)
        canvas.bind("<Button-1>", lambda e, l=label, k=kind: self._on_press(l, k))

        self.canvases.append((canvas, label, kind))
        if kind == "op" and label != "=":
            self.op_widgets[label] = canvas

    def _draw_all(self):
        for canvas, label, kind in self.canvases:
            self._draw_button(canvas, label, kind)

    def _draw_button(self, canvas, label, kind, active=False):
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w <= 1 or h <= 1:
            return

        if label == "0":
            # Wide rounded pill filling the full cell.
            d = h          # circle diameter = cell height
            r = d / 2
            w = canvas.winfo_width()
            if w > d:
                body = w - d
                canvas.create_oval(0, 0, d, d, fill=self._bg(kind, active), outline="")
                canvas.create_oval(body, 0, body + d, d, fill=self._bg(kind, active), outline="")
                canvas.create_rectangle(r, 0, r + body, d, fill=self._bg(kind, active), outline="")
            else:
                canvas.create_oval(0, 0, d, d, fill=self._bg(kind, active), outline="")
            # "0" sits near the left like the iPhone calculator.
            canvas.create_text(
                r + d * 0.30, d / 2,
                text="0", fill=self._fg(kind, active),
                font=(FONT, int(d * 0.5)),
                anchor="w",
            )
        else:
            d = min(w, h)  # perfect circle
            off_x = (w - d) / 2
            off_y = (h - d) / 2
            canvas.create_oval(
                off_x, off_y, off_x + d, off_y + d,
                fill=self._bg(kind, active), outline="",
            )
            weight = "bold" if kind == "op" else "normal"
            font_size = int(d * 0.42)
            canvas.create_text(
                off_x + d / 2, off_y + d / 2,
                text=label, fill=self._fg(kind, active),
                font=(FONT, font_size, weight),
            )

    def _bg(self, kind, active):
        if kind == "utility":
            return UTILITY_BG
        if kind == "number":
            return NUMBER_BG
        if active:
            return OP_ACTIVE_BG
        return OP_BG

    def _fg(self, kind, active):
        if kind == "utility":
            return UTILITY_FG
        if kind == "op" and active:
            return OP_ACTIVE_FG
        return NUMBER_FG if kind == "number" else OP_FG

    def _on_press(self, label, kind):
        if kind == "op":
            self._on_operator(label)
        elif kind == "utility":
            self._on_utility(label)
        else:
            self._on_number(label)

    def _on_number(self, digit):
        if self.start_new_number:
            self.expression = "0"
            self.start_new_number = False
            self._clear_active_ops()
        if digit == ".":
            if "." in self.expression:
                return
            self.expression += "."
        else:
            if self.expression == "0":
                self.expression = digit
            else:
                self.expression += digit
        self._update_display()

    def _on_operator(self, op):
        if op == "=":
            self._calculate()
            return
        if self.last_operation is not None and not self.start_new_number:
            self._calculate()
        self.last_operand = float(self.expression) if self.expression != "Error" else 0.0
        self.last_operation = op
        self.start_new_number = True
        self._highlight_op(op)

    def _on_utility(self, label):
        if label == "AC":
            self._clear_all()
        elif label == "+/-":
            if self.expression not in ("0", "Error"):
                if self.expression.startswith("-"):
                    self.expression = self.expression[1:]
                else:
                    self.expression = "-" + self.expression
                self._update_display()
        elif label == "%":
            value = float(self.expression) / 100.0
            self.expression = self._format_number(value)
            self._update_display()

    def _calculate(self):
        if self.last_operation is None:
            return
        try:
            current = float(self.expression)
            left = self.last_operand
            op = self.last_operation
            if op == "+":
                result = left + current
            elif op == "-":
                result = left - current
            elif op == "×":
                result = left * current
            else:
                if current == 0:
                    raise ZeroDivisionError
                result = left / current
            self.expression = self._format_number(result)
        except (ValueError, OverflowError, ZeroDivisionError):
            self.expression = "Error"
        self._update_display()
        self.last_operation = None
        self.start_new_number = True
        self._clear_active_ops()

    def _clear_all(self):
        self.expression = "0"
        self.last_operand = None
        self.last_operation = None
        self.start_new_number = False
        self._clear_active_ops()
        self._update_display()

    def _format_number(self, value):
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))
        s = f"{value:.10f}".rstrip("0").rstrip(".")
        if len(s) > 16:
            s = f"{value:.6e}"
        if s == "-0":
            s = "0"
        return s

    def _update_display(self):
        text = self.expression
        size = 78
        if len(text) > 6:
            size = 64
        if len(text) > 10:
            size = 50
        if len(text) > 14:
            size = 36
        self.display.config(text=text, font=(FONT, size))

    def _clear_active_ops(self):
        for label, canvas in self.op_widgets.items():
            self._draw_button(canvas, label, "op")

    def _highlight_op(self, op):
        for label, canvas in self.op_widgets.items():
            self._draw_button(canvas, label, "op", active=(label == op))


def main():
    root = tk.Tk()
    AppleCalculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
