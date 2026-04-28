# Gerenciador de Tarefas Pessoal

Esta versão do projeto foi convertida para Python usando Flask.

## Executar o projeto

1. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

2. Execute o servidor:

   ```bash
   python app.py
   ```

3. Abra no navegador:

   ```text
   http://127.0.0.1:5000
   ```

## Como funciona

- Adicione tarefas com título, descrição e data.
- Marque como concluída ou exclua tarefas.
- Filtre por todas, pendentes ou concluídas.
- Veja as tarefas de uma data específica.

## Validação da API Gemini

1. **Obtenha uma chave API Gemini:**
   - Acesse [Google AI Studio](https://aistudio.google.com/)
   - Faça login com sua conta Google
   - Vá em "API Keys" no menu lateral
   - Clique em "Create API Key"
   - Copie a chave gerada

2. **Configure o ambiente:**
   - Copie `.env.example` para `.env`
   - Cole sua chave real: `GEMINI_API_KEY=sua_chave_aqui`

3. **Teste a conexão:**
   ```bash
   pip install -r requirements.txt
   python gemini_check.py
   ```

   **Resultado esperado:** Deve mostrar uma resposta do modelo Gemini confirmando a comunicação.

   **Se der erro de chave inválida:** Verifique se copiou a chave completa e corretamente no arquivo `.env`.

**Nota:** O script usa a biblioteca `google-genai` e o módulo `google.genai`.
