import curses


class CursesDisplay:

    def __init__(self):
        self.scr = curses.initscr()
        curses.start_color()
        self.scr.keypad(0)
        curses.noecho()
        self.colors = {}

    @property
    def size(self):
        return self.scr.getmaxyx()

    def new_line(self):
        self.scr.addstr('\n', curses.color_pair(1))

    def finish(self):
        curses.use_default_colors()
        self.scr.refresh()
        self.scr.getch()

    def print_color(self, r: int, g: int, b: int, s=' '):
        key = (r, g, b)
        if key not in self.colors:
            i_color = 1 + len(self.colors)
            self.colors[key] = i_color
            r = int(1000 * r / 255)
            g = int(1000 * g / 255)
            b = int(1000 * b / 255)
            curses.init_color(i_color, r, g, b)
            curses.init_pair(i_color, curses.COLOR_BLACK, i_color)
        else:
            i_color = self.colors[key]
        self.scr.addstr(s, curses.color_pair(i_color))
        self.scr.refresh()