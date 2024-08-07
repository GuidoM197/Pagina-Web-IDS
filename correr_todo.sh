#!/bin/bash

source venv/bin/activate

# Abre una nueva terminal para ejecutar Cliente/init.sh
gnome-terminal -- bash -c "cd ./Client && bash init.sh; exec bash"

# Abre una nueva terminal para ejecutar Server/init.sh
gnome-terminal -- bash -c "cd ./Server && bash init.sh; exec bash"
