import warnings
warnings.filterwarnings("ignore")

from backend.router.query_router import route_question  

def main():
    print("\nEnterprise Knowledge Assistant Ready.")
    print("Type your question or 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()

        if not question:
            continue

        if question.lower() == "exit":
            print("Goodbye.")
            break

        result = route_question(question)

        print(f"\nAssistant [{result['source_type'].upper()}]:")
        print(result['answer'])

        if result.get('sources'):
            print(f"\nSources: {', '.join(result['sources'])}")

        print("-" * 60)

if __name__ == "__main__":
    main()