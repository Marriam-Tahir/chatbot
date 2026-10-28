"""Quick test of your Azure OpenAI settings (no Streamlit needed)."""

from openai import AzureOpenAI, NotFoundError, AuthenticationError

from chatbot import ConfigError, get_config

try:
    cfg = get_config()
except ConfigError as e:
    print("X", e, "- fill in your .env file first.")
    raise SystemExit(1)

print("Endpoint  :", cfg["endpoint"])
print("Deployment:", cfg["deployment"])
print("API version:", cfg["api_version"])
print("Testing connection...\n")

client = AzureOpenAI(
    api_key=cfg["api_key"],
    azure_endpoint=cfg["endpoint"],
    api_version=cfg["api_version"],
)

try:
    response = client.chat.completions.create(
        model=cfg["deployment"],
        messages=[{"role": "user", "content": "Say hello in one short sentence."}],
        max_tokens=30,
    )
    print("OK, Azure is working. Reply:", response.choices[0].message.content)
except NotFoundError:
    print("X Deployment not found. AZURE_OPENAI_DEPLOYMENT must exactly match the")
    print("  deployment name in Azure AI Foundry > Deployments, and the endpoint must")
    print("  belong to the same resource.")
except AuthenticationError:
    print("X Authentication failed. Check AZURE_OPENAI_API_KEY and the endpoint.")
except Exception as e:  # noqa: BLE001
    print("X Error:", e)