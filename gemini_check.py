"""Script para testar conexão com OpenAI API (ChatGPT)."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from gemini_utils import APIRateLimiter


def load_env_file() -> None:
    """Carrega variáveis de ambiente do arquivo .env."""
    env_path = Path(".env")
    if env_path.exists():
        try:
            load_dotenv(env_path)
            print("Arquivo .env carregado.")
        except ImportError:
            print("Aviso: python-dotenv não instalado. Ignorando .env.")
    else:
        print("Aviso: arquivo .env não encontrado.")


def main() -> None:
    """Função principal - testa conexão com API OpenAI."""
    load_env_file()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("Erro: OPENAI_API_KEY não configurada ou inválida.")
        print("Defina sua chave OpenAI no .env ou no ambiente.")
        print("\nExemplo PowerShell:")
        print("  $env:OPENAI_API_KEY='sua_chave_aqui'")
        print("\nObtenha sua chave em: https://platform.openai.com/api-keys")
        sys.exit(1)

    try:
        from openai import OpenAI
    except ImportError:
        print("Erro: biblioteca openai não instalada.")
        print("Instale com: pip install openai")
        sys.exit(1)

    # Verificar rate limit
    can_request, wait_time = APIRateLimiter.check_rate_limit()
    if not can_request:
        print(f"⏳ Rate limit ativo. Aguarde {wait_time:.1f}s antes da próxima requisição.")
        # Tentar usar cache
        cached = APIRateLimiter.get_cached_response()
        if cached:
            print("✓ Usando resposta em cache:")
            print(f"\n--- Cache ---\n{cached}\n----------")
        return

    try:
        client = OpenAI(api_key=api_key)

        default_model = "gpt-4o-mini"
        env_model = os.getenv("OPENAI_MODEL", "").strip()
        model_name = env_model if env_model else default_model

        print(f"Conectando ao ChatGPT com o modelo: {model_name}")

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Responda apenas: OK + nome do modelo"}
            ],
            max_tokens=50
        )

        result_text = response.choices[0].message.content.strip()
        APIRateLimiter.set_cached_response(result_text)
        APIRateLimiter.update_rate_limit()

        print("\n--- Resposta do ChatGPT ---")
        print(result_text)
        print("---------------------------")

    except Exception as exc:
        error_str = str(exc)
        
        if APIRateLimiter.is_quota_error(error_str):
            print("\n" + APIRateLimiter.get_friendly_error_message(error_str))
            # Tentar usar cache
            cached = APIRateLimiter.get_cached_response()
            if cached:
                print(f"\n✓ Usando resposta em cache:\n{cached}")
            sys.exit(1)
        else:
            print("\nErro ao chamar a API OpenAI:")
            print(error_str)
            sys.exit(1)


if __name__ == "__main__":
    main()
