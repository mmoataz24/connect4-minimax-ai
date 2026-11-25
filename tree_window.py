import tkinter as tk
from tkinter import ttk

from board import EMPTY, HUMAN, AI, next_open_row
from heuristic import heuristic
from tree_print import fmt_value


SLOT = 64
LEVEL = 100


class TreeWindow:
    def __init__(self, master, history, index):
        self.history = history
        self.index = index
        self.step = 1
        self.total = 1
        self.playing = False
        self.node_at = {}
        self.expanded = set()
        self.best_path = set()
        self.win = tk.Toplevel(master)
        self.win.title("Search Tree Visualization")
        self.win.geometry("1300x720")
        moves_bar = tk.Frame(self.win)
        moves_bar.pack(fill="x", padx=8, pady=(6, 0))
        tk.Button(moves_bar, text="<<  Previous computer move", command=lambda: self.load_turn(self.index - 1)).pack(side="left", padx=2)
        tk.Button(moves_bar, text="Next computer move  >>", command=lambda: self.load_turn(self.index + 1)).pack(side="left", padx=2)
        self.turn_label = tk.Label(moves_bar, font=("Arial", 11, "bold"), fg="#7a3e00")
        self.turn_label.pack(side="left", padx=12)
        controls = tk.Frame(self.win)
        controls.pack(fill="x", padx=8, pady=5)
        tk.Button(controls, text="|<  First", command=lambda: self.go_to(1)).pack(side="left", padx=2)
        tk.Button(controls, text="<  Back", command=lambda: self.go_to(self.step - 1)).pack(side="left", padx=2)
        self.play_btn = tk.Button(controls, text="Play", width=6, command=self.toggle_play)
        self.play_btn.pack(side="left", padx=2)
        tk.Button(controls, text="Next  >", command=lambda: self.go_to(self.step + 1)).pack(side="left", padx=2)
        tk.Button(controls, text="Last  >|", command=lambda: self.go_to(self.total)).pack(side="left", padx=2)
        tk.Label(controls, text="  Speed (ms):").pack(side="left")
        self.speed_var = tk.IntVar(value=400)
        tk.Spinbox(controls, from_=50, to=2000, increment=50, textvariable=self.speed_var, width=6).pack(side="left")
        tk.Button(controls, text="Show chosen path only", command=self.reset_view).pack(side="right", padx=2)
        tk.Button(controls, text="Collapse all", command=self.collapse_all).pack(side="right", padx=2)
        self.step_var = tk.IntVar(value=self.step)
        self.scale = tk.Scale(self.win, from_=1, to=self.total, orient="horizontal", variable=self.step_var, command=self.on_scale, showvalue=False)
        self.scale.pack(fill="x", padx=8)
        self.step_label = tk.Label(self.win, font=("Arial", 11, "bold"), anchor="w")
        self.step_label.pack(fill="x", padx=8)
        self.result_label = tk.Label(self.win, font=("Arial", 10), anchor="w", fg="#1d4ed8")
        self.result_label.pack(fill="x", padx=8)
        legend = "▲ MAX (computer)     ▼ MIN (human)     ● CHANCE     ■ LEAF (heuristic)     gray X = pruned (cut)     blue = kept / chosen path     orange = current step     ? = not finished yet     click a node to expand / collapse"
        tk.Label(self.win, text=legend, font=("Arial", 9), fg="#444", anchor="w").pack(fill="x", padx=8, pady=3)
        body = tk.Frame(self.win)
        body.pack(fill="both", expand=True)
        side = tk.Frame(body, width=270, padx=6)
        side.pack(side="left", fill="y")
        tk.Label(side, text="All computer moves in this game", font=("Arial", 10, "bold")).pack(anchor="w")
        list_frame = tk.Frame(side)
        list_frame.pack(fill="x")
        self.moves_list = tk.Listbox(list_frame, height=10, width=40, exportselection=False, font=("Consolas", 9))
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.moves_list.yview)
        self.moves_list.configure(yscrollcommand=list_scroll.set)
        list_scroll.pack(side="right", fill="y")
        self.moves_list.pack(side="left", fill="x")
        for i, entry in enumerate(history):
            fell = "" if entry["real"] == entry["col"] else f"->{entry['real']}"
            self.moves_list.insert("end", f"Move {i + 1:>2}: col {entry['col']}{fell}  v={fmt_value(entry['root'].value)}  n={entry['nodes']}")
        self.moves_list.bind("<<ListboxSelect>>", self.on_select_move)
        tk.Label(side, text="Board before this move", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
        self.mini = tk.Canvas(side, width=250, height=230, bg="white", highlightthickness=0)
        self.mini.pack(anchor="w")
        self.move_info = tk.Label(side, justify="left", anchor="w", font=("Arial", 9))
        self.move_info.pack(anchor="w", fill="x")
        frame = tk.Frame(body)
        frame.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(frame, bg="white")
        xs = ttk.Scrollbar(frame, orient="horizontal", command=self.canvas.xview)
        ys = ttk.Scrollbar(frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=xs.set, yscrollcommand=ys.set)
        xs.pack(side="bottom", fill="x")
        ys.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        self.canvas.bind("<Shift-MouseWheel>", lambda e: self.canvas.xview_scroll(-1 * (e.delta // 120), "units"))
        self.win.update_idletasks()
        self.load_turn(index)

    def load_turn(self, index):
        if index < 0 or index >= len(self.history):
            return
        self.playing = False
        self.play_btn.config(text="Play")
        self.index = index
        entry = self.history[index]
        self.root_node = entry["root"]
        self.steps = self.root_node.steps
        self.total = len(self.steps)
        self.step = self.total
        self.nodes_count = entry["nodes"]
        self.expanded = set()
        self.best_path = set()
        self.mark_best_path()
        self.scale.config(to=self.total)
        self.step_var.set(self.step)
        self.moves_list.selection_clear(0, "end")
        self.moves_list.selection_set(index)
        self.moves_list.see(index)
        self.turn_label.config(text=f"Computer move {index + 1} of {len(self.history)}")
        self.win.title(f"Search Tree - computer move {index + 1} of {len(self.history)}")
        self.draw_mini_board(entry)
        self.draw(scroll_to=self.root_node)

    def on_select_move(self, event):
        selected = self.moves_list.curselection()
        if selected and selected[0] != self.index:
            self.load_turn(selected[0])

    def draw_mini_board(self, entry):
        board = entry["board"]
        rows, cols = len(board), len(board[0])
        cell = min(240 // cols, 200 // rows)
        top = 22
        self.mini.delete("all")
        self.mini.create_rectangle(0, top, cols * cell, top + rows * cell, fill="#1f5fd6", outline="")
        colors = {EMPTY: "white", HUMAN: "#e02424", AI: "#f5c400"}
        landed = next_open_row(board, entry["real"])
        for c in range(cols):
            x = c * cell + cell // 2
            self.mini.create_text(x, 8, text=str(c), font=("Arial", 7))
            for r in range(rows):
                y = top + r * cell
                if r == landed and c == entry["real"]:
                    self.mini.create_oval(c * cell + 2, y + 2, (c + 1) * cell - 2, y + cell - 2, fill="#fff3b0", outline="#ff7a00", width=3)
                else:
                    self.mini.create_oval(c * cell + 2, y + 2, (c + 1) * cell - 2, y + cell - 2, fill=colors[board[r][c]], outline="#123c8a")
        x = entry["col"] * cell + cell // 2
        self.mini.create_polygon(x - 6, 12, x + 6, 12, x, 21, fill="#ff7a00")
        info = f"Heuristic before move: {fmt_value(heuristic(board))}\n"
        info += f"Computer chose column {entry['col']}"
        if entry["real"] != entry["col"]:
            info += f"\nbut the disc fell in column {entry['real']}"
        info += f"\nNodes expanded: {entry['nodes']}\nTime: {entry['time']:.4f} s"
        info += f"\nScore after move -> You: {entry['human_score']}  Computer: {entry['ai_score']}"
        self.move_info.config(text=info)

    def mark_best_path(self):
        node = self.root_node
        while node is not None:
            self.best_path.add(id(node))
            self.expanded.add(id(node))
            next_node = None
            if node.kind != "CHANCE":
                for child in node.children:
                    if child.move == node.best and not child.pruned:
                        next_node = child
                        break
            node = next_node

    def reset_view(self):
        self.expanded = set()
        self.best_path = set()
        self.mark_best_path()
        self.draw(scroll_to=self.root_node)

    def collapse_all(self):
        self.expanded = {id(self.root_node)}
        self.draw(scroll_to=self.root_node)

    def visible_children(self, node):
        if id(node) not in self.expanded:
            return []
        return [c for c in node.children if c.order <= self.step]

    def layout(self, node, depth, positions, counter):
        kids = self.visible_children(node)
        if not kids:
            x = 30 + counter[0] * SLOT + SLOT // 2
            counter[0] += 1
        else:
            for kid in kids:
                self.layout(kid, depth + 1, positions, counter)
            x = (positions[id(kids[0])][0] + positions[id(kids[-1])][0]) / 2
        positions[id(node)] = (x, 50 + depth * LEVEL)

    def draw(self, scroll_to=None):
        self.canvas.delete("all")
        self.node_at = {}
        positions = {}
        counter = [0]
        self.layout(self.root_node, 0, positions, counter)
        current = self.steps[self.step - 1]
        self.draw_node(self.root_node, positions, current)
        width = 60 + counter[0] * SLOT
        height = max(y for x, y in positions.values()) + 80
        self.canvas.config(scrollregion=(0, 0, width, height))
        self.step_label.config(text=f"Step {self.step} / {self.total}:   " + self.describe(current))
        if self.step == self.total:
            self.result_label.config(text=f"Move {self.index + 1}: search finished -> computer plays column {self.root_node.best} with value {fmt_value(self.root_node.value)}   |   nodes expanded = {self.nodes_count}")
        else:
            self.result_label.config(text="Searching...")
        if scroll_to is not None and id(scroll_to) in positions:
            x, y = positions[id(scroll_to)]
            self.canvas.update_idletasks()
            self.canvas.xview_moveto(max(0, (x - self.canvas.winfo_width() / 2) / width))
            self.canvas.yview_moveto(max(0, (y - self.canvas.winfo_height() / 2) / height))

    def draw_node(self, node, positions, current):
        x, y = positions[id(node)]
        finished = self.step == self.total
        for kid in self.visible_children(node):
            kx, ky = positions[id(kid)]
            if kid.pruned:
                self.canvas.create_line(x, y + 22, kx, ky - 22, fill="#aaaaaa", dash=(4, 3))
            elif finished and id(kid) in self.best_path and id(node) in self.best_path:
                self.canvas.create_line(x, y + 22, kx, ky - 22, fill="#1d4ed8", width=4)
            else:
                self.canvas.create_line(x, y + 22, kx, ky - 22, fill="#666666")
            label = f"c{kid.move}" if kid.prob is None else f"c{kid.move} p={kid.prob}"
            self.canvas.create_text((x + 3 * kx) / 4, (y + 3 * ky) / 4 - 6, text=label, font=("Arial", 8), fill="#7a3e00")
            self.draw_node(kid, positions, current)
        tag = f"n{len(self.node_at)}"
        self.node_at[tag] = node
        r = 20
        colors = {"MAX": "#9be29b", "MIN": "#f5a3a3", "CHANCE": "#ffe08a"}
        fill = "#d6d6d6" if node.pruned else ("#bcd7ff" if node.leaf else colors[node.kind])
        outline, width = "#333333", 1
        if finished and id(node) in self.best_path:
            outline, width = "#1d4ed8", 3
        if node is current:
            outline, width = "#ff7a00", 4
        if node.pruned or node.leaf:
            self.canvas.create_rectangle(x - r, y - r, x + r, y + r, fill=fill, outline=outline, width=width, tags=tag)
        elif node.kind == "MAX":
            self.canvas.create_polygon(x, y - r - 4, x - r - 4, y + r, x + r + 4, y + r, fill=fill, outline=outline, width=width, tags=tag)
        elif node.kind == "MIN":
            self.canvas.create_polygon(x - r - 4, y - r, x + r + 4, y - r, x, y + r + 4, fill=fill, outline=outline, width=width, tags=tag)
        else:
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline=outline, width=width, tags=tag)
        if node.pruned:
            self.canvas.create_text(x, y, text="X", font=("Arial", 14, "bold"), fill="#d00000", tags=tag)
        else:
            text = fmt_value(node.value) if node.last <= self.step else "?"
            offset = 5 if node.kind == "MAX" and not node.leaf else (-5 if node.kind == "MIN" and not node.leaf else 0)
            self.canvas.create_text(x, y + offset, text=text, font=("Arial", 8, "bold"), tags=tag)
        self.canvas.create_text(x, y + r + 12, text=f"#{node.order}", font=("Arial", 7), fill="#777777")
        if node.children and not node.pruned:
            sign = "-" if id(node) in self.expanded else "+"
            self.canvas.create_text(x + r + 10, y, text=sign, font=("Arial", 12, "bold"), fill="#1d4ed8", tags=tag)

    def describe(self, node):
        if node.parent is None:
            return "start at the root (MAX = computer to move)"
        who = "computer" if node.parent.kind == "MAX" else ("human" if node.parent.kind == "MIN" else "chance")
        if node.pruned:
            return f"PRUNED column {node.move} -> not explored because {node.note}"
        if node.kind == "CHANCE":
            text = f"{who} chooses column {node.move} -> chance node (disc may slip left / right)"
        elif node.prob is not None:
            text = f"disc falls in column {node.move} with probability {node.prob}"
        else:
            text = f"{who} tries column {node.move}"
        if node.note and not node.children:
            text += f" -> {node.note}, value = {fmt_value(node.value)}"
        elif node.leaf:
            text += f" -> depth limit reached, heuristic h = {fmt_value(node.value)}"
        elif node.kind != "CHANCE":
            text += f" -> {node.kind} node"
        return text

    def on_scale(self, value):
        value = int(float(value))
        if value != self.step:
            self.go_to(value)

    def go_to(self, step):
        self.step = max(1, min(self.total, step))
        self.step_var.set(self.step)
        node = self.steps[self.step - 1]
        parent = node.parent
        while parent is not None:
            self.expanded.add(id(parent))
            parent = parent.parent
        self.draw(scroll_to=node)

    def toggle_play(self):
        self.playing = not self.playing
        self.play_btn.config(text="Pause" if self.playing else "Play")
        if self.playing:
            if self.step >= self.total:
                self.go_to(1)
            self.auto_step()

    def auto_step(self):
        if not self.playing or not self.win.winfo_exists():
            return
        if self.step >= self.total:
            self.playing = False
            self.play_btn.config(text="Play")
            return
        self.go_to(self.step + 1)
        try:
            delay = max(20, self.speed_var.get())
        except tk.TclError:
            delay = 400
        self.win.after(delay, self.auto_step)

    def on_click(self, event):
        items = self.canvas.find_withtag("current")
        if not items:
            return
        for tag in self.canvas.gettags(items[0]):
            if tag in self.node_at:
                node = self.node_at[tag]
                if node.children and not node.pruned:
                    if id(node) in self.expanded:
                        self.expanded.discard(id(node))
                    else:
                        self.expanded.add(id(node))
                    self.draw()
                return
