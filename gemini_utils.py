"""Utilidades para integração com OpenAI API com rate limiting e cache."""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

CACHE_FILE = Path(".api_cache.json")
RATE_LIMIT_FILE = Path(".api_rate_limit.json")
MIN_TIME_BETWEEN_REQUESTS = 10  # segundos


class APIRateLimiter:
    """Gerenciador de rate limiting e cache para OpenAI API."""

    @staticmethod
    def load_cache() -> dict:
        """Carrega cache de respostas anteriores."""
        if CACHE_FILE.exists():
            try:
                return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    @staticmethod
    def save_cache(cache: dict) -> None:
        """Salva cache de respostas."""
        CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def check_rate_limit() -> tuple[bool, Optional[float]]:
        """
        Verifica se pode fazer nova requisição.
        
        Returns:
            (pode_fazer_requisição, tempo_espera_em_segundos)
        """
        if RATE_LIMIT_FILE.exists():
            try:
                data = json.loads(RATE_LIMIT_FILE.read_text(encoding="utf-8"))
                last_request_str = data.get("last_request", "")
                if last_request_str:
                    last_request = datetime.fromisoformat(last_request_str)
                    time_elapsed = (datetime.now() - last_request).total_seconds()
                    if time_elapsed < MIN_TIME_BETWEEN_REQUESTS:
                        return False, MIN_TIME_BETWEEN_REQUESTS - time_elapsed
            except Exception:
                pass
        return True, None

    @staticmethod
    def update_rate_limit() -> None:
        """Atualiza timestamp da última requisição."""
        RATE_LIMIT_FILE.write_text(
            json.dumps({"last_request": datetime.now().isoformat()}, indent=2),
            encoding="utf-8"
        )

    @staticmethod
    def get_cached_response(cache_key: str = "default") -> Optional[str]:
        """Obtém resposta em cache se disponível."""
        cache = APIRateLimiter.load_cache()
        return cache.get(f"response_{cache_key}")

    @staticmethod
    def set_cached_response(response: str, cache_key: str = "default") -> None:
        """Salva resposta em cache."""
        cache = APIRateLimiter.load_cache()
        cache[f"response_{cache_key}"] = response
        cache[f"timestamp_{cache_key}"] = datetime.now().isoformat()
        APIRateLimiter.save_cache(cache)

    @staticmethod
    def is_quota_error(error: str) -> bool:
        """Verifica se é erro de quota."""
        return "429" in error or "rate_limit" in error.lower() or "quota" in error.lower()

    @staticmethod
    def get_friendly_error_message(error: str) -> str:
        """Retorna mensagem de erro amigável."""
        if APIRateLimiter.is_quota_error(error):
            return (
                "⚠️  Limite de taxa da API OpenAI excedido!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Você atingiu o limite de requisições.\n\n"
                "Opções:\n"
                "1. Aguarde alguns momentos antes de tentar novamente\n"
                "2. Upgrade sua cota em https://platform.openai.com\n"
                "3. Use uma API key diferente\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
        return f"Erro na API OpenAI: {error}"


# Backward compatibility alias
GeminiRateLimiter = APIRateLimiter

