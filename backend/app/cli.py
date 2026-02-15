from app.brain.ai_engine import process_input

EXIT_WORDS = {"exit", "quit", "stop", "bye"}


def run_cli() -> None:
    print("Jarvis CLI (offline). Type 'exit' to stop.")
    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAssistant: Goodbye.")
            break

        if not user_text:
            continue

        if user_text.lower() in EXIT_WORDS:
            print("Assistant: Goodbye.")
            break

        response = process_input(user_text)
        print(f"Assistant: {response}")


if __name__ == "__main__":
    run_cli()
