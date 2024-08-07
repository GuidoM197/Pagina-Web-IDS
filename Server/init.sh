#!/bin/bash

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
PYTHON_MAJOR_MINOR=$(echo $PYTHON_VERSION | cut -d. -f1,2)

# Instalar Python 3 y los paquetes necesarios
sudo apt install -y python${PYTHON_MAJOR_MINOR} python${PYTHON_MAJOR_MINOR}-venv python${PYTHON_MAJOR_MINOR}-dev

pip install flask
pip install flask_sqlalchemy sqlalchemy psycopg2-binary

python3 app.py
