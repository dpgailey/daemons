#!/usr/bin/env python3

import inspect
import time

from wind0wz import Wind0wz



w = Wind0wz()

try:
  first = w.window('first', 50, 50, 0, 0)

  second = w.window('second', 50, 50, 0, 50)

  for x in range(1000):
    w.write(first['name'], str(x) + ': Hello world!')
    w.write(second['name'], str(x) + ': Goodbye world!')
    time.sleep(.20)


  while True:
    True
except Exception as exception:
  print(exception)
  w.close()
