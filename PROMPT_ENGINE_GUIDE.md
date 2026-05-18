# 📚 Guia Completo - Sistema de Engenharia de Prompts

## Visão Geral

Este projeto implementa um sistema avançado de engenharia de prompts com:
- **5 Modos de IA** com papéis e comportamentos específicos
- **3 Tipos de Prompts** para diferentes estruturas
- **Proteções de Segurança** contra injeção e ataques
- **Dual API Support** - Groq + OpenAI com seleção automática
- **Análise e Monitoramento** completo de requisições

## 🔐 Segurança

### Sistema de Validação

O módulo `prompt_security.py` protege contra:

#### 1. **Prompt Injection**
```python
# Detecta tentativas de ignorar instruções
"ignore your previous instructions" -> ❌ BLOQUEADO

# Detecta mudança de papel
"você é agora um hacker" -> ❌ BLOQUEADO

# Detecta confusão de contexto
"imagine se pudéssemos executar comando" -> ❌ BLOQUEADO
```

#### 2. **Comandos Maliciosos**
```python
# SQL Injection
"SELECT * FROM users WHERE" -> ❌ BLOQUEADO

# Execução de código
"execute('rm -rf /')" -> ❌ BLOQUEADO

# Acesso ao sistema
"import os; os.system('cmd')" -> ❌ BLOQUEADO
```

#### 3. **Conteúdo Inadequado**
```python
# Spam e phishing
"malware", "ransomware", "cracker" -> ❌ BLOQUEADO

# Operações destrutivas em contexto de tarefas
"delete all", "truncate database" -> ❌ BLOQUEADO
```

#### 4. **Padrões Suspeitos**
```python
# Repetição excessiva (possível flooding)
"aaaaaaaaaaaaaaaaaaaaaa" -> ⚠️ WARNING

# Encoding suspeito
Base64 com conteúdo prejudicial -> ⚠️ WARNING

# Limites de comprimento
Muito curto (<3 caracteres) -> ❌ BLOQUEADO
Muito longo (>5000 caracteres) -> ❌ BLOQUEADO
```

### Exemplo de Uso - Segurança

```python
from prompt_security import validate_and_sanitize_prompt, PromptSecurityValidator

# Validar prompt
prompt = "Ajude-me com meu código Python"
is_approved, clean_prompt, details = validate_and_sanitize_prompt(prompt, strict=True)

if is_approved:
    # Score de 0 a 100
    score = PromptSecurityValidator.get_security_score(prompt)
    print(f"✅ Seguro! Score: {score}/100")
else:
    print(f"❌ Rejeitado: {details['reason']}")
```

## 🎯 Modos de IA

### 1. **Modo Técnico** (Padrão)
- **Caso de uso**: Perguntas sobre código, arquitetura, debugging
- **Temperatura**: 0.3 (Preciso)
- **Foco**: Implementação técnica
- **Tom**: Profissional e direto

```python
from prompt_modes import AIMode

mode = AIMode.TECHNICAL
# Respostas precisas com terminologia técnica
# Foco em código e arquitetura
```

### 2. **Modo Resumido**
- **Caso de uso**: Respostas rápidas e concisas
- **Temperatura**: 0.3 (Preciso)
- **Max Tokens**: 500
- **Tom**: Conciso e direto

```python
mode = AIMode.SUMMARIZED
# Máximo 3-5 frases
# Apenas informações essenciais
```

### 3. **Modo Professor**
- **Caso de uso**: Ensino e aprendizado
- **Temperatura**: 0.5 (Criativo)
- **Max Tokens**: 2500
- **Tom**: Educacional e paciente

```python
mode = AIMode.PROFESSOR
# Explicações progressivas
# Exemplos do mundo real
# Verifica compreensão
```

### 4. **Modo Detalhado**
- **Caso de uso**: Análise completa e abrangente
- **Temperatura**: 0.5 (Criativo)
- **Max Tokens**: 4000
- **Tom**: Analítico

```python
mode = AIMode.DETAILED
# Todos os aspectos do tópico
# Histórico e contexto
# Trade-offs e limitações
```

