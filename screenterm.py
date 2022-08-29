import curses
from math import dist


class Screen:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        
        self.stdscr.clear()
        
        # workaround for bug where text was not written
        stdscr.nodelay(True)
        try:
            stdscr.getkey()
        except:
            pass
        stdscr.nodelay(False)
        
        max_rows, max_cols = self.stdscr.getmaxyx()
        self.term_win = curses.newwin(max_rows - 1, max_cols, 0, 0)
        self.status_win = curses.newwin(1, max_cols, max_rows - 1, 0)
        
        self.status_win.clear()
        self.status_win.refresh()
        
        self.term_win.clear()
        self.term_win.move(0, 0)
        self.term_win.refresh()
        
        self.fields = []
        
        self.max_rows, self.max_cols = self.stdscr.getmaxyx()
    
    def add_field(self, row, col, length, attr):
        self.fields.append((row, col, length, attr))
    
    def clear_fields(self):
        self.fields = []
    
    def read_field(self, n):
        row, col, length, _ = self.fields[n]
        return self.term_win.instr(row, col, length).decode("utf-8")
    
    def getpos(self):
        return self.term_win.getyx()
    
    def setpos(self, row, col):
        self.term_win.move(row, col)
        self.term_win.refresh()
    
    def put(self, c):
        try:
            self.term_win.addstr(c)
        except curses.error:
            self.term_win.move(0, 0)
        self.term_win.refresh()
    
    def clear(self):
        self.term_win.clear()
        self.term_win.refresh()
    
    def write(self, row, col, c):
        try:
            self.term_win.addstr(row, col, c)
        except curses.error:
            pass
        self.term_win.refresh()
    
    def status(self, s):
        self.status_win.clear()
        self.status_win.addstr(s)
        self.status_win.refresh()
        self.term_win.refresh()
    
    def isinfield(self, row, col):
        field = None
        field_no = -1
        for i, (start_row, start_col, length, attr) in enumerate(self.fields):
            if (
                row == start_row
                and col >= start_col
                and col - start_col < length
            ):
                field = (start_row, start_col, length, attr)
                field_no = i
                break
        
        return field, field_no
    
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
    
    def cursor_home(self):
        row, col = self.term_win.getyx()
        field, _ = self.isinfield(row, col - 1)
        
        if field:
            new_row, new_col, _, _ = field
            self.setpos(new_row, new_col)
    
    def cursor_end(self):
        row, col = self.term_win.getyx()
        field, _ = self.isinfield(row, col)
        
        if field:
            new_row, col, length, _ = field
            self.setpos(new_row, col + length)
    
    def cursor_tab(self):
        row, col = self.term_win.getyx()
        field, index = self.isinfield(row, col)
        if not field:
            field, index = self.isinfield(row, col - 1)
        
        if field:
            next_field_index = (index + 1) % len(self.fields)
            new_row, new_col, _, _ = self.fields[next_field_index]
            self.setpos(new_row, new_col)
        
        else:
            new_field = None
            distance = 0
            for f in self.fields:
                new_row, new_col, length, _ = f
                
                new_distance = dist([col, row], [new_col, new_row])
                new_distance_left = (
                    dist([col, row], [new_col + length - 1, new_row])
                )
                
                min_distance = min(new_distance, new_distance_left)
                
                if not new_field or min_distance < distance:
                    distance = min_distance
                    new_field = f
                    
            if new_field:
                new_row, new_col, _, _ = new_field
                self.setpos(new_row, new_col)
    
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
    
    screen.write(2, 1, "Item ID     ===>")
    screen.write(3, 1, "Description ===>")
    screen.write(4, 1, "Price       ===>")
    screen.write(4, 35, "Code ===>")
    screen.setpos(0, 0)
    
    screen.add_field(2, 18, 16, [])
    screen.add_field(3, 18, 16, [])
    screen.add_field(4, 18, 16, [])
    screen.add_field(4, 45, 4, [])
    
    while True:
        c = stdscr.getkey()
        
        if (
            c.isprintable() 
            and len(c) == 1
            and (not c.isspace() or c == " ")
        ):
            row, col = screen.getpos()
            field, _ = screen.isinfield(row, col)
            if not field:
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
        
        elif c == "KEY_HOME":
            screen.cursor_home()
        
        elif c == "KEY_END":
            screen.cursor_end()
        
        elif c == "\t":
            screen.cursor_tab()
        
        elif c == "\n":
            break
        
        else:
            screen.status(f"X - Unrecognized \"{c}\"")

    item_id = screen.read_field(0).strip()
    description = screen.read_field(1).strip()
    price = screen.read_field(2).strip()
    return item_id, description, price


if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    
    try:
        item_id, description, price = main(stdscr)
    except:
        item_id, description, price = ("", "", "")
    
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
    
    print(f"Your item ID was: {item_id}")
    print(f"Your description was: {description}")
    print(f"Your price was: {price}")
