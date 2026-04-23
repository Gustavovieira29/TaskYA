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

1. Crie uma chave de API Gemini na sua conta Google Cloud / Gemini.
2. Copie `.env.example` para `.env` e defina `GEMINI_API_KEY`.
3. Execute:

   ```bash
   pip install -r requirements.txt
   python gemini_check.py
   ```

O script fará uma chamada simples ao modelo Gemini e exibirá a resposta retornada.
