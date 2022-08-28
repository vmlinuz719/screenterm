import curses

fields = [
    (1, 1, 16, []),
    (2, 1, 16, []),
    (3, 1, 16, []),
    (4, 1, 16, []),
    (5, 1, 16, []),
    (6, 1, 16, []),
    (7, 1, 16, []),
    (8, 1, 16, []),
]

class Screen:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        
        self.stdscr.clear()
        
        max_rows, max_cols = self.stdscr.getmaxyx()
        self.term_win = curses.newwin(max_rows - 1, max_cols, 0, 0)
        self.status_win = curses.newwin(1, max_cols, max_rows - 1, 0)
        
        self.fields = []
        
        self.max_rows, self.max_cols = self.stdscr.getmaxyx()
    
    def add_field(self, field):
        self.fields.append(field)
    
    def clear_fields(self):
        self.fields = []
    
    def getpos(self):
        return self.term_win.getyx()
    
    def setpos(self, row, col):
        self.term_win.move(row, col)
    
    def isprotected(self, row, col):
        protected = True
        for start_row, start_col, length, attr in self.fields:
            if (
                row == start_row
                and col >= start_col
                and col - start_col < length
            ):
                protected = False
                break
        
        return protected
    
    def write(self, row, col, c):
        try:
            self.term_win.addstr(row, col, c)
            self.term_win.refresh()
        except curses.error:
            pass
    
    def put(self, c):
        try:
            self.term_win.addstr(c)
            self.term_win.refresh()
        except curses.error:
            self.term_win.move(0, 0)
    
    def status(self, s):
        self.status_win.clear()
        self.status_win.addstr(s)
        self.status_win.refresh()
        self.term_win.refresh()
    
    def cursor_up(self):
        row, col = self.term_win.getyx()
        if row == 0:
            self.term_win.move(self.max_rows - 2, col)
        else:
            self.term_win.move(row - 1, col)
        self.term_win.refresh()
    
    def cursor_down(self):
        row, col = self.term_win.getyx()
        if row < self.max_rows - 2:
            self.term_win.move(row + 1, col)
        else:
            self.term_win.move(0, col)
        self.term_win.refresh()
    
    def cursor_left(self):
        row, col = self.term_win.getyx()
        if col > 0:
            self.term_win.move(row, col - 1)
        elif row == 0:
            self.term_win.move(self.max_rows - 2, self.max_cols - 1)
        else:
            self.term_win.move(row - 1, self.max_cols - 1)
        self.term_win.refresh()
    
    def cursor_right(self):
        row, col = self.term_win.getyx()
        if col < self.max_cols - 1:
            self.term_win.move(row, col + 1)
        elif row == self.max_rows - 2:
            self.term_win.move(0, 0)
        else:
            self.term_win.move(row + 1, 0)
        self.term_win.refresh()

def main(stdscr):
    stdscr.clear()
    
    screen = Screen(stdscr)
    
    while True:
        c = stdscr.getkey()
        
        if (
            c.isprintable() 
            and len(c) == 1
            and (not c.isspace() or c == " ")
        ):
            row, col = screen.getpos()
            if screen.isprotected(row, col):
                screen.status("X - Protected")
            else:
                screen.status("")
                screen.put(c)
        
        elif c == "KEY_UP":
            screen.cursor_up()
        
        elif c == "KEY_DOWN":
            screen.cursor_down()
        
        elif c == "KEY_LEFT" or c == "KEY_BACKSPACE":
            screen.cursor_left()
        
        elif c == "KEY_RIGHT":
            screen.cursor_right()
        
        else:
            screen.status("X - Unrecognized")

curses.wrapper(main)

