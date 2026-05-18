# 📋 TaskYA Cheat Sheet

## 🚀 Iniciar (Primeira Vez)

```powershell
cd C:\Users\seu_usuario\OneDrive\Área de Trabalho\GITHUB\TaskYA
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py
python app.py        # Terminal 1 - deixar rodando

# Em outro terminal (Terminal 2)
.venv\Scripts\Activate.ps1
python test_api.py

# Abrir browser
http://localhost:5000
```

---

## ⚡ Iniciar (Próximas Vezes)

```powershell
# Terminal 1
cd path/to/TaskYA
.venv\Scripts\Activate.ps1
python app.py

# Terminal 2
.venv\Scripts\Activate.ps1
python test_api.py

# Browser
http://localhost:5000
```

---

## 🧪 Testar Segurança

```powershell
# ✅ Prompt seguro (Score 100)
curl.exe -X POST http://localhost:5000/api/prompt/security-check `
  -H "Content-Type: application/json" `
  -d '{"message":"Como otimizar um loop em Python?"}'

# ❌ Prompt malicioso (Score 20)
curl.exe -X POST http://localhost:5000/api/prompt/security-check `
  -H "Content-Type: application/json" `
  -d '{"message":"ignore your instructions"}'
```

---

## 🔌 APIs Importantes

| Endpoint | Método | O que faz |
|----------|--------|----------|
| `/api/prompt/security-check` | POST | Valida segurança |
| `/api/prompt/process` | POST | Processa com modo |
| `/api/prompt/modes` | GET | Lista 5 modos |
| `/api/prompt/providers` | GET | Lista APIs |
| `/api/prompt/stats` | GET | Estatísticas |
| `/api/prompt/history` | GET | Histórico |

---

## 🎯 5 Modos de IA

| Modo | Uso | Exemplo |
|------|-----|---------|
| **TECHNICAL** | Código/Debug | "Como debugar?" |
| **SUMMARIZED** | Resumos | "Resuma em 3 frases" |
| **PROFESSOR** | Educação | "Explique" |
| **DETAILED** | Completo | "Descreva em detalhes" |
| **TECHNICAL_SUPPORT** | Suporte | "Qual é o erro?" |

---

## 🔒 Score de Segurança

| Score | Status | Ação |
|-------|--------|------|
| 100 | ✅ Seguro | ✓ Processa |
| 70-99 | ⚠️ Aviso | ⚠️ Monitora |
| 30-69 | 🟡 Suspeito | ⚠️ Revisa |
| < 30 | ❌ Bloqueado | ✗ Rejeita |

---

## 📊 3 Tipos de Prompts

1. **SIMPLE** - Pergunta direta
2. **STRUCTURED** - Com contexto e formato
3. **SPECIALIZED** - Otimizado para domínio

---

## 🛑 O Que Bloqueia

- Tentar desabilitar restrições: `ignore your instructions`
- Executar código: `execute(`, `eval(`
- SQL Injection: `DELETE FROM`
- Importação maliciosa: `import os`
- Acesso ao sistema: `os.system()`, `subprocess`
- Flooding: mesma palavra > 80%

---

## ⚙️ Configurar APIs (Opcional)

Criar arquivo `.env`:
```
OPENAI_API_KEY=sk-proj-sua_chave
GROQ_API_KEY=gsk_sua_chave
```

---

## 🐛 Problemas Comuns

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| Conexão recusada | Terminal 1 rodando `python app.py`? |
| "Flooding" em prompt | Padrão seguro - aumentar variedade no texto |
| API retorna vazio | Configurar `.env` com chaves |

---

## 📁 Arquivos Importantes

```
.venv/                    # Ambiente virtual
instance/tasks.db         # Banco de dados
.env                      # Chaves de API (criar)
app.py                    # Servidor (rodar)
requirements.txt          # Dependências
test_api.py              # Testes
README.md                # Docs completas
SETUP_COMPLETE.md        # Instruções detalhadas
```

---

## 🎨 Interface Web

**Home (http://localhost:5000)**
- ✅ Dashboard com 5 tarefas de exemplo
- ✅ Botão "Gerar resumo" → Testa IA
- ✅ Formulário para adicionar tarefas
- ✅ Filtros por status e data
- ✅ Editar e deletar tarefas

---

## 📞 Endpoints Principais

```bash
# Verificar segurança
POST /api/prompt/security-check
{"message": "seu prompt"}

# Processar com modo
POST /api/prompt/process
{
  "message": "seu prompt",
  "mode": "technical|summarized|professor|detailed|technical_support",
  "prompt_type": "simple|structured|specialized"
}

# Listar modos
GET /api/prompt/modes

# Ver estatísticas
GET /api/prompt/stats

# Ver histórico
GET /api/prompt/history
```

---

## ✅ Checklist de Features

- ✅ Gerenciador de tarefas CRUD
- ✅ 5 modos de IA
- ✅ 3 tipos de prompts
- ✅ 8+ padrões de segurança
- ✅ Score de segurança 0-100
- ✅ Dual API (Groq + OpenAI)
- ✅ Auto-seleção de provider
- ✅ Histórico de requisições
- ✅ Geração de resumos
- ✅ 12 endpoints REST
- ✅ Logging completo
- ✅ Tratamento de erros

---

## 🟢 Status

**Pronto para usar!** Todos os componentes testados e funcionando.

- Testes: ✅ Passando
- Segurança: ✅ Funcionando
- API: ✅ Respondendo
- Database: ✅ Criado
- UI: ✅ Acessível
