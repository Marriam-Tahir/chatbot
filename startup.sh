#!/bin/bash
# Startup command for Azure App Service (Linux, Python 3.11+)
python -m streamlit run app.py \
  --server.port 8000 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false
