import curses
from PIL import Image


class CursesDisplay:

    def __init__(self):
        self.scr = curses.initscr()
        curses.start_color()
        self.scr.keypad(0)
        curses.noecho()
        self.colors = {}
        self._old_pairs = {}
        curses.def_prog_mode()

    def _init_text_style(self):
        self._define_color(1, r=0, g=0, b=0)
        self._define_color(2, r=200, g=200, b=200)
        self._define_style(1, 2, 1)
        self._define_style(2, 1, 2)

    def _reset(self):
        self.scr.clear()
        self.colors.clear()
        self._init_text_style()

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

    def wait_key(self):
        while True:
            inch = self.scr.getch()
            if inch in [ord('a'), ord('d'), ord('q')]:
                return inch

    def imshow(self, image, msg=''):
        self._reset()
        dh, dw = self.size
        header = 'Q - Exit | D - Next | A - Prev | %s' % msg
        header = header[:dw - 1]
        self.scr.addstr(header, curses.color_pair(1))
        if image is not None:
            i_w, i_h = image.size
            i_w *= 2  # Rows compensation.
            f = min((dw - 1) / i_w, (dh - 1) / i_h)
            new_w = int(f * i_w)
            new_h = int(f * i_h)
            image = image.resize((new_w, new_h), Image.ANTIALIAS)
            image = image.convert('P', palette=Image.ADAPTIVE, colors=253)
            image = image.convert('RGB')
            pxs = image.load()
            for i_row in range(new_h):
                self.new_line()
                for i_col in range(new_w):
                    r, g, b = pxs[i_col, i_row]
                    self.print_color(r, g, b)
        inch = self.finish()
        return inch

    def finish(self):
        inch = self.wait_key()
        self.reset_original_scheme()
        curses.use_default_colors()
        self.scr.refresh()
        curses.endwin()
        return inch

    def _define_style(self, i_style: int, i_fg_color: int, i_bg_color):
        self._old_pairs[i_style] = curses.pair_content(i_style)
        curses.init_pair(i_style, i_fg_color, i_bg_color)

    def _define_color(self, i_color: int, r: int, g: int, b: int):
        key = (r, g, b)
        old_rgb = curses.color_content(i_color)
        self.colors[key] = (i_color, old_rgb)
        r = int(1000 * r / 255)
        g = int(1000 * g / 255)
        b = int(1000 * b / 255)
        curses.init_color(i_color, r, g, b)

    def print_color(self, r: int, g: int, b: int, s=' '):
        key = (r, g, b)
        if key not in self.colors:
            i_color = 1 + len(self.colors)
            self._define_color(i_color, r, g, b)
            self._define_style(i_color, 2, i_color)
        else:
            i_color, _ = self.colors[key]
        self.scr.addstr(s, curses.color_pair(i_color))
        self.scr.refresh()
