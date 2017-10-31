from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
    snake = 'Snakeee',
    data_files = [('', ['8biteat.wav', 'freesansbold.ttf'])],
    options = {'py2exe': {'bundle_files': 2, 'compressed': True}},
    windows = [{'script': "main.py"}],
    zipfile = None,
)