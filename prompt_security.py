"""Sistema de segurança e proteção contra prompt injection e ataques."""

import re
from typing import Tuple, Dict, List
from enum import Enum
import json
import hashlib


class SecurityThreatLevel(Enum):
    """Níveis de ameaça detectados."""
    SAFE = "safe"
    WARNING = "warning"
    CRITICAL = "critical"
    BLOCKED = "blocked"


class PromptSecurityValidator:
    """Valida e sanitiza prompts contra injeção e conteúdo malicioso."""

    # Padrões perigosos conhecidos
    DANGEROUS_PATTERNS = {
        r"(?i)(ignore|forget|disregard).*?(previous|prior|instruction|rule|system|constraint)": "Tentativa de desabilitar restrições",
        r"(?i)(execute|run|eval|exec)\s*\(": "Tentativa de execução de código",
        r"(?i)(sql|select|insert|update|delete|drop).*?(from|into|where)": "Injeção SQL detectada",
        r"(?i)(import|require|load)\s*(?:\(|<)": "Tentativa de importar módulos",
        r"(?i)(jailbreak|breakout|escape|bypass)": "Tentativa de contorno de segurança",
        r"(?i)os\.(system|popen)|subprocess|shell=true": "Tentativa de acesso ao sistema",
        r"(?i)(administrator|root|sudo|privilege)": "Tentativa de escalonamento de privilégio",
        r"(?i)(password|secret|token|api[_-]?key)": "Tentativa de acesso a credenciais",
    }

    # Palavras-chave inadequadas (spam/inapropriadas)
    INAPPROPRIATE_KEYWORDS = [
        "spam", "phishing", "malware", "ransomware", "botnet",
        "cracker", "hacker", "exploit", "vulnerability", "zero-day"
    ]

    # Palavras-chave bloqueadas para contexto de tarefas
    TASK_CONTEXT_BLOCKED = [
        "delete all", "drop database", "truncate", "rm -rf",
        "format disk", "wipe", "destroy", "kill process"
    ]

    # Limite de contexto
    MAX_PROMPT_LENGTH = 5000
    MIN_PROMPT_LENGTH = 3

    # Limite de repetição de padrão (ajustado para 85% - permite estruturas formatadas)
    MAX_REPETITION_RATIO = 0.85

    @staticmethod
    def validate_prompt(prompt: str) -> Tuple[bool, Dict]:
        """
        Valida um prompt contra múltiplas ameaças.
        
        Returns:
            (é_seguro, detalhes)
        """
        if not isinstance(prompt, str):
            return False, {
                "threat_level": SecurityThreatLevel.CRITICAL.value,
                "reason": "Prompt não é texto",
                "details": "Tipo inválido recebido"
            }

        # Limpeza inicial
        prompt = prompt.strip()

        # Verificação de comprimento
        if len(prompt) < PromptSecurityValidator.MIN_PROMPT_LENGTH:
            return False, {
                "threat_level": SecurityThreatLevel.WARNING.value,
                "reason": "Prompt muito curto",
                "details": f"Mínimo: {PromptSecurityValidator.MIN_PROMPT_LENGTH} caracteres"
            }

        if len(prompt) > PromptSecurityValidator.MAX_PROMPT_LENGTH:
            return False, {
                "threat_level": SecurityThreatLevel.WARNING.value,
                "reason": "Prompt muito longo",
                "details": f"Máximo: {PromptSecurityValidator.MAX_PROMPT_LENGTH} caracteres"
            }

        # Detectar padrões perigosos
        dangerous_match = PromptSecurityValidator._check_dangerous_patterns(prompt)
        if dangerous_match:
            return False, {
                "threat_level": SecurityThreatLevel.CRITICAL.value,
                "reason": dangerous_match[1],
                "details": f"Padrão detectado: {dangerous_match[0]}"
            }

        # Verificar palavras-chave inadequadas
        inappropriate_match = PromptSecurityValidator._check_inappropriate_keywords(prompt)
        if inappropriate_match:
            return False, {
                "threat_level": SecurityThreatLevel.BLOCKED.value,
                "reason": "Conteúdo inadequado detectado",
                "details": f"Palavra-chave bloqueada: {inappropriate_match}"
            }

        # Verificar injeção em contexto de tarefas
        if PromptSecurityValidator._is_task_context_blocked(prompt):
            return False, {
                "threat_level": SecurityThreatLevel.CRITICAL.value,
                "reason": "Operação destrutiva em contexto de tarefas",
                "details": "Comando não permitido neste contexto"
            }

        # Verificar repetição excessiva (possível ataque de flooding)
        if PromptSecurityValidator._has_excessive_repetition(prompt):
            return False, {
                "threat_level": SecurityThreatLevel.WARNING.value,
                "reason": "Padrão de repetição excessiva",
                "details": "Possível tentativa de flooding"
            }

        # Verificar encoding suspeito (base64, hex)
        encoding_threat = PromptSecurityValidator._check_suspicious_encoding(prompt)
        if encoding_threat:
            return False, {
                "threat_level": SecurityThreatLevel.WARNING.value,
                "reason": encoding_threat,
                "details": "Conteúdo codificado suspeito"
            }

        return True, {
            "threat_level": SecurityThreatLevel.SAFE.value,
            "reason": "Prompt validado com sucesso",
            "details": "Nenhuma ameaça detectada"
        }

    @staticmethod
    def sanitize_prompt(prompt: str) -> str:
        """
        Remove/reduz conteúdo potencialmente perigoso sem destruir o prompt.
        """
        # Remove caracteres de controle
        prompt = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', prompt)

        # Remove múltiplos espaços em branco
        prompt = re.sub(r'\s+', ' ', prompt)

        # Remove sequências suspeitas de caracteres especiais
        prompt = re.sub(r'([!@#$%^&*()_+=\[\]{};:\'",.<>?/\\|`~]){5,}', r'\1\1\1', prompt)

        return prompt.strip()

    @staticmethod
    def _check_dangerous_patterns(prompt: str) -> Tuple[str, str] | None:
        """Detecta padrões perigosos conhecidos."""
        for pattern, description in PromptSecurityValidator.DANGEROUS_PATTERNS.items():
            if re.search(pattern, prompt):
                return pattern, description
        return None

    @staticmethod
    def _check_inappropriate_keywords(prompt: str) -> str | None:
        """Detecta palavras-chave inadequadas."""
        prompt_lower = prompt.lower()
        for keyword in PromptSecurityValidator.INAPPROPRIATE_KEYWORDS:
            if keyword in prompt_lower:
                return keyword
        return None

    @staticmethod
    def _is_task_context_blocked(prompt: str) -> bool:
        """Verifica bloqueios específicos do contexto de tarefas."""
        prompt_lower = prompt.lower()
        for blocked_term in PromptSecurityValidator.TASK_CONTEXT_BLOCKED:
            if blocked_term in prompt_lower:
                return True
        return False

    @staticmethod
    def _has_excessive_repetition(prompt: str) -> bool:
        """Detecta padrões repetitivos excessivos (flooding real - palavras repetidas)."""
        # Apenas detecta se a MESMA PALAVRA é repetida > 80% das vezes
        # Ignora caracteres únicos pois listas formatadas naturalmente têm muitos caracteres repetidos
        words = prompt.lower().split()
        
        if len(words) < 10:  # Prompts curtos não são flooding
            return False
        
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1

        max_count = max(word_counts.values()) if word_counts else 0
        
        # Só bloqueia se UMA PALAVRA representa > 80% do texto (flooding real)
        if max_count / len(words) > 0.8:
            return True

        return False

    @staticmethod
    def _check_suspicious_encoding(prompt: str) -> str | None:
        """Detecta encodings suspeitos (base64, hex)."""
        # Verificar base64 pattern
        if re.search(r'^[A-Za-z0-9+/]{20,}={0,2}$', prompt):
            try:
                import base64
                decoded = base64.b64decode(prompt).decode('utf-8')
                # Se conseguiu decodificar, pode ser suspeito
                if any(char in decoded.lower() for char in ['exec', 'eval', 'import', 'open']):
                    return "Base64 com conteúdo suspeito"
            except Exception:
                pass

        # Verificar hex pattern
        if re.match(r'^([0-9a-fA-F]{2})+$', prompt) and len(prompt) > 30:
            return "Encoding hexadecimal suspeito"

        return None

    @staticmethod
    def get_security_score(prompt: str) -> int:
        """Retorna score de segurança de 0 (máximo perigo) a 100 (completamente seguro)."""
        is_safe, details = PromptSecurityValidator.validate_prompt(prompt)

        if not is_safe:
            threat_level = details.get("threat_level")
            if threat_level == SecurityThreatLevel.BLOCKED.value:
                return 0
            elif threat_level == SecurityThreatLevel.CRITICAL.value:
                return 20
            elif threat_level == SecurityThreatLevel.WARNING.value:
                return 60
        else:
            return 100

        return 50


