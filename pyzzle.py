# Pyzzle, a program for learning programming
# David Kaméus, 2024

import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.simpledialog as simpledialog
import random
import io
import builtins
import traceback

LIST_WIDTH = 50
LIST_FONT = "Consolas"
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 400
BOX_HEIGHT = 30

# dataclass, just holds information in one place
class PyzzleDescription:
    def __init__(self, instructions, code):
        self.instructions = instructions
        self.code = code

# I'm a graphics guy, I like using vectors when possible
class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

# main class, holds most program logic
class Pyzzle:
    def __init__(self, root):
        self.root = root ; root.title("Pyzzle")
        self.root.rowconfigure(0, weight=1); self.root.columnconfigure(0, weight=1) # Makes things resize with the window
        self.init_puzzle_area()
        self.init_output()
        self.init_instructions()
        self.init_menu()
        
    def init_instructions(self):
        self.instructions_area = tk.LabelFrame(self.root, text="Instructions") ; self.instructions_area.grid(row=0, column=1, sticky=tk.NSEW)
        self.instructions = tk.Label(self.instructions_area, text="", justify=tk.LEFT, font=LIST_FONT) ; self.instructions.grid()
    
    def init_puzzle_area(self):
        self.puzzle_area = PuzzleArea(self.root)

    def init_output(self):
        self.left_side_frame = tk.Frame(self.root) ; self.left_side_frame.grid(row=1, column=1, sticky=tk.NSEW)
        self.left_side_frame.rowconfigure(0, weight=1); self.left_side_frame.columnconfigure(0, weight=1) ; self.left_side_frame.rowconfigure(1, weight=1)
        # TODO: make things resize nicely
        self.input_frame = tk.LabelFrame(self.left_side_frame, text="Input") ; self.input_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.input = tk.Listbox(self.input_frame, width=LIST_WIDTH, activestyle=tk.NONE, font=LIST_FONT) ; self.input.grid(sticky=tk.NSEW)
        
        self.compile_btn = tk.Button(self.input_frame, text="Run!", command=self.run_puzzle) ; self.compile_btn.grid(sticky=tk.NSEW)
        
        self.output_frame = tk.LabelFrame(self.left_side_frame, text="Output") ; self.output_frame.grid(row=1,column=0, sticky=tk.NSEW)
        self.output = tk.Listbox(self.output_frame, width=LIST_WIDTH, activestyle=tk.NONE, font=LIST_FONT) ; self.output.grid(sticky=tk.NSEW)

    def init_menu(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.configure(menu = self.menu_bar)
        self.menu_bar.add_command(label="File", command=self.load_puzzle)

    def load_puzzle(self):
        filename = filedialog.askopenfilename(defaultextension=".pyzzle",initialdir="./assets")
        if filename:
            description = parse_pyzzle_file(filename)
            self.instructions["text"] = description.instructions
            self.puzzle_area.set_pieces(description.code)

    def run_puzzle(self):
        # clear old input and outputs
        self.input.delete(0, tk.END)
        self.output.delete(0, tk.END)
        # get new input
        lines = self.puzzle_area.get_solution()
        for line in lines:
            self.input.insert(tk.END, line)
        code = "\n".join(lines)
        # run the gathered solution
        try:
            # now *this* is some cursed code
            log = io.StringIO()
            def myprint(*args, **kwargs):
                builtins.print(*args, file=log, **kwargs)
            # this is the hackiest hack, but wow is it simple
            def myinput(prompt):
                return simpledialog.askstring("Input", prompt)
            input = myinput
            print = myprint
            exec(compile(code, "<Canvas>", "exec")) # <> are needed here to avoid a bug in python (https://github.com/python/cpython/issues/122071)
            print = builtins.print
            out_lines = log.getvalue().split("\n")
            log.close()
            # end cursed code
        except Exception as e:
            print = builtins.print # this won't be done in try block if exec fails
            errors = traceback.format_exception(e)
            out_lines = [line for e in errors[0:1] + errors[2:] for line in e.split("\n") if line]
        finally:
            print = builtins.print
            input = builtins.input
        # show the output
        for line in out_lines:
            self.output.insert(tk.END, line)


class PuzzleArea:
    def __init__(self, root):
        self.width = CANVAS_WIDTH
        self.height = CANVAS_HEIGHT
        self.canvas_frame = tk.LabelFrame(root, text="Canvas") ; self.canvas_frame.grid(row=0, column=0, rowspan=2, sticky=tk.NSEW)
        # this makes the canvas expand when the frame grows
        self.canvas_frame.rowconfigure(0, weight=1); self.canvas_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.canvas_frame, width=self.width, height=self.height, bg="white") ; self.canvas.grid(sticky=tk.NSEW)
        self.pieces = [] # [(rect_0, text_0), (rect_1, text_1), ...]
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.clusters = []
        self.largest_cluster = []

        self.clicked_rect = None
        self.clicked_text = None
        self.click_start = Vec2(0, 0)

    # find which rectangle and text was clicked, store in instance vars
    def on_click(self, event):
        clicked_item = self.canvas.find_closest(event.x, event.y) 
        if clicked_item:
            self.click_start = Vec2(event.x, event.y)
            if "rectangle" in self.canvas.gettags(clicked_item):
                rect_id = clicked_item[0]
                self.clicked_rect = rect_id
                for r, t in self.pieces:
                    if r == rect_id:
                        self.clicked_text = t
                        break
            elif "rect_text" in self.canvas.gettags(clicked_item):
                text_id = clicked_item[0]
                self.clicked_text = text_id
                for r, t in self.pieces:
                    if t == text_id:
                        self.clicked_rect = r
                        break

    # move selected rect and text
    def on_drag(self, event):
        if self.clicked_rect and self.clicked_text:
            current = Vec2(event.x, event.y)
            delta = current - self.click_start
            self.click_start = current
            self.canvas.move(self.clicked_rect, delta.x, delta.y)
            self.canvas.move(self.clicked_text, delta.x, delta.y)
            self.update_clusters()

    # unselect rect and text
    def on_release(self, event):
        self.clicked_rect = None
        self.clicked_text = None
    
    # Set the puzzle pieces based on a piece of source code. Deletes old pieces if they exist
    def set_pieces(self, source):
        self.canvas.delete(tk.ALL)
        self.pieces = []
        self.clusters = []
        self.largest_cluster = []
        lines = source.strip().split("\n")
        for line in lines:
            if line:
                self.create_puzzle_piece(line)

    # create a puzzle piece based off a line of code and place it in a random position in the canvas
    def create_puzzle_piece(self, text):
        line_length_chars = len(text)
        line_length_pixels = line_length_chars * 10 # TODO: make more robust
        line_height_pixels = BOX_HEIGHT
        x = random.randint(0, max(self.width - line_length_pixels, 0))
        y = random.randint(0, self.height - line_height_pixels)
        padding = 5 # TODO: Make more robust
        rect_id = self.canvas.create_rectangle(x, y, x + line_length_pixels, y + line_height_pixels, fill="white", tags="rectangle")
        text_id = self.canvas.create_text(x + padding, y + line_height_pixels / 2, anchor=tk.W, text=text, tags="rect_text", font=LIST_FONT)
        self.pieces.append((rect_id, text_id))
    
    # get a list of the strings in the largest cluster of pieces, sorted from top to bottom
    def get_solution(self):
        self.update_clusters()
        lines = [self.canvas.itemcget(t, "text") for r, t in self.pieces if r in self.largest_cluster]
        return lines
    
    def update_clusters(self):
        # sort pieces from top to bottom
        self.pieces.sort(key=lambda r: self.canvas.coords(r[0])[1])# r[0] is rect_id, coords[1] is y
        # cluster pieces, mark the largest cluster green
        boxes = [(rect_id, self.canvas.coords(rect_id)) for rect_id, _ in self.pieces]
        self.clusters = cluster_boxes(boxes)
        self.largest_cluster = [l[0] for l in max(self.clusters, key=len)]
        for rect_id, _ in self.pieces:
            self.canvas.itemconfig(rect_id, {"fill": "lightgreen" if rect_id in self.largest_cluster else "white"})

