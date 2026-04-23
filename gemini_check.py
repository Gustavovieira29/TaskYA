import os
import sys
from pathlib import Path


def load_env_file() -> None:
    env_path = Path(".env")
    if env_path.exists():
        try:
            from dotenv import load_dotenv
        except ImportError:
            print("Aviso: python-dotenv não instalado. Ignorando .env.")
            return
        load_dotenv(env_path)
        print("Arquivo .env carregado.")


def get_response_text(response: object) -> str:
    if response is None:
        return "Resposta vazia da API."
    if hasattr(response, "text"):
        return response.text
    if hasattr(response, "candidates") and response.candidates:
        candidate = response.candidates[0]
        return getattr(candidate, "content", repr(candidate))
    return repr(response)


def main() -> None:
    load_env_file()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Erro: a variável de ambiente GEMINI_API_KEY não foi encontrada.")
        print("Defina a chave no .env ou no ambiente antes de executar o script.")
        print("Exemplo no PowerShell:")
        print("  $env:GEMINI_API_KEY='sua_chave_aqui'")
        sys.exit(1)

    try:
        from google.ai import generativeai as genai
    except ImportError:
        print("Erro: biblioteca google-generativeai não encontrada.")
        print("Instale com: pip install -r requirements.txt")
        sys.exit(1)

    model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    prompt = "Verifique a comunicação com a API Gemini e responda apenas OK junto com o nome do modelo."

    genai.configure(api_key=api_key)
    print(f"Conectando ao Gemini com o modelo: {model}")

    try:
        response = genai.generate_text(
            model=model,
            prompt=prompt,
            max_output_tokens=60,
        )
    except Exception as exc:
        print("Erro ao chamar a API Gemini:")
        print(exc)
        sys.exit(1)

    text = get_response_text(response)
    print("\n--- Resposta do Gemini ---")
    print(text.strip())
    print("--------------------------")


if __name__ == "__main__":
    main()
