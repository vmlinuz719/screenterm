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

def main(stdscr):
    stdscr.clear()

    max_rows, max_cols = stdscr.getmaxyx()
    term_win = curses.newwin(max_rows - 1, max_cols, 0, 0)
    status_win = curses.newwin(1, max_cols, max_rows - 1, 0)

    while True:
        c = stdscr.getkey()

        row, col = term_win.getyx()

        if (
            c.isprintable() 
            and len(c) == 1
            and (not c.isspace() or c == " ")
        ):
            status_win.clear()

            protected = True
            for start_row, start_col, length, attr in fields:
                if (
                    row == start_row
                    and col >= start_col
                    and col - start_col < length
                ):
                    protected = False
                    break

            if protected:
                status_win.addstr("Protected")
                status_win.refresh()

            else:
                status_win.refresh()

                try:
                    term_win.addstr(c)
                except curses.error:
                    term_win.move(0, 0)

        elif c == "KEY_RIGHT":
            if col < max_cols - 1:
                term_win.move(row, col + 1)
            elif row == max_rows - 2:
                term_win.move(0, 0)
            else:
                term_win.move(row + 1, 0)

        elif c == "KEY_LEFT" or c == "KEY_BACKSPACE":
            if col > 0:
                term_win.move(row, col - 1)
            elif row == 0:
                term_win.move(max_rows - 2, max_cols - 1)
            else:
                term_win.move(row - 1, max_cols - 1)

        elif c == "KEY_UP":
            if row == 0:
                term_win.move(max_rows - 2, col)
            else:
                term_win.move(row - 1, col)

        elif c == "KEY_DOWN":
            if row < max_rows - 2:
                term_win.move(row + 1, col)
            else:
                term_win.move(0, col)

        elif c == "\n":
            try:
                input = term_win.instr(row, col, 16).decode("utf-8")
            except curses.error:
                input = "Error reading input"

            status_win.clear()
            status_win.addstr(input)
            status_win.refresh()

        else:
            status_win.clear()

            if c.isprintable() and not c.isspace():
                status_win.addstr(f"{c} key pressed!")
            else:
                status_win.addstr(f"Unprintable key pressed!")

            status_win.refresh()

        term_win.refresh()

curses.wrapper(main)

