"""Main file for running AutoSummoner"""

import multiprocessing
import sys

from AutoSummoner import App

if __name__ == '__main__':
    multiprocessing.freeze_support()
    sys.exit(App.run())
