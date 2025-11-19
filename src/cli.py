from .agent import run_agent


def main():
    print("👋 FinanCIA — Agente Financeiro (digite 'sair' para encerrar)")
    while True:
        try:
            user = input("\nVocê: ")
        except (EOFError, KeyboardInterrupt):
            print("\nAgente: Até mais! 🧾")
            break

        if user.strip().lower() in {"sair", "exit", "quit"}:
            print("Agente: Até mais! 🧾")
            break

        response = run_agent(user)
        print(f"Agente: {response.text}")

        if response.tool_call:
            print(f"[debug] Tool chamada: {response.tool_call['name']}")
            print(f"[debug] Args: {response.tool_call['args']}")
            print(f"[debug] Resultado: {response.tool_result}")


if __name__ == "__main__":
    main()
