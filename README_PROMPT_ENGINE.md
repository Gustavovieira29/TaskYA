# 🚀 TaskYA - Gerenciador de Tarefas com Engenharia de Prompts Avançada

Uma aplicação web moderna de gerenciamento de tarefas com integração inteligente de APIs de IA, sistema avançado de engenharia de prompts e proteções de segurança robustas.

## ✨ Recursos Principais

### 🎯 Engenharia de Prompts Avançada

- **5 Modos de IA**: Técnico, Resumido, Professor, Detalhado, Suporte Técnico
- **3 Tipos de Prompts**: Simples, Estruturado, Especializado
- **Auto-detecção de Modo**: Detecta automaticamente o melhor modo baseado na pergunta
- **Otimização de Prompts**: Melhora clareza, brevidade e estrutura

### 🔐 Segurança Robusta

- **Proteção contra Prompt Injection**: Detecta tentativas de contorno de instruções
- **Detecção de Malware**: Bloqueia conteúdo prejudicial
- **Validação de Padrões**: Identifica comportamentos suspeitos
- **Rate Limiting**: Protege contra abuso
- **Sanitização**: Limpa prompts sem destruir conteúdo legítimo

### 🔄 Dual API Support

- **Groq API**: Otimizada para código e programação (Llama 3.3 70B)
- **OpenAI API**: Excelente para texto criativo (GPT-4o mini)
- **Seleção Automática**: Escolhe o melhor provider para cada tipo de pergunta
- **Comparação de Respostas**: Compara respostas de múltiplas APIs
- **Distribuição de Responsabilidades**: Define qual API responde sobre cada tópico

### 📊 Monitoramento e Análise

- **Histórico Completo**: Rastreia todas as requisições e respostas
- **Métricas de Performance**: Tempo de resposta, tokens usados, estimativa de custo
- **Estatísticas de Uso**: Modo mais usado, provider mais confiável, taxa de sucesso
- **Análise Prévia**: Analisa pergunta sem processar

### 🌐 API REST Completa

Endpoints para:
- Processar prompts com modo e tipo especificados
- Comparar provedores
- Analisar segurança
- Gerar resumos de tarefas
- Consultar estatísticas
- Gerenciar histórico

## 🛠️ Instalação

### Pré-requisitos

- Python 3.8+
- pip ou conda
- Chaves de API (Groq e/ou OpenAI)

### Setup

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd TaskYA
```

2. **Crie um ambiente virtual**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
# Crie um arquivo .env na raiz do projeto
GROQ_API_KEY=sua_chave_groq_aqui
GROQ_MODEL=llama-3.3-70b-versatile

# Opcional: OpenAI
OPENAI_API_KEY=sua_chave_openai_aqui
OPENAI_MODEL=gpt-4o-mini
```

5. **Execute a aplicação**
```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

## 📖 Guia de Uso

### Usando o Navegador

1. **Homepage**: Veja e gerencie suas tarefas
2. **Gerar Resumo**: Clique em "Gerar Resumo" para obter um resumo IA-powered

### Usando a API REST

#### Exemplo 1: Processar um prompt

```bash
curl -X POST http://localhost:5000/api/prompt/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Como otimizar um loop em Python?",
    "mode": "technical",
    "prompt_type": "structured"
  }'
```

#### Exemplo 2: Comparar provedores

```bash
curl -X POST http://localhost:5000/api/prompt/compare \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Qual é o melhor design pattern?",
    "mode": "detailed"
  }'
```

#### Exemplo 3: Verificar segurança

```bash
curl -X POST http://localhost:5000/api/prompt/security-check \
  -H "Content-Type: application/json" \
  -d '{"message": "Sua pergunta aqui"}'
```

### Usando Python

```python
from prompt_engine import get_prompt_engine, PromptRequest
from prompt_modes import AIMode
from prompt_types import PromptType

engine = get_prompt_engine()

# Criar requisição
request = PromptRequest(
    user_message="Como debugar um erro em C++?",
    mode=AIMode.TECHNICAL,
    prompt_type=PromptType.STRUCTURED
)

# Processar
response = engine.process_request(request)
print(response.response_text)
```

## 📁 Estrutura do Projeto

```
TaskYA/
├── app.py                          # Aplicação Flask principal
├── prompt_engine.py                # Motor de prompts integrado
├── prompt_security.py              # Sistema de segurança
├── prompt_modes.py                 # 5 modos de IA
├── prompt_types.py                 # Tipos de prompts
├── dual_api_manager.py             # Gerenciador de APIs
├── database.py                     # Modelo de dados
├── audit_log.py                    # Log de auditoria
├── gemini_utils.py                 # Utilidades de rate limiting
├── PROMPT_ENGINE_GUIDE.md          # Guia completo do motor
├── examples_prompt_engine.py       # Exemplos práticos
├── requirements.txt                # Dependências Python
├── templates/
│   └── index.html                  # Interface web
├── static/
│   └── style.css                   # Estilos CSS
└── instance/
    └── tasks.db                    # Banco de dados SQLite