# simple clustering algorithm, taking a list of (id, [coords]) and returning a list of [(id, [coords])]
def cluster_boxes(boxes):
    threshold = Vec2(BOX_HEIGHT * 2, BOX_HEIGHT)
    clusters = []
    for box_id, coords in boxes:
        x1, y1, x2, y2 = coords
        added = False
        for cluster in clusters:
            for _, ccoords in cluster:
                cx1, cy1, cx2, cy2 = ccoords
                # y: difference between top and bottom of the boxes is small enough (either up or down)
                if (abs(y1 - cy2) < threshold.y or abs(cy1 - y2) < threshold.y 
                    # x: pieces somewhat aligned in x by their left edge
                    ) and abs(x1 - cx1) < threshold.x: 
                        cluster.append((box_id, coords))
                        added = True
                        break
            if added:
                break
        if not added:
            clusters.append([(box_id, coords)])    
    return clusters

# parse a .pyzzle file to get the instructions and code pieces in a PyzzleDescription
def parse_pyzzle_file(filename):
    INSTRUCTIONS_MARKER = "PYZZLE_INSTRUCTIONS_"
    CODE_MARKER = "PYZZLE_CODE_"
    START_MARKER = "START"
    END_MARKER = "END"
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read()
        instr_start = content.find(INSTRUCTIONS_MARKER + START_MARKER)
        instr_end = content.find(INSTRUCTIONS_MARKER + END_MARKER)
        code_start = content.find(CODE_MARKER + START_MARKER)
        code_end = content.find(CODE_MARKER + END_MARKER)
        instructions = content[instr_start+len(INSTRUCTIONS_MARKER + START_MARKER):instr_end].strip()
        code = content[code_start+len(CODE_MARKER + START_MARKER):code_end].strip()
        return PyzzleDescription(instructions, code)


def main():
    root = tk.Tk()
    Pyzzle(root)
    root.mainloop()

if __name__ == "__main__":
    main()