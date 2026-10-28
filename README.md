# Nova - Azure OpenAI Chatbot (Streamlit)

## Files
| File | Purpose |
|---|---|
| `app.py` | Streamlit chat frontend |
| `chatbot.py` | Azure OpenAI client, config and streaming |
| `.env` | Your secrets (local only, never commit) |
| `.env.example` | Template to share |
| `requirements.txt` | Dependencies |
| `startup.sh` | Azure App Service startup command |
| `Dockerfile` | Optional container deployment |

## 1. Get your Azure values
1. Azure Portal > your **Azure OpenAI** resource > **Keys and Endpoint**: copy `KEY 1` and the `Endpoint`.
2. Azure AI Foundry > **Deployments**: copy the **deployment name** exactly (e.g. `gpt-4o-mini`).
3. Put all three in `.env`.

> **"Deployment not found" error?** The value of `AZURE_OPENAI_DEPLOYMENT` must be the deployment
> name you created (not just the model name), the endpoint must be from the same resource, and a
> brand new deployment can take a few minutes to become active.

## 2. Run locally
```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501

## 3. Deploy to Azure App Service (Linux)
```bash
az login
az group create --name nova-rg --location eastus
az appservice plan create --name nova-plan --resource-group nova-rg --sku B1 --is-linux
az webapp create --resource-group nova-rg --plan nova-plan --name <unique-app-name> --runtime "PYTHON:3.11"

# Secrets go in app settings, NOT in the uploaded .env
az webapp config appsettings set --resource-group nova-rg --name <unique-app-name> --settings \
  AZURE_OPENAI_API_KEY="<key>" \
  AZURE_OPENAI_ENDPOINT="https://<resource>.openai.azure.com/" \
  AZURE_OPENAI_DEPLOYMENT="<deployment-name>" \
  AZURE_OPENAI_API_VERSION="2024-10-21" \
  SCM_DO_BUILD_DURING_DEPLOYMENT=true

az webapp config set --resource-group nova-rg --name <unique-app-name> --startup-file "bash startup.sh"
az webapp config set --resource-group nova-rg --name <unique-app-name> --web-sockets-enabled true

# Zip deploy (run inside the project folder; do not include .env)
zip -r app.zip app.py chatbot.py requirements.txt startup.sh
az webapp deploy --resource-group nova-rg --name <unique-app-name> --src-path app.zip --type zip
```
Your app will be at `https://<unique-app-name>.azurewebsites.net`.

Streamlit needs **WebSockets** enabled on App Service (done above).

## Optional: Docker
```bash
docker build -t nova-chatbot .
docker run -p 8000:8000 --env-file .env nova-chatbot
```
