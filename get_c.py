# not my work, in the interest of full disclosure
import sys, time, select, os
 
def get_c():
    ch = None
    try:
        os.system('stty raw</dev/tty')
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            ch = sys.stdin.read(1)
    finally:
        os.system('stty -raw</dev/tty')
    return ch
