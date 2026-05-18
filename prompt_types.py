"""Tipos de estruturas de prompts: simples, estruturado e especializado."""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import json


class PromptType(Enum):
    """Tipos de prompts disponíveis."""
    SIMPLE = "simple"
    STRUCTURED = "structured"
    SPECIALIZED = "specialized"


@dataclass
class PromptContext:
    """Contexto para construção de prompts."""
    user_message: str
    system_message: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "user_message": self.user_message,
            "system_message": self.system_message,
            "context": self.context or {},
            "metadata": self.metadata or {},
        }


class PromptBuilder(ABC):
    """Classe base para construtores de prompts."""

    @abstractmethod
    def build(self, context: PromptContext) -> str:
        """Constrói o prompt."""
        pass

    @abstractmethod
    def validate(self, prompt: str) -> bool:
        """Valida o prompt construído."""
        pass


class SimplePromptBuilder(PromptBuilder):
    """Constrói prompts simples e diretos."""

    def build(self, context: PromptContext) -> str:
        """
        Constrói um prompt simples.
        
        Formato: [Sistema] + [Mensagem do usuário]
        """
        parts = []

        if context.system_message:
            parts.append(context.system_message)

        parts.append(context.user_message)

        return "\n".join(parts)

    def validate(self, prompt: str) -> bool:
        """Valida prompt simples."""
        return len(prompt.strip()) > 0 and len(prompt) < 2000


class StructuredPromptBuilder(PromptBuilder):
    """Constrói prompts com estrutura definida."""

    def build(self, context: PromptContext) -> str:
        """
        Constrói um prompt estruturado com seções bem definidas.
        
        Formato:
        [SISTEMA]
        [OBJETIVO]
        [ENTRADA]
        [CONTEXTO]
        [FORMATO DE SAÍDA]
        [RESTRIÇÕES]
        [MENSAGEM DO USUÁRIO]
        """
        sections = []

        # Seção de sistema
        if context.system_message:
            sections.append(f"[SISTEMA]\n{context.system_message}\n")

        # Objetivo (extraído do contexto)
        if context.context and "objective" in context.context:
            sections.append(f"[OBJETIVO]\n{context.context['objective']}\n")

        # Contexto
        if context.context and "background" in context.context:
            sections.append(f"[CONTEXTO]\n{context.context['background']}\n")

        # Formato de saída
        if context.context and "output_format" in context.context:
            sections.append(f"[FORMATO DE SAÍDA]\n{context.context['output_format']}\n")

        # Restrições
        if context.context and "constraints" in context.context:
            constraints = context.context['constraints']
            if isinstance(constraints, list):
                constraints_text = "\n".join(f"- {c}" for c in constraints)
            else:
                constraints_text = str(constraints)
            sections.append(f"[RESTRIÇÕES]\n{constraints_text}\n")

        # Mensagem do usuário
        sections.append(f"[PERGUNTA]\n{context.user_message}")

        return "".join(sections)

    def validate(self, prompt: str) -> bool:
        """Valida prompt estruturado."""
        required_markers = ["[PERGUNTA]"]
        has_markers = all(marker in prompt for marker in required_markers)
        return has_markers and len(prompt) > 100 and len(prompt) < 5000


class SpecializedPromptBuilder(PromptBuilder):
    """Constrói prompts especializados com campos específicos e validações."""

    # Templates especializados por domínio
    TEMPLATES = {
        "code_analysis": {
            "title": "Análise de Código",
            "sections": [
                "LINGUAGEM",
                "OBJETIVO",
                "CÓDIGO",
                "PROBLEMAS ESPERADOS",
                "FORMATO DE SAÍDA"
            ]
        },
        "task_management": {
            "title": "Gerenciamento de Tarefas",
            "sections": [
                "TAREFA",
                "STATUS ATUAL",
                "CONTEXTO",
                "AÇÃO SOLICITADA",
                "PRIORIDADE",
                "RESTRIÇÕES"
            ]
        },
        "debugging": {
            "title": "Debugging",
            "sections": [
                "SINTOMA",
                "AMBIENTE",
                "PASSOS PARA REPRODUZIR",
                "LOG/ERRO",
                "O QUE JÁ FOI TENTADO",
                "FORMATO DE RESPOSTA"
            ]
        },
        "documentation": {
            "title": "Documentação",
            "sections": [
                "TIPO",
                "PÚBLICO-ALVO",
                "TÓPICO",
                "PROFUNDIDADE",
                "FORMATO",
                "EXEMPLOS NECESSÁRIOS"
            ]
        },
        "optimization": {
            "title": "Otimização",
            "sections": [
                "COMPONENTE",
                "MÉTRICA ATUAL",
                "MÉTRICA ALVO",
                "RESTRIÇÕES",
                "CONTEXTO",
                "FORMATO DE SAÍDA"
            ]
        }
    }

    def build(self, context: PromptContext) -> str:
        """
        Constrói um prompt especializado.
        
        Requer contexto com 'specialization_type' para usar template apropriado.
        """
        sections = []

        # Sistema
        if context.system_message:
            sections.append(f"╔═══ SISTEMA ═══╗\n{context.system_message}\n")

        # Tipo de especialização
        specialization = context.metadata.get("specialization_type") if context.metadata else None

        if specialization and specialization in self.TEMPLATES:
            template = self.TEMPLATES[specialization]
            sections.append(f"╔═══ {template['title'].upper()} ═══╗\n")

            # Preencher seções do template com dados do contexto
            if context.context:
                for section in template['sections']:
                    section_key = section.lower().replace(" ", "_")
                    if section_key in context.context:
                        sections.append(f"\n[{section}]\n{context.context[section_key]}")
        else:
            # Usar contexto geral se disponível
            if context.context:
                for key, value in context.context.items():
                    if isinstance(value, (str, int, float)):
                        sections.append(f"\n[{key.upper().replace('_', ' ')}]\n{value}")
                    elif isinstance(value, list):
                        items = "\n".join(f"  • {item}" for item in value)
                        sections.append(f"\n[{key.upper().replace('_', ' ')}]\n{items}")

        # Mensagem do usuário como pergunta final
        sections.append(f"\n╔═══ PERGUNTA ═══╗\n{context.user_message}")

        return "".join(sections)

    def validate(self, prompt: str) -> bool:
        """Valida prompt especializado."""
        has_markers = any(marker in prompt for marker in ["[", "╔", "SISTEMA", "PERGUNTA"])
        has_substance = len(prompt) > 150
        return has_markers and has_substance and len(prompt) < 6000

    @staticmethod
    def get_available_specializations() -> Dict[str, str]:
        """Retorna especializações disponíveis."""
        return {
            key: template['title']
            for key, template in SpecializedPromptBuilder.TEMPLATES.items()
        }


