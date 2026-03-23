import warnings
warnings.filterwarnings("ignore")

from backend.agent.agent_runner import run_agent

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

        answer = run_agent(question)
        print(f"\nAssistant:\n{answer}\n")
        print("-" * 60)

if __name__ == "__main__":
    main()