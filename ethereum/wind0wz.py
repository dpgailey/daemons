import curses
from curses import wrapper

class Wind0wz():
  def __init__(self):
    self.curses = curses
    self.main_window = curses.initscr()
    self.curses.noecho()
    self.curses.cbreak()
    self.window_list = {}

  def window(self, name, height, width, begin_y, begin_x):
    win = self.curses.newwin(height, width, begin_y, begin_x)
    win.border(0,0,0,0,0,0,0,0)
    pad = win.subpad(begin_y, begin_x)
    pad.scrollok(True)
    self.window_list[name] = {'name': name, 'win': pad, 'height': height, 'width': width, 'y': begin_y, 'x': begin_x}
    return self.window_list[name]

  def write(self, name, output):
    me = self.window_list[name]
    win = me['win']
    win.scrollok(True)
    #win.setscrreg(3, me['height']-3)
    win.scroll(1)

    win.addstr(0, 1, output)

    win.refresh()

  def close(self):
   self.curses.echo()
   self.curses.endwin()
