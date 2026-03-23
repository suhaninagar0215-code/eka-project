from backend.llm.llm_provider import get_llm

def test_llm():
    try:
        llm = get_llm()
        response = llm.invoke("Say hello like a professional chatbot")

        print("\n LLM Response:")
        print(response.content)

    except Exception as e:
        print("\n LLM Test Failed:")
        print(str(e))


if __name__ == "__main__":
    test_llm()