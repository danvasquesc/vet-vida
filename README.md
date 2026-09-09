# VETVIDA - SISTEMA WEB DE CLÍNICA VETERINÁRIA

## Projeto Integrador Extensionista - ADS 3

<br>

### 1. TECNOLOGIAS UTILIZADAS

- Front-end: HTML5, CSS3 e JavaScript puro
- Back-end / API: Python 3 (bibliotecas nativas do Python)
- Banco de dados: SQLite + SQL
<br>

IMPORTANTE: não é necessário instalar MySQL, XAMPP, Docker, Flask ou qualquer biblioteca externa.
O SQLite já vem junto com o Python e o arquivo do banco é criado automaticamente.

<br>

###  2. COMO EXECUTAR NO WINDOWS / VS CODE

Opção mais simples:
1. Extraia a pasta do projeto.
2. Abra a pasta no VS Code.
3. Dê duplo clique em INICIAR.bat ou execute no terminal:

   ```python backend/server.py```

   Caso "python" não funcione, tente:<br>
   ```py backend/server.py```

4. Abra o navegador em:
   ```http://127.0.0.1:8000```

5. Para encerrar o servidor, pressione CTRL+C no terminal.

<br>

### 3. FUNCIONALIDADES

- Cadastro de animais <br>
- Registro de serviços realizados (consulta, exame, vacina, cirurgia etc.) <br>
- Consulta do histórico de serviços por animal <br>
- Painel com indicadores simples <br>
- Persistência em banco de dados SQLite <br>

<br>

### 4. ESTRUTURA DO PROJETO

frontend/<br>
  index.html      -> estrutura das telas
  styles.css      -> estilos visuais
  app.js          -> interação com a API

backend/<br>
  server.py       -> servidor web e API REST

database/<br>
  schema.sql      -> criação das tabelas SQL
  seed.sql        -> dados de exemplo
  vetclinic.db    -> criado automaticamente na primeira execução

documentacao.pdf -> documentação do trabalho

<br>

### 5. ROTAS PRINCIPAIS DA API

GET  /api/animals               -> lista os animais <br>
POST /api/animals               -> cadastra um animal <br>
GET  /api/services              -> lista os serviços <br>
POST /api/services              -> registra um serviço <br>
GET  /api/animals/{id}/history  -> histórico de um animal <br>
GET  /api/stats                 -> indicadores do painel <br>

<br>

### 6. DADOS DE EXEMPLO

Na primeira execução o sistema cadastra automaticamente alguns animais e serviços de demonstração, apenas para facilitar os testes e os prints.

Para zerar os dados, encerre o servidor, apague o arquivo:
database/vetclinic.db
Depois execute o sistema novamente.
