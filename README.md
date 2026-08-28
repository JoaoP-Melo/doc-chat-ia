# DOC CHAT IA
**Arquitetura de Software | RAG | Clean Code | Monólito Modular | Segurança Enterprise**

Sistema fullstack que permite aos usuários fazer upload de documentos PDF e interagir com um assistente de IA especializado, capaz de responder perguntas contextualizadas com base no conteúdo do documento. O projeto foi arquitetado seguindo princípios de **Clean Code**, **SOLID** e padrões de mercado, com foco em escalabilidade, segurança e manutenibilidade.


## 🏗️ Arquitetura do Sistema

O backend foi construído sobre uma arquitetura de **monólito modular**, onde cada módulo encapsula uma responsabilidade específica do domínio, promovendo:

- **Alta coesão** e **baixo acoplamento** entre domínios
- **Escalabilidade horizontal** futura (cada módulo pode ser extraído para um microsserviço)
- **Testabilidade isolada** por módulo
- **Manutenibilidade** e clareza na evolução do código

```
┌─────────────────────────────────────────────────────────────┐
│                    MONÓLITO MODULAR                          │
├─────────────┬─────────────┬─────────────────────────────────┤
│   Auth      │  Conversa   │         Documentos              │
│  Módulo     │   Módulo    │          Módulo                 │
├─────────────┼─────────────┼─────────────────────────────────┤
│ • Registro  │ • Criar     │ • Upload PDF                    │
│ • Login     │ • Listar    │ • Deletar                       │
│ • Refresh   │ • Deletar   │ • Vetorização (384 chunks)      │
│   Token     │ • Perguntar │                                 │
│ • Revogar   │ • Histórico │                                 │
│   Sessão    │             │                                 │
└─────────────┴─────────────┴─────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
            ┌──────────────┐    ┌──────────────┐
            │  PostgreSQL  │    │   pgvector   │
            │   (dados)    │    │ (embeddings) │
            └──────────────┘    └──────────────┘
```

## 🧠 Pipeline RAG (Retrieval-Augmented Generation)

O sistema implementa um pipeline completo de **RAG**, combinando recuperação de informações com geração de linguagem natural:

| Etapa | Descrição |
|-------|-----------|
| **1. Ingestão** | Upload do PDF → extração de texto → chunking em blocos de 384 tokens |
| **2. Vetorização** | Geração de embeddings via modelo de linguagem e armazenamento no `pgvector` |
| **3. Recuperação** | Busca semântica pelos 5 chunks mais relevantes para a pergunta do usuário |
| **4. Geração** | O agente de IA recebe: instruções do sistema + histórico (últimas 10 mensagens) + 5 chunks + pergunta |
| **5. Resposta** | Resposta contextualizada e fundamentada no documento |

## 🔐 Módulo de Autenticação (Auth)

Responsável pela segurança da identidade e gestão de sessões. Implementa autenticação stateless com **JWT** e mecanismo de **Refresh Token Rotation**.

### 🔹 POST `/auth/register`
- Validação de dados de entrada
- Hash de senha com algoritmo robusto (bcrypt/argon2)
- Persistência no banco com **email como chave primária**

### 🔹 POST `/auth/login`
- Validação de credenciais
- Geração de **Access Token** (15 minutos) + **Refresh Token** (7 dias)
- Refresh token armazenado no banco com hash interno
- Set de cookies httpOnly no navegador

### 🔹 POST `/auth/refresh`
- Chamada automática quando o access token expira
- Validação do refresh token + comparação de hash com o banco
- **Rotação de token**: gera novo hash aleatório, salva no banco e emite novo refresh token
- Expiração absoluta em 7 dias (sessão inválida → login obrigatório)

### 🔹 DELETE `/auth/logout`
- Revogação imediata da sessão no banco
- Acionada automaticamente em caso de detecção de invasão ou erro de token
- Padrão de segurança: **fail-fast** para sessões comprometidas

## 💬 Módulo de Conversação

Gerencia o ciclo de vida das conversas entre usuário e agente de IA.

### 🔹 POST `/conversations`
- **Protegida** — validação de cookie de sessão
- Cria uma nova conversa vinculada a um documento previamente armazenado
- Relação 1:1 entre conversa e documento

### 🔹 GET `/conversations`
- **Protegida** — lista todas as conversas do usuário autenticado
- Otimizada para interface frontend com paginação/scroll

### 🔹 DELETE `/conversations/:id`
- **Protegida** — verificação de identidade antes da exclusão
- Exclusão em cascata do documento associado (se solicitado)

### 🔹 POST `/conversations/question`
- **Protegida** — endpoint principal do sistema
- Recebe a pergunta do usuário
- Recupera os 5 chunks mais semelhantes via similaridade de cosseno no `pgvector`
- Monta o contexto: instruções do sistema + histórico (10 mensagens) + chunks + pergunta
- Envia para o agente de IA e retorna a resposta

### 🔹 GET `/conversations/:chat_id/messages`
- **Protegida** — recupera o histórico completo de mensagens de uma conversa

## 📁 Módulo de Documentos

Responsável pela ingestão e gestão dos documentos PDF no sistema vetorial.

### 🔹 POST `/documents`
- **Protegida** — recebe arquivo PDF
- Processamento: extração de texto → chunking (384 tokens) → geração de embeddings → persistência no `pgvector`
- Cada chunk é armazenado como vetor para busca semântica eficiente

