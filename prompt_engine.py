"""Motor central de engenharia de prompts - Integra segurança, modos, tipos e APIs."""

import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

from prompt_security import validate_and_sanitize_prompt, PromptSecurityValidator, PromptInjectionDetector
from prompt_modes import AIMode, AIModesConfig, ModeSelector
from prompt_types import PromptType, PromptContext, PromptFactory, PromptOptimizer
from dual_api_manager import DualAPIManager, APIProvider, APIResponseMetrics

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptRequest:
    """Representa uma requisição de prompt."""

    def __init__(
        self,
        user_message: str,
        mode: Optional[AIMode] = None,
        prompt_type: PromptType = PromptType.STRUCTURED,
        preferred_provider: Optional[APIProvider] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.user_message = user_message
        self.mode = mode or AIMode.TECHNICAL
        self.prompt_type = prompt_type
        self.preferred_provider = preferred_provider
        self.context = context or {}
        self.timestamp = datetime.now().isoformat()
        self.request_id = self._generate_request_id()

    def _generate_request_id(self) -> str:
        """Gera ID único para requisição."""
        import hashlib
        content = f"{self.user_message}{self.timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "request_id": self.request_id,
            "user_message": self.user_message,
            "mode": self.mode.value,
            "prompt_type": self.prompt_type.value,
            "preferred_provider": self.preferred_provider.value if self.preferred_provider else None,
            "context": self.context,
            "timestamp": self.timestamp
        }


class PromptResponse:
    """Representa uma resposta de prompt."""

    def __init__(
        self,
        request_id: str,
        response_text: str,
        metrics: APIResponseMetrics,
        security_info: Dict[str, Any],
        mode: AIMode,
        prompt_type: PromptType
    ):
        self.request_id = request_id
        self.response_text = response_text
        self.metrics = metrics
        self.security_info = security_info
        self.mode = mode
        self.prompt_type = prompt_type
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "request_id": self.request_id,
            "response_text": self.response_text,
            "metrics": self.metrics.to_dict(),
            "security_info": self.security_info,
            "mode": self.mode.value,
            "prompt_type": self.prompt_type.value,
            "timestamp": self.timestamp
        }


