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


def main() -> None:
    load_env_file()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Erro: GEMINI_API_KEY não encontrada.")
        print("Defina no .env ou no ambiente.")
        print("Exemplo PowerShell:")
        print("  $env:GEMINI_API_KEY='sua_chave_aqui'")
        sys.exit(1)

    try:
        from google import genai
    except ImportError:
        print("Erro: biblioteca google-genai não instalada.")
        print("Instale com: pip install google-genai")
        sys.exit(1)

    try:
        client = genai.Client(api_key=api_key)

        default_model = "gemini-1.5-flash"
        env_model = os.getenv("GEMINI_MODEL", "").strip()
        if not env_model:
            model_name = default_model
        elif env_model == "gemini-1.5-pro":
            print(
                "Atenção: o modelo gemini-1.5-pro não é suportado pelo método generate_content "
                "nesta versão da API. Usando gemini-1.5-flash em seu lugar."
            )
            model_name = default_model
        else:
            model_name = env_model

        print(f"Conectando ao Gemini com o modelo: {model_name}")

        response = client.models.generate_content(
            model=model_name,
            contents="Responda apenas: OK + nome do modelo"
        )

    except Exception as exc:
        print("\nErro ao chamar a API Gemini:")
        print(exc)
        sys.exit(1)

    print("\n--- Resposta do Gemini ---")
    print(response.text.strip())
    print("--------------------------")


if __name__ == "__main__":
    main()