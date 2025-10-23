# Streamlit Deployment Guide

The AR²C Streamlit interface ships as `streamlit_app.py` at the repository root. This document explains how to run it locally and deploy it to Streamlit Community Cloud (free tier) without adding any closed-source dependencies.

## Local Execution
1. Install Python 3.9 or newer.
2. Create a virtual environment (recommended) and install requirements:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Launch the app:
   ```bash
   streamlit run streamlit_app.py
   ```
4. Open the served URL (default `http://localhost:8501`) to interact with the demo entirely offline. All answers are produced from the bundled knowledge base in `data/knowledge_base.json`.

## Streamlit Community Cloud
1. Fork or push this repository to your own GitHub account.
2. Sign in to [Streamlit Community Cloud](https://streamlit.io/cloud) using GitHub and select **New app**.
3. Choose your repository, the default branch, and set the app file to `streamlit_app.py`.
4. In the **Advanced settings**, add:
   - **Dependencies file**: `requirements.txt`
   - (Optional) Environment variable `AR2C_KB_PATH` if you plan to point to a custom knowledge base.
5. Deploy. Streamlit installs the dependencies and runs the app automatically. Updates pushed to your repo trigger redeploys.

## Custom Knowledge Base
- Replace `data/knowledge_base.json` with additional entries. The loader enforces the same schema used by the CLI.
- For deployments, commit the updated JSON file; Streamlit will bundle it automatically.
- To use an alternate file without modifying the repository, set an environment variable `AR2C_KB_PATH` to the path of your JSON file. The Streamlit app reads it if present.

## Operational Notes
- The app only depends on Streamlit and the standard library, keeping the demo lightweight.
- No external APIs or network calls are required; retrieval and reasoning are performed locally in-memory.
- The Community Cloud free tier provides public URLs. If you need a fully offline experience, keep the app on an internal network using the local execution steps.
