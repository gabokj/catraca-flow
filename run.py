import os
import sys

# Adiciona o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import run_server

if __name__ == '__main__':
    run_server()

