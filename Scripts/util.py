import os
import sys


def get_path(filename):
    if hasattr(sys, "_MEIPASS"):
        if filename[:3] == '../':
            filename = filename[1:]
        return os.path.join(sys._MEIPASS, filename)
    else:
        return filename
