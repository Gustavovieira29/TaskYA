"""Gerenciador de APIs de IA - Suporta Groq e OpenAI com escolha automática."""

import os
from typing import Optional, Dict, Any, Tuple, List
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import json


class APIProvider(Enum):
    """Provedores de API de IA disponíveis."""
    GROQ = "groq"
    OPENAI = "openai"  # ou Claude Anthropic


class APIResponseMetrics:
    """Métricas de resposta da API."""

    def __init__(self):
        self.provider: str = ""
        self.response_time: float = 0.0
        self.tokens_used: int = 0
        self.cost_estimate: float = 0.0
        self.timestamp: str = ""
        self.success: bool = False
        self.error_message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "provider": self.provider,
            "response_time": self.response_time,
            "tokens_used": self.tokens_used,
            "cost_estimate": self.cost_estimate,
            "timestamp": self.timestamp,
            "success": self.success,
            "error_message": self.error_message,
        }


class AIAPIClient(ABC):
    """Classe base para clientes de API de IA."""

    @abstractmethod
    def send_message(
        self,
        message: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Tuple[str, APIResponseMetrics]:
        """Envia mensagem para API e retorna resposta com métricas."""
        pass

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Valida se as credenciais estão configuradas."""
        pass

    @abstractmethod
    def estimate_cost(self, tokens: int) -> float:
        """Estima custo para número de tokens."""
        pass


class GroqAPIClient(AIAPIClient):
    """Cliente para Groq API."""

    # Preços aproximados (ajuste conforme necessário)
    PRICE_PER_1K_TOKENS = 0.0005  # ~$0.50 por 1M tokens

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Inicializa cliente Groq."""
        try:
            from groq import Groq
            if self.api_key:
                self.client = Groq(api_key=self.api_key)
        except ImportError:
            pass

    def validate_credentials(self) -> bool:
        """Valida credenciais Groq."""
        return self.api_key is not None and self.client is not None

    def send_message(
        self,
        message: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Tuple[str, APIResponseMetrics]:
        """Envia mensagem para Groq."""
        metrics = APIResponseMetrics()
        metrics.provider = APIProvider.GROQ.value
        metrics.timestamp = datetime.now().isoformat()

        if not self.validate_credentials():
            metrics.success = False
            metrics.error_message = "Groq API key não configurada"
            return "", metrics

        try:
            import time
            start_time = time.time()

            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": message})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            end_time = time.time()

            content = response.choices[0].message.content

            # Calcular métricas
            metrics.response_time = end_time - start_time
            metrics.tokens_used = response.usage.total_tokens
            metrics.cost_estimate = self.estimate_cost(metrics.tokens_used)
            metrics.success = True

            return content, metrics

        except Exception as e:
            metrics.success = False
            metrics.error_message = str(e)
            return "", metrics

    def estimate_cost(self, tokens: int) -> float:
        """Estima custo para tokens."""
        return (tokens / 1000) * self.PRICE_PER_1K_TOKENS


class OpenAIAPIClient(AIAPIClient):
    """Cliente para OpenAI API."""

    # Preços aproximados (ajuste conforme necessário)
    PRICE_PER_1K_INPUT_TOKENS = 0.005  # $0.005 por 1K tokens de entrada
    PRICE_PER_1K_OUTPUT_TOKENS = 0.015  # $0.015 por 1K tokens de saída

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Inicializa cliente OpenAI."""
        try:
            from openai import OpenAI
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            pass

    def validate_credentials(self) -> bool:
        """Valida credenciais OpenAI."""
        return self.api_key is not None and self.client is not None

    def send_message(
        self,
        message: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Tuple[str, APIResponseMetrics]:
        """Envia mensagem para OpenAI."""
        metrics = APIResponseMetrics()
        metrics.provider = APIProvider.OPENAI.value
        metrics.timestamp = datetime.now().isoformat()

        if not self.validate_credentials():
            metrics.success = False
            metrics.error_message = "OpenAI API key não configurada"
            return "", metrics

        try:
            import time
            start_time = time.time()

            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": message})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            end_time = time.time()

            content = response.choices[0].message.content

            # Calcular métricas
            metrics.response_time = end_time - start_time
            metrics.tokens_used = response.usage.total_tokens
            metrics.cost_estimate = self.estimate_cost(
                response.usage.prompt_tokens,
                response.usage.completion_tokens
            )
            metrics.success = True

            return content, metrics

        except Exception as e:
            metrics.success = False
            metrics.error_message = str(e)
            return "", metrics

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estima custo para tokens."""
        input_cost = (input_tokens / 1000) * self.PRICE_PER_1K_INPUT_TOKENS
        output_cost = (output_tokens / 1000) * self.PRICE_PER_1K_OUTPUT_TOKENS
        return input_cost + output_cost


class DualAPIManager:
    """Gerenciador de múltiplas APIs com escolha automática."""

    def __init__(self):
        self.groq_client = GroqAPIClient()
        self.openai_client = OpenAIAPIClient()
        self.metrics_history: List[APIResponseMetrics] = []
        self.api_distribution = {
            APIProvider.GROQ: [],  # Tópicos para Groq
            APIProvider.OPENAI: []  # Tópicos para OpenAI
        }

    def get_available_providers(self) -> List[APIProvider]:
        """Retorna provedores disponíveis."""
        available = []
        if self.groq_client.validate_credentials():
            available.append(APIProvider.GROQ)
        if self.openai_client.validate_credentials():
            available.append(APIProvider.OPENAI)
        return available

    def send_message(
        self,
        message: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        preferred_provider: Optional[APIProvider] = None
    ) -> Tuple[str, APIResponseMetrics]:
        """
        Envia mensagem usando provider preferido ou automático.
        """
        available_providers = self.get_available_providers()

        if not available_providers:
            metrics = APIResponseMetrics()
            metrics.success = False
            metrics.error_message = "Nenhuma API de IA configurada"
            return "", metrics

        # Selecionar provider
        if preferred_provider and preferred_provider in available_providers:
            provider = preferred_provider
        else:
            provider = self._select_best_provider(message)

        # Enviar mensagem
        if provider == APIProvider.GROQ:
            response, metrics = self.groq_client.send_message(
                message, system_message, temperature, max_tokens
            )
        else:
            response, metrics = self.openai_client.send_message(
                message, system_message, temperature, max_tokens
            )

        # Registrar métricas
        self.metrics_history.append(metrics)

        return response, metrics

    def compare_responses(
        self,
        message: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Obtém respostas de ambas as APIs para comparação.
        """
        results = {}
        available_providers = self.get_available_providers()

        for provider in available_providers:
            if provider == APIProvider.GROQ:
                response, metrics = self.groq_client.send_message(
                    message, system_message, temperature, max_tokens
                )
            else:
                response, metrics = self.openai_client.send_message(
                    message, system_message, temperature, max_tokens
                )

            results[provider.value] = {
                "response": response,
                "metrics": metrics.to_dict()
            }

            self.metrics_history.append(metrics)

        return results

    def _select_best_provider(self, message: str) -> APIProvider:
        """
        Seleciona o melhor provider baseado em heurísticas.
        """
        message_lower = message.lower()

        # Se é pergunta técnica/código, usar Groq (bom para programação)
        technical_keywords = ["código", "bug", "debug", "sistema", "algoritmo", "python", "javascript"]
        if any(keyword in message_lower for keyword in technical_keywords):
            available = self.get_available_providers()
            if APIProvider.GROQ in available:
                return APIProvider.GROQ

        # Se é pergunta geral/criativa, preferir OpenAI (melhor para texto)
        creative_keywords = ["escrever", "criar", "historia", "poesia", "criativo"]
        if any(keyword in message_lower for keyword in creative_keywords):
            available = self.get_available_providers()
            if APIProvider.OPENAI in available:
                return APIProvider.OPENAI

        # Padrão: usar primeira disponível
        available = self.get_available_providers()
        return available[0] if available else APIProvider.GROQ

    def distribute_by_topic(self, topic: str, provider: APIProvider) -> None:
        """
        Define qual provider deve responder sobre um tópico.
        """
        if provider in self.api_distribution:
            self.api_distribution[provider].append(topic)

    def get_provider_for_topic(self, topic: str) -> Optional[APIProvider]:
        """
        Obtém provider sugerido para um tópico.
        """
        for provider, topics in self.api_distribution.items():
            if any(t.lower() in topic.lower() for t in topics):
                return provider
        return None

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Retorna resumo de métricas."""
        if not self.metrics_history:
            return {"total_calls": 0}

        successful = [m for m in self.metrics_history if m.success]
        failed = [m for m in self.metrics_history if not m.success]

        providers_used = {}
        total_cost = 0.0
        total_time = 0.0

        for metric in successful:
            if metric.provider not in providers_used:
                providers_used[metric.provider] = 0
            providers_used[metric.provider] += 1
            total_cost += metric.cost_estimate
            total_time += metric.response_time

        return {
            "total_calls": len(self.metrics_history),
            "successful": len(successful),
            "failed": len(failed),
            "providers_used": providers_used,
            "total_cost_estimate": total_cost,
            "avg_response_time": total_time / len(successful) if successful else 0,
            "failure_rate": len(failed) / len(self.metrics_history) if self.metrics_history else 0
        }

    def reset_metrics(self) -> None:
        """Limpa histórico de métricas."""
        self.metrics_history.clear()
