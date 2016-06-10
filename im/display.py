import curses


class CursesDisplay:

    def __init__(self):
        self.scr = curses.initscr()
        curses.start_color()
        self.scr.keypad(0)
        curses.noecho()
        self.colors = {}
        self._old_pairs = {}
        curses.def_prog_mode()

    @property
    def size(self):
        return self.scr.getmaxyx()

    def new_line(self):
        self.scr.addstr('\n', curses.color_pair(1))

    def reset_original_scheme(self):
        for _, (i_color, (r, g, b)) in self.colors.items():     # Reset original colors.
            curses.init_color(i_color, r, g, b)

        for i_color, (fg, bg) in self._old_pairs.items():       # Reset pairs - logic but without effect currently.
            curses.init_pair(i_color, bg, fg)

    def finish(self):
        curses.use_default_colors()
        self.scr.getch()
        self.reset_original_scheme()
        self.scr.refresh()
        curses.endwin()
        curses.reset_shell_mode()

    def print_color(self, r: int, g: int, b: int, s=' '):
        key = (r, g, b)
        if key not in self.colors:
            i_color = 1 + len(self.colors)
            old_rgb = curses.color_content(i_color)
            self.colors[key] = (i_color, old_rgb)
            r = int(1000 * r / 255)
            g = int(1000 * g / 255)
            b = int(1000 * b / 255)
            curses.init_color(i_color, r, g, b)
            self._old_pairs[i_color] = curses.pair_content(i_color)
            curses.init_pair(i_color, curses.COLOR_BLACK, i_color)
        else:
            i_color, _ = self.colors[key]
        self.scr.addstr(s, curses.color_pair(i_color))
        self.scr.refresh()