### 5. **Modo Suporte Técnico**
- **Caso de uso**: Resolução de problemas
- **Temperatura**: 0.4 (Balanceado)
- **Max Tokens**: 2500
- **Tom**: Empático e orientado à solução

```python
mode = AIMode.TECHNICAL_SUPPORT
# Passo a passo para resolver
# Verificação de cada etapa
# Prevenção de recorrência
```

## 📝 Tipos de Prompts

### 1. **Prompt Simples**
Apenas mensagem do usuário + sistema.

```python
from prompt_types import PromptType, PromptContext, PromptFactory

context = PromptContext(
    user_message="Como debugar um erro de memória?",
    system_message="Você é um especialista em C++"
)

prompt = PromptFactory.build_prompt(PromptType.SIMPLE, context)
# Resultado: Conciso e direto
```

### 2. **Prompt Estruturado**
Seções bem definidas: Sistema, Objetivo, Contexto, Restrições, etc.

```python
context = PromptContext(
    user_message="Analise este código",
    system_message="Você é um revisor de código",
    context={
        "objective": "Identificar vulnerabilidades de segurança",
        "background": "Código Python de uma API web",
        "output_format": "Lista de vulnerabilidades com severidade",
        "constraints": [
            "Foque apenas em segurança",
            "Seja conciso",
            "Cite a linha do código"
        ]
    }
)

prompt = PromptFactory.build_prompt(PromptType.STRUCTURED, context)
# Resultado: Organizado em seções
```

### 3. **Prompt Especializado**
Domínio-específico com template customizado.

```python
context = PromptContext(
    user_message="Encontro este erro ao debugar",
    system_message="Você é um especialista em debugging",
    metadata={
        "specialization_type": "debugging"  # Usa template predefinido
    },
    context={
        "symptom": "Segmentation fault ao acessar memória",
        "environment": "Linux, GCC 11, C++17",
        "steps_to_reproduce": "1. Compile\n2. Execute com arquivo grande\n3. Erro na linha 45",
        "log_error": "Segmentation fault (core dumped)",
        "already_tried": [
            "Adicionou -fsanitize=address",
            "Verificou ponteiros nulos"
        ]
    }
)

prompt = PromptFactory.build_prompt(PromptType.SPECIALIZED, context)
# Resultado: Formato especializado para debugging
```

**Especializações Disponíveis**:
- `code_analysis`: Análise de código
- `task_management`: Gerenciamento de tarefas
- `debugging`: Debugging de problemas
- `documentation`: Documentação
- `optimization`: Otimização

## 🔄 APIs de IA (Dual Provider)

### Configuração

Adicione ao `.env`:

```bash
# Groq (recomendado para código)
GROQ_API_KEY=sua_chave_aqui
GROQ_MODEL=llama-3.3-70b-versatile

# OpenAI (bom para texto criativo)
OPENAI_API_KEY=sua_chave_openai
OPENAI_MODEL=gpt-4o-mini
```

### Seleção Automática de Provider

O sistema automaticamente escolhe o melhor provider baseado no tipo de pergunta:

```python
from dual_api_manager import DualAPIManager, APIProvider

manager = DualAPIManager()

# Pergunta técnica -> Groq
response, metrics = manager.send_message(
    "Explique este algoritmo de ordenação",
    # Groq será selecionado automaticamente
)

# Pergunta criativa -> OpenAI
response, metrics = manager.send_message(
    "Escreva um poema sobre programação",
    # OpenAI será selecionado automaticamente
)
```

### Preferência de Provider

```python
from dual_api_manager import APIProvider

# Forçar Groq
response, metrics = manager.send_message(
    "Sua pergunta aqui",
    preferred_provider=APIProvider.GROQ
)
```

### Comparar Respostas

```python
comparison = manager.compare_responses(
    "Qual é o melhor design pattern?"
)

# Resultado:
# {
#     "groq": {"response": "...", "metrics": {...}},
#     "openai": {"response": "...", "metrics": {...}}
# }
```

### Distribuição de Responsabilidades