class PromptFactory:
    """Factory para criar builders de prompts."""

    BUILDERS = {
        PromptType.SIMPLE: SimplePromptBuilder(),
        PromptType.STRUCTURED: StructuredPromptBuilder(),
        PromptType.SPECIALIZED: SpecializedPromptBuilder(),
    }

    @classmethod
    def get_builder(cls, prompt_type: PromptType) -> PromptBuilder:
        """Obtém builder para o tipo de prompt."""
        return cls.BUILDERS.get(prompt_type, cls.BUILDERS[PromptType.SIMPLE])

    @classmethod
    def build_prompt(cls, prompt_type: PromptType, context: PromptContext) -> str:
        """Constrói prompt usando tipo especificado."""
        builder = cls.get_builder(prompt_type)
        return builder.build(context)

    @classmethod
    def build_and_validate(cls, prompt_type: PromptType, context: PromptContext) -> tuple[bool, str]:
        """Constrói e valida prompt."""
        builder = cls.get_builder(prompt_type)
        prompt = builder.build(context)
        is_valid = builder.validate(prompt)
        return is_valid, prompt


class PromptOptimizer:
    """Otimiza prompts para melhor performance."""

    @staticmethod
    def optimize_for_clarity(prompt: str) -> str:
        """Otimiza prompt para clareza."""
        # Remove linhas em branco excessivas
        lines = prompt.split('\n')
        cleaned = [line.strip() for line in lines if line.strip()]
        return '\n'.join(cleaned)

    @staticmethod
    def optimize_for_brevity(prompt: str) -> str:
        """Otimiza prompt para ser mais breve."""
        # Remove redundâncias
        prompt = PromptOptimizer.optimize_for_clarity(prompt)

        # Remove palavras-chave redundantes
        redundant_phrases = [
            "por favor", "se possível", "if possible",
            "obrigado", "muito obrigado", "thanks",
            "ajude-me", "me ajude"
        ]

        prompt_lower = prompt.lower()
        for phrase in redundant_phrases:
            prompt = prompt.replace(phrase, "").replace(phrase.capitalize(), "")

        return prompt.strip()

    @staticmethod
    def optimize_for_structure(prompt: str) -> str:
        """Otimiza prompt com melhor estrutura visual."""
        lines = prompt.split('\n')
        optimized = []

        for line in lines:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                # Adiciona separador visual
                optimized.append(f"\n### {line}")
            elif line.startswith('-'):
                # Mantém bullet points
                optimized.append(f"  {line}")
            elif line:
                optimized.append(line)

        return '\n'.join(optimized)

    @staticmethod
    def get_optimization_score(prompt: str) -> Dict[str, float]:
        """Calcula score de otimização."""
        scores = {
            "clarity": 0.0,
            "brevity": 0.0,
            "structure": 0.0,
            "overall": 0.0
        }

        # Clarity: linhas devem ser claras, sem redundância
        lines = prompt.split('\n')
        clarity_score = min(len([l for l in lines if l.strip()]) / 10, 1.0)
        scores["clarity"] = clarity_score

        # Brevity: não deve ser muito longo
        brevity_score = max(1.0 - (len(prompt) / 2000), 0.0)
        scores["brevity"] = brevity_score

        # Structure: deve ter marcadores de seção
        structure_markers = sum(1 for line in lines if line.strip().startswith('['))
        structure_score = min(structure_markers / 3, 1.0)
        scores["structure"] = structure_score

        # Overall: média dos scores
        scores["overall"] = sum([scores["clarity"], scores["brevity"], scores["structure"]]) / 3

        return scores
