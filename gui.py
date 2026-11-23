import tkinter as tk
from tkinter import ttk, messagebox

from board import EMPTY, HUMAN, AI, create_board, copy_board, valid_columns, drop_piece, is_full, count_fours, board_to_text
from heuristic import heuristic
from agent import choose_move
from expectiminimax import real_drop
from tree_print import fmt_value, node_label, print_tree
from tree_window import TreeWindow


class Connect4App:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4 - Minimax Agent")
        self.frame = None
        self.show_setup()

    def show_setup(self):
        if self.frame is not None:
            self.frame.destroy()
        self.frame = tk.Frame(self.root, padx=30, pady=20)
        self.frame.pack()
        tk.Label(self.frame, text="Connect 4", font=("Arial", 22, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        self.rows_var = tk.IntVar(value=6)
        self.cols_var = tk.IntVar(value=7)
        self.k_var = tk.IntVar(value=4)
        self.algo_var = tk.StringVar(value="alphabeta")
        self.first_var = tk.StringVar(value="human")
        tk.Label(self.frame, text="Rows (>= 6):").grid(row=1, column=0, sticky="w", pady=3)
        tk.Spinbox(self.frame, from_=6, to=12, textvariable=self.rows_var, width=6).grid(row=1, column=1, sticky="w")
        tk.Label(self.frame, text="Columns (>= 7):").grid(row=2, column=0, sticky="w", pady=3)
        tk.Spinbox(self.frame, from_=7, to=14, textvariable=self.cols_var, width=6).grid(row=2, column=1, sticky="w")
        tk.Label(self.frame, text="Depth K:").grid(row=3, column=0, sticky="w", pady=3)
        tk.Spinbox(self.frame, from_=1, to=10, textvariable=self.k_var, width=6).grid(row=3, column=1, sticky="w")
        tk.Label(self.frame, text="Algorithm:").grid(row=4, column=0, sticky="nw", pady=3)
        algo_frame = tk.Frame(self.frame)
        algo_frame.grid(row=4, column=1, sticky="w")
        tk.Radiobutton(algo_frame, text="Minimax without alpha-beta", variable=self.algo_var, value="minimax").pack(anchor="w")
        tk.Radiobutton(algo_frame, text="Minimax with alpha-beta", variable=self.algo_var, value="alphabeta").pack(anchor="w")
        tk.Radiobutton(algo_frame, text="Expectiminimax", variable=self.algo_var, value="expectiminimax").pack(anchor="w")
        tk.Label(self.frame, text="First player:").grid(row=5, column=0, sticky="nw", pady=3)
        first_frame = tk.Frame(self.frame)
        first_frame.grid(row=5, column=1, sticky="w")
        tk.Radiobutton(first_frame, text="Human (Red)", variable=self.first_var, value="human").pack(anchor="w")
        tk.Radiobutton(first_frame, text="Computer (Yellow)", variable=self.first_var, value="ai").pack(anchor="w")
        tk.Button(self.frame, text="Start Game", width=15, command=self.start_game).grid(row=6, column=0, columnspan=2, pady=15)

    def start_game(self):
        try:
            rows = self.rows_var.get()
            cols = self.cols_var.get()
            k = self.k_var.get()
        except tk.TclError:
            messagebox.showerror("Error", "Please enter valid numbers")
            return
        if rows < 6 or cols < 7 or k < 1:
            messagebox.showerror("Error", "Rows must be >= 6, columns >= 7 and K >= 1")
            return
        self.rows = rows
        self.cols = cols
        self.k = k
        self.algorithm = self.algo_var.get()
        self.board = create_board(rows, cols)
        self.last_root = None
        self.history = []
        self.column_values = {}
        self.game_over = False
        self.busy = False
        self.cell = min(80, 900 // cols, 560 // rows)
        self.top = 55
        self.frame.destroy()
        self.frame = tk.Frame(self.root, padx=10, pady=10)
        self.frame.pack()
        names = {"minimax": "Minimax", "alphabeta": "Alpha-Beta", "expectiminimax": "Expectiminimax"}
        tk.Label(self.frame, text=f"{names[self.algorithm]}   |   K = {k}   |   {rows} x {cols}", font=("Arial", 12, "bold")).pack()
        self.score_label = tk.Label(self.frame, font=("Arial", 12))
        self.score_label.pack(pady=3)
        self.canvas = tk.Canvas(self.frame, width=cols * self.cell, height=self.top + rows * self.cell, bg="white", highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)
        self.status = tk.Label(self.frame, text="Your turn", font=("Arial", 11))
        self.status.pack(pady=3)
        self.info = tk.Label(self.frame, text="", font=("Arial", 10), fg="#555")
        self.info.pack()
        buttons = tk.Frame(self.frame)
        buttons.pack(pady=5)
        tk.Button(buttons, text="Tree (Graph)", width=12, command=self.show_tree_graph).pack(side="left", padx=5)
        tk.Button(buttons, text="Tree (List)", width=12, command=self.show_tree).pack(side="left", padx=5)
        tk.Button(buttons, text="New Game", width=12, command=self.show_setup).pack(side="left", padx=5)
        self.update_scores()
        self.draw_board()
        print("=" * 60)
        print(f"New game: {rows}x{cols}, algorithm = {self.algorithm}, K = {k}")
        print("=" * 60)
        if self.first_var.get() == "ai":
            self.busy = True
            self.status.config(text="Computer is thinking...")
            self.root.after(300, self.ai_turn)

    def draw_board(self):
        self.canvas.delete("all")
        cell = self.cell
        self.canvas.create_rectangle(0, self.top, self.cols * cell, self.top + self.rows * cell, fill="#1f5fd6", outline="")
        colors = {EMPTY: "white", HUMAN: "#e02424", AI: "#f5c400"}
        for c in range(self.cols):
            x = c * cell + cell // 2
            self.canvas.create_text(x, 14, text=str(c), font=("Arial", 11, "bold"))
            if c in self.column_values:
                self.canvas.create_text(x, 38, text=fmt_value(self.column_values[c]), font=("Arial", 9), fill="#333")
            for r in range(self.rows):
                y = self.top + r * cell
                pad = cell // 10
                self.canvas.create_oval(c * cell + pad, y + pad, (c + 1) * cell - pad, y + cell - pad, fill=colors[self.board[r][c]], outline="#123c8a", width=2)

    def update_scores(self):
        human = count_fours(self.board, HUMAN)
        ai = count_fours(self.board, AI)
        self.score_label.config(text=f"You (Red): {human}     Computer (Yellow): {ai}")

    def on_click(self, event):
        if self.busy or self.game_over:
            return
        col = event.x // self.cell
        if col not in valid_columns(self.board):
            return
        msg = self.play(col, HUMAN)
        print(msg)
        if not self.game_over:
            self.busy = True
            self.status.config(text="Computer is thinking...")
            self.root.after(50, self.ai_turn)

    def play(self, col, piece):
        real = col
        if self.algorithm == "expectiminimax":
            real = real_drop(self.board, col)
        self.last_real = real
        self.board = drop_piece(self.board, real, piece)
        who = "You" if piece == HUMAN else "Computer"
        msg = f"{who} chose column {col}"
        if real != col:
            msg += f", but the disc fell in column {real}"
        self.update_scores()
        self.draw_board()
        self.status.config(text=msg)
        if is_full(self.board):
            self.end_game()
        return msg

    def ai_turn(self):
        print()
        print("-" * 60)
        print(f"Computer turn ({self.algorithm}, K = {self.k})")
        print("Board before move:")
        print(board_to_text(self.board))
        print(f"Heuristic of current board: {fmt_value(heuristic(self.board))}")
        col, root, nodes, elapsed = choose_move(self.board, self.algorithm, self.k)
        self.last_root = root
        board_before = copy_board(self.board)
        self.column_values = {child.move: child.value for child in root.children if child.value is not None}
        print()
        print("Minimax tree:")
        print_tree(root)
        print()
        print("Values of each column after applying the heuristic:")
        for c in sorted(self.column_values):
            print(f"  column {c}: {fmt_value(self.column_values[c])}")
        print(f"Chosen column: {col}   nodes expanded: {nodes}   time: {elapsed:.4f} s")
        self.busy = False
        msg = self.play(col, AI)
        self.history.append({
            "root": root,
            "nodes": nodes,
            "time": elapsed,
            "board": board_before,
            "col": col,
            "real": self.last_real,
            "human_score": count_fours(self.board, HUMAN),
            "ai_score": count_fours(self.board, AI),
        })
        print(msg)
        print("Board after move:")
        print(board_to_text(self.board))
        h = heuristic(self.board)
        print(f"Heuristic of board after move: {fmt_value(h)}")
        print(f"Score -> Human: {count_fours(self.board, HUMAN)}  Computer: {count_fours(self.board, AI)}")
        self.info.config(text=f"Last AI move: nodes = {nodes}, time = {elapsed:.3f} s, board heuristic = {fmt_value(h)}")
        if not self.game_over:
            self.status.config(text=msg + "   -   Your turn")

    def end_game(self):
        self.game_over = True
        human = count_fours(self.board, HUMAN)
        ai = count_fours(self.board, AI)
        if human > ai:
            result = "You win!"
        elif ai > human:
            result = "Computer wins!"
        else:
            result = "It's a draw!"
        text = f"{result}\nYou: {human}   Computer: {ai}"
        self.status.config(text=result + "   -   press 'Tree (Graph)' to replay every computer move")
        print()
        print("GAME OVER - " + text.replace("\n", " | "))
        messagebox.showinfo("Game Over", text + "\n\nPress 'Tree (Graph)' to see the search tree of every computer move in this game.")

    def show_tree_graph(self):
        if not self.history:
            messagebox.showinfo("Tree", "The computer has not played yet")
            return
        TreeWindow(self.root, self.history, len(self.history) - 1)

    def show_tree(self):
        if not self.history:
            messagebox.showinfo("Tree", "The computer has not played yet")
            return
        win = tk.Toplevel(self.root)
        win.title("Minimax Trees (all computer moves)")
        win.geometry("650x500")
        tree = ttk.Treeview(win)
        tree.heading("#0", text="Node  (click the arrows to expand)")
        scroll = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        items = {}

        def add_item(parent, node):
            iid = tree.insert(parent, "end", text=node_label(node))
            items[iid] = node
            if node.children:
                tree.insert(iid, "end", text="...")
            return iid

        def expand(iid):
            children = tree.get_children(iid)
            if len(children) == 1 and children[0] not in items:
                tree.delete(children[0])
                for child in items[iid].children:
                    add_item(iid, child)

        def on_open(event):
            expand(tree.focus())

        for i, entry in enumerate(self.history):
            move_id = tree.insert("", "end", text=f"Computer move {i + 1}: chose column {entry['col']}, nodes = {entry['nodes']}, time = {entry['time']:.4f} s")
            root_id = add_item(move_id, entry["root"])
            expand(root_id)
            tree.item(root_id, open=True)
            if i == len(self.history) - 1:
                tree.item(move_id, open=True)
                tree.see(root_id)
        tree.bind("<<TreeviewOpen>>", on_open)
