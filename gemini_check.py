import os
import sys
from pathlib import Path

def load_env_file() -> None:
    env_path = Path(".env")
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
        except ImportError:
            pass

def main() -> None:
    load_env_file()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ Erro: GROQ_API_KEY não encontrada.")
        sys.exit(1)

    try:
        from groq import Groq
    except ImportError:
        print("❌ Erro: biblioteca groq não instalada. Use: pip install groq")
        sys.exit(1)

    client = Groq(api_key=api_key)
    model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    print(f"--- Chat Groq Iniciado ({model_name}) ---")
    print("Digite 'sair' ou 'exit' para encerrar.\n")

    # Lista para manter o histórico da conversa (memória do chat)
    messages = [
        {"role": "system", "content": "Você é um assistente de programação útil e conciso."}
    ]

    while True:
        # Pega a pergunta do usuário
        user_input = input("Você: ")

        if user_input.lower() in ["sair", "exit", "quit"]:
            print("Encerrando chat... tchau!")
            break

        if not user_input.strip():
            continue

        # Adiciona a pergunta ao histórico
        messages.append({"role": "user", "content": user_input})

        try:
            # Envia todo o histórico para o Groq manter o contexto
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.7,
            )

            response_text = completion.choices[0].message.content
            print(f"\nGroq: {response_text}\n")

            # Adiciona a resposta do assistente ao histórico
            messages.append({"role": "assistant", "content": response_text})

        except Exception as e:
            print(f"\n⚠️ Erro na resposta: {e}")

if __name__ == "__main__":
    main()