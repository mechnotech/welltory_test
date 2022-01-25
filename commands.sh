#!/bin/bash
alembic upgrade head
cd src
python3 pywsgi.py

