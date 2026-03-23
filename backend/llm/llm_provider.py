from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


def _validate_env():
    required = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT_4O",
        "AZURE_OPENAI_DEPLOYMENT_MINI",
        "OPENAI_API_VERSION",
    ]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

_validate_env()

def get_llm():
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_4O"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        temperature=0,
        max_tokens=2000      
    )

def get_mini_llm():
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_MINI"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        temperature=0,
        max_tokens=1000      
    )
if __name__ == "__main__" :
    llm = get_llm()
    print("LLM loaded successfully:", llm.deployment_name)