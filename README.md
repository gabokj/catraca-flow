# CatracaFlow — Sistema Inteligente de Controle de Acesso e Catraca

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Ativo-success.svg)](#)

Sistema web completo e moderno para gestão e controle de acesso via catraca física ou virtual, geração automatizada de tickets com QR Code, apontamento de atrasos, autorizações de saída e controle periódico de cotas de ocorrências (esquecimento/perda de crachá e uniforme).

---

## 🚀 Funcionalidades

- **Identificação Ágil por CPF**: Consulta em tempo real e auto-cadastro para agilidade no fluxo de entrada.
- **Emissão Automática de Tickets com QR Code**:
  - Verificação de janela de horários (tolerância, atrasos leves e encaminhamentos).
  - Saídas autorizadas (apoio, atividades externas, biblioteca, orientação/tutor).
- **Gestão de Cotas de Ocorrências**:
  - Controle automático de limites mensais/semanais (ex: esquecimento de crachá, perda e vestimenta).
  - Bloqueio e encaminhamento quando o limite é excedido.
- **Backend Leve em Python**: Roda com a biblioteca padrão nativa do Python, sem necessidade de frameworks pesados para começar.
- **Suporte a Banco de Dados**: SQLite nativo (zero configuração inicial) e compatível com MySQL.
- **Interface Responsiva**: Visual moderno em tema dark, fluido e compatível com totens touch screen e terminais de catraca.

---

## 📁 Estrutura do Projeto

```text
catraca/
├── backend/                  # API REST e regras de negócio
│   ├── __init__.py
│   ├── app.py                # Servidor HTTP e endpoints REST
│   ├── config.py             # Configurações de porta e conexão com o banco
│   └── functions.py          # Lógica de validação de horário, QR code e cotas
├── frontend/                 # Interface do usuário (Web / Totem)
│   ├── css/                  # Folhas de estilo (tema moderno e responsivo)
│   ├── fonts/                # Tipografia personalizada
│   ├── img/                  # Logos e recursos visuais
│   ├── js/                   # Funções assíncronas e integração com o backend
│   ├── cracha.html           # Tela de ocorrência de crachá
│   ├── login.html            # Tela de identificação por CPF
│   ├── motivo.html           # Seleção de tipo de acesso / ocorrência
│   ├── ticket.html           # Visualização e impressão do ticket gerado
│   └── tipo-saida.html       # Categorização de motivos de saída
├── sql/
│   └── database.sql          # Script de criação de tabelas para MySQL
├── .gitignore                # Arquivos ignorados pelo Git
├── index.html                # Ponto de entrada com redirecionamento automático
├── requirements.txt          # Dependências opcionais (ex: pymysql)
└── run.py                    # Script de inicialização do sistema
```

---

## 🛠️ Como Executar

### Pré-requisitos
- Python 3.10 ou superior instalado.

### 1. Iniciar a aplicação
No terminal, dentro da pasta do projeto, execute:
```bash
python run.py
```

### 2. Acessar o sistema
Abra seu navegador no endereço:
```
http://localhost:8000
```

---

## ⚙️ Configurações

As configurações do sistema ficam centralizadas em `backend/config.py`:
- `DB_TYPE`: Escolha `"sqlite"` (padrão) ou `"mysql"`.
- `SERVER_PORT`: Porta de execução (padrão `8000`).
- `MYSQL_*`: Credenciais de conexão caso utilize banco MySQL.