```

## 🔑 Arquivos Principais Explicados

### prompt_security.py
- `PromptSecurityValidator`: Valida contra injeção, malware, padrões suspeitos
- `PromptInjectionDetector`: Detecta tentativas avançadas de injeção
- `validate_and_sanitize_prompt()`: Função principal de validação

### prompt_modes.py
- `AIMode`: Enum com 5 modos
- `ModeConfig`: Configuração de cada modo com system prompt
- `ModeSelector`: Sugere modo baseado na entrada do usuário

### prompt_types.py
- `PromptType`: Enum com 3 tipos
- `PromptBuilder`: Classes para construir cada tipo
- `PromptFactory`: Factory para criar prompts
- `PromptOptimizer`: Otimiza prompts

### dual_api_manager.py
- `AIAPIClient`: Interface base para clientes de API
- `GroqAPIClient` e `OpenAIAPIClient`: Implementações específicas
- `DualAPIManager`: Gerencia múltiplas APIs
- `APIResponseMetrics`: Rastreia métricas de resposta

### prompt_engine.py
- `PromptRequest`: Representa uma requisição
- `PromptResponse`: Representa uma resposta
- `PromptEngine`: Orquestra todo o fluxo

## 🔒 Segurança

### Padrões Detectados

- **Prompt Injection**: "ignore suas instruções", "você é agora um hacker"
- **SQL Injection**: "SELECT * FROM users WHERE"
- **Execução de Código**: "execute('rm -rf /')", "import os"
- **Acesso ao Sistema**: "sistema", "shell", "bash", "administrator"
- **Conteúdo Malicioso**: "malware", "ransomware", "botnet", "exploit"

### Score de Segurança

- 0-20: 🔴 Crítico
- 20-50: 🟠 Aviso
- 50-75: 🟡 Cauteloso
- 75-100: 🟢 Seguro

## 📊 Comparação de Modos

| Modo | Caso de Uso | Temperatura | Max Tokens | Tom |
|------|------------|------------|-----------|-----|
| **Técnico** | Código, arquitetura | 0.3 | 2000 | Profissional |
| **Resumido** | Respostas rápidas | 0.3 | 500 | Conciso |
| **Professor** | Ensino e aprendizado | 0.5 | 2500 | Educacional |
| **Detalhado** | Análise completa | 0.5 | 4000 | Analítico |
| **Suporte** | Resolução de problemas | 0.4 | 2500 | Empático |

## 💡 Casos de Uso

### 1. Desenvolvimento de Software
```python
request = PromptRequest(
    user_message="Revise este código em busca de bugs",
    mode=AIMode.TECHNICAL,
    prompt_type=PromptType.SPECIALIZED,
    context={"specialization_type": "code_analysis"}
)
```

### 2. Educação
```python
request = PromptRequest(
    user_message="Explique o que é Big O notation",
    mode=AIMode.PROFESSOR,
    prompt_type=PromptType.STRUCTURED
)
```

### 3. Suporte Técnico
```python
request = PromptRequest(
    user_message="Recebi um erro 500 na API",
    mode=AIMode.TECHNICAL_SUPPORT,
    prompt_type=PromptType.SPECIALIZED,
    context={"specialization_type": "debugging"}
)
```

## 🚀 Performance

- **Resposta Rápida**: ~1-2s com Groq, ~2-3s com OpenAI
- **Custo Eficiente**: Groq é ~10x mais barato que OpenAI
- **Alta Disponibilidade**: Suporta failover automático entre APIs

## 📝 Exemplos Adicionais

Veja `examples_prompt_engine.py` para 10 exemplos práticos:

1. Uso Básico
2. Auto-detecção de Modo
3. Validação de Segurança
4. Tipos de Prompts
5. Comparação de Provedores
6. Todos os Modos
7. Contexto Especializado
8. Análise Prévia
9. Estatísticas
10. Distribuição Dual API

Execute com:
```bash
python examples_prompt_engine.py
```

## 🐛 Troubleshooting

### Erro: "API key não configurada"
→ Verifique o arquivo `.env` e as variáveis de ambiente

### Prompt rejeitado por segurança
→ Use `/api/prompt/analyze` para ver o score de segurança

### Performance lenta
→ Use modo `SUMMARIZED` ou provider `GROQ`

## 📚 Documentação

- [Guia Completo do Motor de Prompts](PROMPT_ENGINE_GUIDE.md)
- [Exemplos Práticos](examples_prompt_engine.py)
- [API REST Endpoints](#-endpoints-da-api)

## 🤝 Contribuindo

Para contribuir:
1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

## 👨‍💻 Autor

Desenvolvido com ❤️ como solução completa de engenharia de prompts para TaskYA

## 🌟 Features Futuras

- [ ] Persistência de histórico de prompts
- [ ] Análise de qualidade de respostas
- [ ] Dashboard de análise visual
- [ ] Integração com Claude Anthropic
- [ ] Cache inteligente de respostas
- [ ] Webhooks para notificações
- [ ] Export de histórico
- [ ] Multi-usuário com autenticação

## 📞 Suporte

Para questões, problemas ou sugestões, abra uma issue no repositório.

---

**Last Updated**: Maio 2026  
**Versão**: 1.0.0  
**Status**: ✅ Produção
