from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
    dest_base = 'Snake',
    data_files = [('', ['8biteat.wav', 'freesansbold.ttf'])],
    options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
    windows = [{'script': "main.py"}],
    zipfile = None,
)

os.rename('dist/main.exe','dist/snake.exe')