class PromptInjectionDetector:
    """Detecta tentativas de prompt injection avançadas."""

    @staticmethod
    def detect_role_playing_injection(prompt: str) -> bool:
        """Detecta tentativas de fazer IA mudar de papel."""
        patterns = [
            r"(?i)(you are now|you are a|pretend you are|act as|play the role)",
            r"(?i)(ignore your.*?instructions|forget your.*?guidelines)",
            r"(?i)(new instructions|updated rules|new rules)"
        ]

        for pattern in patterns:
            if re.search(pattern, prompt):
                return True
        return False

    @staticmethod
    def detect_context_confusion(prompt: str) -> bool:
        """Detecta tentativas de confundir o contexto."""
        patterns = [
            r"(?i)(in the hypothetical|imagine if|what if|suppose)",
            r"(?i)(from now on|as of now|starting now)",
            r"(?i)(disregard the context|ignore context)"
        ]

        for pattern in patterns:
            if re.search(pattern, prompt):
                return True
        return False

    @staticmethod
    def detect_hidden_instructions(prompt: str) -> bool:
        """Detecta instruções ocultas em formatos especiais."""
        # Verificar instruções em markdown
        if '```' in prompt and any(keyword in prompt.lower() for keyword in
                                    ['execute', 'run', 'eval', 'import']):
            return True

        # Verificar instruções em JSON
        try:
            if prompt.strip().startswith('{'):
                data = json.loads(prompt)
                if any(key in str(data).lower() for key in ['execute', 'system', 'cmd']):
                    return True
        except json.JSONDecodeError:
            pass

        return False

    @staticmethod
    def analyze_injection_risk(prompt: str) -> Dict:
        """Análise completa de risco de injeção."""
        return {
            "role_playing_detected": PromptInjectionDetector.detect_role_playing_injection(prompt),
            "context_confusion_detected": PromptInjectionDetector.detect_context_confusion(prompt),
            "hidden_instructions_detected": PromptInjectionDetector.detect_hidden_instructions(prompt),
            "overall_risk": any([
                PromptInjectionDetector.detect_role_playing_injection(prompt),
                PromptInjectionDetector.detect_context_confusion(prompt),
                PromptInjectionDetector.detect_hidden_instructions(prompt)
            ])
        }


def validate_and_sanitize_prompt(prompt: str, strict: bool = True) -> Tuple[bool, str, Dict]:
    """
    Valida e sanitiza um prompt.
    
    Args:
        prompt: Texto do prompt
        strict: Se True, rejeita prompts com warnings
    
    Returns:
        (aprovado, prompt_limpo, detalhes)
    """
    # Validação básica
    is_safe, details = PromptSecurityValidator.validate_prompt(prompt)

    # Detectar injeção avançada
    injection_analysis = PromptInjectionDetector.analyze_injection_risk(prompt)

    # Sanitizar
    clean_prompt = PromptSecurityValidator.sanitize_prompt(prompt)

    # Determinar aprovação final
    approved = is_safe and not injection_analysis["overall_risk"]

    if strict and not is_safe:
        approved = False

    # Combinar detalhes
    all_details = {
        **details,
        "injection_risk": injection_analysis,
        "clean_prompt": clean_prompt,
        "security_score": PromptSecurityValidator.get_security_score(prompt)
    }

    return approved, clean_prompt if approved else prompt, all_details
