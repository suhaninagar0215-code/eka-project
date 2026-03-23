import warnings
warnings.filterwarnings("ignore")
from backend.agent.agent_runner import run_agent

def main():
    while True:
        question = input("\n Ask something(or 'exit'):")

        if question.lower() == "exit":
            break

        answer = run_agent(question)
        print("\nAnswer:\n",answer)


if __name__ == "__main__":
    main()