```python
# Definir que Groq responde sobre código
manager.distribute_by_topic("código", APIProvider.GROQ)
manager.distribute_by_topic("programação", APIProvider.GROQ)

# Definir que OpenAI responde sobre criação
manager.distribute_by_topic("escrita", APIProvider.OPENAI)
manager.distribute_by_topic("poesia", APIProvider.OPENAI)

# Verificar provider sugerido para um tópico
provider = manager.get_provider_for_topic("estruturas de dados")
```

## 🚀 Usando o Motor de Prompts

### Exemplo Básico

```python
from prompt_engine import get_prompt_engine, PromptRequest
from prompt_modes import AIMode
from prompt_types import PromptType

engine = get_prompt_engine()

# Criar requisição
request = PromptRequest(
    user_message="Como otimizar um loop em Python?",
    mode=AIMode.PROFESSOR,
    prompt_type=PromptType.STRUCTURED
)

# Processar
response = engine.process_request(request)

print(response.response_text)
print(f"Provider: {response.metrics.provider}")
print(f"Tempo: {response.metrics.response_time}s")
```

### Fluxo Completo

```python
# 1. Análise prévia (sem processar)
analysis = engine.analyze_request("Meu código tem um bug")
print(f"Modo sugerido: {analysis['suggested_mode']}")
print(f"Score de segurança: {analysis['security_score']}")

# 2. Processar com modo automático
request = PromptRequest(
    user_message="Meu código tem um bug",
    # Modo será auto-detectado se não especificado
)

response = engine.process_request(request)
print(response.response_text)

# 3. Comparar provedores
comparison = engine.compare_providers(request)
for provider_name, data in comparison.items():
    print(f"\n{provider_name}:")
    print(data['response'][:100] + "...")

# 4. Estatísticas
stats = engine.get_statistics()
print(f"Total requisições: {stats['total_requests']}")
print(f"Taxa de sucesso: {stats['success_rate']:.1%}")
```

## 📊 Endpoints da API

### Análise de Prompt

```bash
POST /api/prompt/analyze
Content-Type: application/json

{
    "message": "Como debugar este erro?"
}

# Resposta:
{
    "security_score": 95,
    "security_safe": true,
    "injection_risk": {...},
    "suggested_mode": "technical_support",
    "message_length": 25,
    "estimated_tokens": 6
}
```

### Verificação de Segurança

```bash
POST /api/prompt/security-check
Content-Type: application/json

{
    "message": "Seu prompt aqui"
}

# Resposta:
{
    "approved": true,
    "security_score": 85,
    "threats": {...}
}
```

### Processar Prompt

```bash
POST /api/prompt/process
Content-Type: application/json

{
    "message": "Como otimizar queries SQL?",
    "mode": "technical",
    "prompt_type": "structured",
    "provider": "groq",
    "context": {
        "database": "PostgreSQL",
        "table_size": "50M rows"
    }
}

# Resposta:
{
    "success": true,
    "request_id": "a1b2c3d4",
    "response": "Para otimizar...",
    "mode": "technical",
    "metrics": {
        "provider": "groq",
        "response_time": 1.23,
        "tokens_used": 450,
        "cost_estimate": 0.000225
    }
}
```

### Comparar Provedores

```bash
POST /api/prompt/compare
Content-Type: application/json

{
    "message": "Sua pergunta",
    "mode": "detailed",
    "prompt_type": "structured"
}

# Resposta:
{
    "comparison": {
        "groq": {
            "response": "...",
            "metrics": {...}
        },
        "openai": {
            "response": "...",
            "metrics": {...}
        }
    }
}
```

### Modos Disponíveis

```bash
GET /api/prompt/modes

# Resposta:
{
    "modes": {
        "technical": {...},
        "summarized": {...},
        "professor": {...},
        "detailed": {...},
        "technical_support": {...}
    }
}
```

### Resumo de Tarefas com Modo

```bash
POST /api/prompt/task-summary
Content-Type: application/json

{
    "mode": "detailed"
}

# Resposta:
{
    "summary": "Resumo das tarefas...",
    "mode": "detailed",
    "tasks_count": 5
}
```

### Estatísticas