### 🔹 DELETE `/documents`
- **Protegida** — remoção do documento e seus vetores associados
- Chamada automaticamente na exclusão de uma conversa

## 🎨 Frontend

Interface construída com **React**, **HTML5** e **CSS3**, priorizando:

- **Segurança na comunicação**: apenas dados estritamente necessários trafegam entre frontend e backend
- **UX otimizada**: listagem de conversas, upload de documentos e chat em tempo real
- **Gerenciamento de estado** para sessão e tokens
- **Integração RESTful** com o backend

## 🛡️ Segurança Enterprise

| Camada | Implementação |
|--------|---------------|
| **Rate Limiting** | 60 requisições por IP — proteção contra brute force e DDoS |
| **Autenticação** | JWT stateless + Refresh Token Rotation com hash no banco |
| **Sessões** | Expiração absoluta de 7 dias + revogação imediata em anomalias |
| **Cookies** | httpOnly, secure, sameSite — prevenção de XSS e CSRF |
| **Validação** | Sanitização de inputs em todas as rotas |
| **Fail-Fast** | Sessão deletada automaticamente em caso de token inválido ou suspeita de invasão |

## 🗄️ Banco de Dados

**PostgreSQL** com extensão **pgvector**

- Armazenamento relacional dos dados da aplicação (usuários, conversas, mensagens, sessões)
- Armazenamento vetorial dos embeddings para busca semântica por similaridade de cosseno
- Índices otimizados para consultas de similaridade em alta dimensionalidade

## 🧪 Testes

Cobertura de testes implementada para **todas as rotas** do sistema:

- Testes unitários por módulo
- Testes de integração para fluxos end-to-end
- Validação de regras de negócio, segurança e edge cases
- Garantia de integridade e regressão zero

## 🐳 Infraestrutura & DevOps

### Docker Compose

O projeto utiliza **Docker Compose** para orquestração de containers, garantindo:

- **Portabilidade**: ambiente idêntico em desenvolvimento, staging e produção
- **Isolamento**: cada serviço roda em seu próprio container
- **Facilidade de onboarding**: `docker-compose up` para subir toda a stack

## ✅ Boas Práticas Adotadas

| Prática | Aplicação no Projeto |
|---------|----------------------|
| **RESTful API** | Todas as rotas seguem os métodos HTTP semânticos e status codes corretos |
| **Clean Code** | Nomenclatura expressiva, funções com responsabilidade única, baixa complexidade ciclomática |
| **SOLID** | Separação de responsabilidades, inversão de dependência, aberto/fechado |
| **Monólito Modular** | Domínios isolados com fronteiras claras, preparado para evolução arquitetural |
| **Separação de Camadas** | Controllers, Services, Repositories — independência de frameworks |
| **Segurança por Design** | Rate limiting, rotação de tokens, validação de entrada, fail-fast |
| **Observabilidade** | Estrutura preparada para logs estruturados e métricas |
| **Testes Automatizados** | Cobertura completa das rotas e regras de negócio |

## 🚀 Como Executar

### Pré-requisitos

Antes de começar, tenha instalado:

- **Git**
- **Docker**
- **Docker Compose**

### 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd doc_chat_ia
```

### 2. Crie os arquivos de ambiente

Nos arquivos `.env-example` altere o nome deles e deixe apenas `.env`

### 3. Configure as variáveis de ambiente

No arquivo `.env`, configure os dados do PostgreSQL:

```
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
```

No arquivo `backend/.env`, configure principalmente:

```env
SECRET_KEY=
API_KEY=
BASE_URL=
MODEL=
```

### 4. Suba os containers

Com os arquivos `.env` configurados, execute:

```bash
docker compose up --build
```

Esse comando sobe toda a stack do projeto:

- **Frontend React/Vite**
- **Backend Python/FastAPI**
- **PostgreSQL com pgvector**

As migrações do banco são executadas automaticamente quando o container do backend inicia.

### 5. Acesse a aplicação

Depois que os containers estiverem rodando:

- Frontend: `http://localhost:5173`
- Backend/API: `http://localhost:8000`

Para parar os containers:

```bash
docker compose down
```


## 📊 Competências do Mercado de TI Demonstradas

Este projeto evidencia domínio nas competências mais valorizadas atualmente:

- **🤖 IA Generativa & RAG**: Implementação prática de pipeline RAG com embeddings e recuperação semântica
- **🏛️ Arquitetura de Software**: Monólito modular, Clean Architecture, SOLID, separação de camadas
- **🔐 Segurança de Aplicações**: JWT, Refresh Token Rotation, Rate Limiting, proteção contra ataques comuns
- **🗄️ Banco de Dados Vetorial**: Uso de PostgreSQL + pgvector para busca semântica
- **🐳 DevOps & Containers**: Docker Compose para orquestração e ambientes consistentes
- **🧪 Qualidade de Software**: Testes automatizados, Clean Code, validações rigorosas
- **⚡ APIs RESTful**: Design de APIs seguindo padrões HTTP e boas práticas de comunicação cliente-servidor


## 👨‍💻 Autor

Arquitetado e desenvolvido por João Pedro com foco em **excelência técnica**, **segurança** e **escalabilidade**.
