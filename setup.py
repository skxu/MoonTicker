"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup, find_packages

APP = ['moonticker.py']
DATA_FILES = []
OPTIONS = {
  'argv_emulation': True,
  'plist': {
      'LSUIElement': True,
  },
  'packages': ['rumps', 'requests', 'certifi']
}

setup(
    name='MoonTicker',
    version='0.0.1',
    author='skxu',
    author_email='skx@berkeley.edu',
    description='MacOS StatusBar Ticker for cryptocurrencies like Ethereum',
    license='MIT',
    url='https://github.com/skxu/MoonTicker',
    packages=find_packages(),
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app', 'rumps', 'requests', 'ConfigParser'],
)