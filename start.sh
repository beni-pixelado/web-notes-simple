#!/bin/bash
# Script para iniciar a aplicação

cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