class PromptEngine:
    """Motor central de engenharia de prompts."""

    def __init__(self):
        self.api_manager = DualAPIManager()
        self.request_history: List[PromptRequest] = []
        self.response_history: List[PromptResponse] = []
        logger.info("PromptEngine inicializado")

    def process_request(self, request: PromptRequest) -> PromptResponse:
        """
        Processa uma requisição de prompt completa.
        
        Fluxo:
        1. Validação de segurança
        2. Seleção de modo (se não especificado)
        3. Construção de prompt
        4. Envio para API
        5. Retorno de resposta
        """
        # Registrar requisição
        self.request_history.append(request)
        logger.info(f"Processando requisição {request.request_id}")

        # Etapa 1: Validação de segurança
        logger.info("Etapa 1: Validação de segurança")
        is_approved, clean_prompt, security_details = validate_and_sanitize_prompt(
            request.user_message,
            strict=True
        )

        if not is_approved:
            logger.warning(f"Requisição {request.request_id} rejeitada: {security_details['reason']}")
            return self._create_security_rejected_response(
                request, security_details
            )

        # Log de injeção detectada
        if security_details.get("injection_risk", {}).get("overall_risk"):
            logger.warning(f"Risco de injeção detectado: {security_details['injection_risk']}")

        # Etapa 2: Seleção de modo
        logger.info("Etapa 2: Seleção de modo")
        mode = request.mode
        if mode == AIMode.TECHNICAL:  # Default, pode auto-detectar
            suggested_mode = ModeSelector.suggest_mode(request.user_message)
            if suggested_mode != AIMode.TECHNICAL:
                logger.info(f"Modo auto-sugerido: {suggested_mode.value}")
                mode = suggested_mode

        # Etapa 3: Construção de prompt
        logger.info("Etapa 3: Construção de prompt")
        mode_config = AIModesConfig.get_mode_config(mode)

        prompt_context = PromptContext(
            user_message=clean_prompt,
            system_message=mode_config.system_prompt,
            context=request.context,
            metadata={
                "mode": mode.value,
                "prompt_type": request.prompt_type.value
            }
        )

        final_prompt = PromptFactory.build_prompt(request.prompt_type, prompt_context)

        # Otimizar prompt
        if request.prompt_type != PromptType.SIMPLE:
            final_prompt = PromptOptimizer.optimize_for_clarity(final_prompt)

        logger.info(f"Prompt construído ({len(final_prompt)} caracteres)")

        # Etapa 4: Envio para API
        logger.info("Etapa 4: Envio para API")
        response_text, metrics = self.api_manager.send_message(
            message=final_prompt,
            system_message=None,  # Já incluído no prompt
            temperature=mode_config.temperature,
            max_tokens=mode_config.max_tokens,
            preferred_provider=request.preferred_provider
        )

        # Etapa 5: Criar resposta
        logger.info("Etapa 5: Resposta criada")
        response = PromptResponse(
            request_id=request.request_id,
            response_text=response_text,
            metrics=metrics,
            security_info=security_details,
            mode=mode,
            prompt_type=request.prompt_type
        )

        self.response_history.append(response)
        logger.info(f"Requisição {request.request_id} processada com sucesso")

        return response

    def _create_security_rejected_response(
        self,
        request: PromptRequest,
        security_details: Dict[str, Any]
    ) -> PromptResponse:
        """Cria resposta para requisição rejeitada por segurança."""
        metrics = APIResponseMetrics()
        metrics.success = False
        metrics.provider = "security_check"
        metrics.error_message = security_details.get("reason", "Requisição rejeitada")

        response = PromptResponse(
            request_id=request.request_id,
            response_text=f"❌ Requisição rejeitada por razões de segurança:\n{security_details.get('reason')}\nDetalhes: {security_details.get('details')}",
            metrics=metrics,
            security_info=security_details,
            mode=request.mode,
            prompt_type=request.prompt_type
        )

        self.response_history.append(response)
        return response

    def compare_providers(
        self,
        request: PromptRequest
    ) -> Dict[str, Any]:
        """Compara respostas de diferentes provedores."""
        logger.info(f"Comparando provedores para requisição {request.request_id}")

        # Validação de segurança
        is_approved, clean_prompt, security_details = validate_and_sanitize_prompt(
            request.user_message,
            strict=True
        )

        if not is_approved:
            return {
                "status": "rejected",
                "reason": security_details.get("reason"),
                "details": security_details.get("details")
            }

        # Construir prompt
        mode_config = AIModesConfig.get_mode_config(request.mode)
        prompt_context = PromptContext(
            user_message=clean_prompt,
            system_message=mode_config.system_prompt,
            context=request.context
        )

        final_prompt = PromptFactory.build_prompt(request.prompt_type, prompt_context)

        # Comparar
        comparison = self.api_manager.compare_responses(
            message=final_prompt,
            temperature=mode_config.temperature,
            max_tokens=mode_config.max_tokens
        )

        logger.info(f"Comparação concluída com {len(comparison)} provedores")
        return comparison

    def get_available_modes(self) -> List[str]:
        """Retorna modos de IA disponíveis."""
        return [mode.value for mode in AIMode]

    def get_available_prompt_types(self) -> List[str]:
        """Retorna tipos de prompts disponíveis."""
        return [ptype.value for ptype in PromptType]

    def get_available_providers(self) -> List[str]:
        """Retorna provedores de API disponíveis."""
        return [p.value for p in self.api_manager.get_available_providers()]

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso."""
        successful_requests = [r for r in self.response_history if r.metrics.success]
        failed_requests = [r for r in self.response_history if not r.metrics.success]

        modes_used = {}
        for resp in successful_requests:
            mode = resp.mode.value
            modes_used[mode] = modes_used.get(mode, 0) + 1

        providers_used = {}
        for resp in successful_requests:
            provider = resp.metrics.provider
            providers_used[provider] = providers_used.get(provider, 0) + 1

        return {
            "total_requests": len(self.request_history),
            "successful_responses": len(successful_requests),
            "failed_responses": len(failed_requests),
            "success_rate": len(successful_requests) / len(self.response_history) if self.response_history else 0,
            "modes_used": modes_used,
            "providers_used": providers_used,
            "api_metrics": self.api_manager.get_metrics_summary()
        }

    def analyze_request(self, user_message: str) -> Dict[str, Any]:
        """Analisa requisição sem executá-la."""
        security_score = PromptSecurityValidator.get_security_score(user_message)
        injection_analysis = PromptInjectionDetector.analyze_injection_risk(user_message)
        suggested_mode = ModeSelector.suggest_mode(user_message)

        return {
            "security_score": security_score,
            "security_safe": security_score > 50,
            "injection_risk": injection_analysis,
            "suggested_mode": suggested_mode.value,
            "message_length": len(user_message),
            "estimated_tokens": len(user_message) // 4  # Aproximação
        }

    def get_request_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna histórico de requisições."""
        return [r.to_dict() for r in self.request_history[-limit:]]

    def get_response_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna histórico de respostas."""
        return [r.to_dict() for r in self.response_history[-limit:]]

    def clear_history(self) -> None:
        """Limpa histórico."""
        self.request_history.clear()
        self.response_history.clear()
        self.api_manager.reset_metrics()
        logger.info("Histórico limpo")


# Instância global do motor de prompts
_prompt_engine: Optional[PromptEngine] = None


def get_prompt_engine() -> PromptEngine:
    """Obtém instância global do motor de prompts."""
    global _prompt_engine
    if _prompt_engine is None:
        _prompt_engine = PromptEngine()
    return _prompt_engine
