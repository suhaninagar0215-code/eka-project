from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)  

def get_llm():
    print("ENDPOINT:", os.getenv("AZURE_OPENAI_ENDPOINT"))
    print("DEPLOYMENT:", os.getenv("AZURE_OPENAI_DEPLOYMENT_4O"))
    print("API VERSION:", os.getenv("OPENAI_API_VERSION"))

    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_4O"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        temperature=0,
        max_tokens=500
    )
    
def get_mini_llm():
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_MINI"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        temperature=0,
        max_tokens=200
    )

if __name__ == "__main__":
    llm = get_llm()
    print("LLM loaded successfully:", llm)