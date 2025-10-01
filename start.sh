#!/bin/bash
pip install --upgrade pip
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