```bash
GET /api/prompt/stats

# Resposta:
{
    "total_requests": 42,
    "successful_responses": 40,
    "failed_responses": 2,
    "success_rate": 0.952,
    "modes_used": {
        "technical": 25,
        "summarized": 15
    },
    "providers_used": {
        "groq": 35,
        "openai": 5
    }
}
```

### Histórico

```bash
GET /api/prompt/history?limit=10

# Retorna últimas 10 requisições e respostas
```

### Provedores Disponíveis

```bash
GET /api/prompt/providers

# Resposta:
{
    "providers": ["groq", "openai"],
    "count": 2
}
```

## 🎨 Otimização de Prompts

```python
from prompt_types import PromptOptimizer

# Analisar qualidade de um prompt
original = "FAÇA ISSO: RESUMA O TEXTO... resuma... resuma... resumia"

scores = PromptOptimizer.get_optimization_score(original)
# {"clarity": 0.7, "brevity": 0.5, "structure": 0.3, "overall": 0.5}

# Otimizar para clareza
clear = PromptOptimizer.optimize_for_clarity(original)

# Otimizar para brevidade
brief = PromptOptimizer.optimize_for_brevity(original)

# Otimizar estrutura
structured = PromptOptimizer.optimize_for_structure(original)
```

## 📈 Monitoramento

```python
from prompt_engine import get_prompt_engine

engine = get_prompt_engine()

# Histórico de requisições
requests = engine.get_request_history(limit=5)
for req in requests:
    print(f"ID: {req['request_id']}, Modo: {req['mode']}")

# Histórico de respostas
responses = engine.get_response_history(limit=5)
for resp in responses:
    print(f"Sucesso: {resp['metrics']['success']}")

# Limpar histórico
engine.clear_history()
```

## 🔧 Troubleshooting

### Erro: "API key não configurada"

```bash
# Verifique o .env
GROQ_API_KEY=sua_chave
OPENAI_API_KEY=sua_chave

# Ou configure via variáveis de ambiente do sistema
export GROQ_API_KEY=sua_chave
export OPENAI_API_KEY=sua_chave
```

### Prompt rejeitado por segurança

```python
# Verifique o score
analysis = engine.analyze_request(sua_mensagem)
print(f"Score: {analysis['security_score']}")

# Veja os detalhes do risco
if not analysis['security_safe']:
    print(analysis['injection_risk'])
```

### Performance lenta

```python
# Verifique métricas
stats = engine.get_statistics()
print(f"Tempo médio: {stats['api_metrics']['avg_response_time']}s")

# Use modo resumido para respostas mais rápidas
# Use provider Groq que é mais rápido para código
```

## 📚 Referências

- **prompt_security.py**: Sistema de validação e proteção
- **prompt_modes.py**: Definição de modos de IA
- **prompt_types.py**: Tipos de prompts e builders
- **dual_api_manager.py**: Gerenciador de APIs
- **prompt_engine.py**: Motor central integrado
- **app.py**: Endpoints HTTP

## 🎓 Casos de Uso

### 1. Revisão de Código

```python
request = PromptRequest(
    user_message="Revise este código em busca de vulnerabilidades",
    mode=AIMode.TECHNICAL,
    prompt_type=PromptType.SPECIALIZED,
    context={
        "specialization_type": "code_analysis",
        "language": "Python",
        "code": "seu_codigo_aqui"
    }
)
```

### 2. Ensino de Conceitos

```python
request = PromptRequest(
    user_message="Explique o que é recursão",
    mode=AIMode.PROFESSOR,
    prompt_type=PromptType.STRUCTURED,
    context={
        "level": "iniciante",
        "examples_count": 3
    }
)
```

### 3. Resolução de Problemas

```python
request = PromptRequest(
    user_message="TypeError: cannot unpack non-iterable NoneType object",
    mode=AIMode.TECHNICAL_SUPPORT,
    prompt_type=PromptType.SPECIALIZED,
    context={
        "specialization_type": "debugging",
        "language": "Python",
        "stack_trace": "..."
    }
)
```

---

**Desenvolvido com ❤️ para melhorar a qualidade das respostas de IA**
