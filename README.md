# ICEIBank

> **Disciplina:** Laboratório de Desenvolvimento de Aplicações Móveis e Distribuídas

> **Curso:** Engenharia de Software

<div align="center">

Banco simplificado dividido em agências independentes, com API REST em arquitetura MVC, relógio lógico de Lamport e autenticação JWT.

<p>
  <img alt="Python 3.12" src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.141-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img alt="Uvicorn" src="https://img.shields.io/badge/Uvicorn-0.52-499848?style=for-the-badge&logo=gunicorn&logoColor=white" />
  <img alt="PyJWT" src="https://img.shields.io/badge/PyJWT-2.13-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" />
  <img alt="Pydantic" src="https://img.shields.io/badge/Pydantic-2-E92063?style=for-the-badge&logo=pydantic&logoColor=white" />
</p>

</div>

---

## Sumário

- [Uso de IA](#uso-de-ia)
- [Contexto Acadêmico](#contexto-acadêmico)
- [Visão Geral](#visão-geral)
- [Escolha de Linguagem](#escolha-de-linguagem)
- [Arquitetura](#arquitetura)
- [Relógio de Lamport](#relógio-de-lamport)
- [Autenticação e Autorização](#autenticação-e-autorização)
- [Endpoints](#endpoints)
- [Limitação Conhecida](#limitação-conhecida)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Como Rodar o Projeto](#como-rodar-o-projeto)
- [Evidências de Teste](#evidências-de-teste)
- [Documentação do Projeto](#documentação-do-projeto)
- [Autor](#autor)

## Uso de IA

- **Claude (Anthropic)**: usado para preparar o ambiente (estruturação de pastas, configuração do projeto FastAPI), traduzir para Python o código de referência que o roteiro fornece em Node.js/Express, verificar e corrigir o código implementado, ajudar na construção e no ajuste do frontend em Vue, complementar/ajudar na formulação das respostas de [`RESPOSTAS.md`](RESPOSTAS.md) e ajudar a organizar e criar os commits do Git.
- **Pesquisa no Google (Gemini)**: usada para consultar conceitos de sistemas distribuídos (relógio de Lamport, atomicidade em transações distribuídas) e o funcionamento de JWT, abordados nas perguntas do roteiro.

## Contexto Acadêmico

Este projeto corresponde ao **Sprint 1** de um projeto único que evolui ao longo de quatro sprints, cada um alinhado a uma unidade da ementa e a um conceito de Sistemas Distribuídos:

| Sprint | Unidade | Tecnologia | Conceito de Sistemas Distribuídos |
| --- | --- | --- | --- |
| **1 (atual)** | U2 - Desenvolvimento Web | API REST / MVC | Relógio lógico de Lamport |
| 2 | U3 - Comunicação indireta | Mensageria / Pub-Sub | Relógio vetorial |
| 3 | U4 - Desenvolvimento Móvel | App Flutter | Consenso (eleição de líder) |
| 4 | U5 - Computação em Nuvem | Containers | Transações distribuídas (2PC/Saga) |

## Visão Geral

O ICEIBank simula um banco dividido em agências, onde cada agência é uma **partição independente** de contas, não uma réplica. O mesmo código é executado três vezes com identidades diferentes, e cada instância responde apenas pelas contas sob sua responsabilidade.

Funcionalidades do Sprint 1:

- CRUD de contas com depósito e saque
- Particionamento determinístico de contas entre as três agências
- Transferência dentro da mesma agência (local) e entre agências diferentes (via REST)
- Registro de todos os eventos com timestamp de relógio lógico de Lamport
- Linha do tempo unificada, mesclando os logs das três agências
- Autenticação e autorização via JWT
- Interface web consumindo a API autenticada, com escolha da agência de acesso

## Escolha de Linguagem

O roteiro traz o código de referência em Node.js/Express, mas a entrega não pode ser em Node. Escolhi **Python (FastAPI)** para o backend e **Vue** para o frontend.

A pasta `agencia-express/` guarda a implementação de referência do roteiro apenas para estudo e comparação. A entrega é a pasta `agencia/`.

## Arquitetura

### Particionamento

Cada conta pertence a exatamente uma agência, definida por `id_conta % 3`. Uma agência recusa qualquer operação sobre contas que não são suas.

| Conta | Agência responsável | Porta |
| --- | --- | --- |
| 0, 3, 6, 9... | Agência 0 | `8081` |
| 1, 4, 7, 10... | Agência 1 | `8082` |
| 2, 5, 8, 11... | Agência 2 | `8083` |

As portas usam o OFFSET pessoal **81** (dois últimos dígitos da matrícula) somado à porta-base 8000.

### Fluxo de uma transferência

```text
Cliente
   |
   v
Agencia de origem (dona da conta de origem)
   |
   |-- destino na mesma agencia  -> credita direto na memoria
   |
   \-- destino em outra agencia  -> POST /contas/{id}/creditar-remoto
                                    (token de servico + timestamp de Lamport)
                                          |
                                          v
                                    Agencia de destino
```

### Camadas do backend

| Camada | Responsabilidade | Arquivos |
| --- | --- | --- |
| Configuração | Particionamento, portas e parâmetros de JWT | `config.py` |
| Controllers | Rotas HTTP e validação de entrada | `controllers/` |
| Services | Relógio lógico, registro de eventos e autenticação | `services/` |
| Aplicação | Composição do estado e registro dos routers | `main.py` |

O estado de cada agência (contas, relógio e registro de eventos) vive em `app.state`, criado no boot. As contas ficam em memória, sem banco de dados, conforme o escopo do sprint.

### Camadas do frontend

| Camada (MVC) | Responsabilidade | Arquivos |
| --- | --- | --- |
| Model | Tipos, acesso à API e estado da sessão | `types/`, `services/api.ts`, `stores/auth.ts` |
| View | Telas e componentes reaproveitáveis | `views/`, `components/` |
| Controller | Reação aos eventos da tela | `<script setup>` de cada view |

O token é injetado em toda requisição por um interceptor do axios, e um segundo interceptor derruba a sessão e leva a pessoa de volta ao login quando a API responde 401.

## Relógio de Lamport

Cada agência mantém um contador inteiro próprio, seguindo as três regras do algoritmo:

| Regra | Método | Comportamento |
| --- | --- | --- |
| Evento local | `evento_local()` | incrementa o contador |
| Ao enviar | `ao_enviar()` | incrementa e envia o valor junto da mensagem |
| Ao receber | `ao_receber(ts)` | ajusta para `max(local, recebido) + 1` |

Todo evento é gravado em `data/eventos-agencia-N.jsonl`, com o timestamp lógico e a hora de parede. O script `mesclar_logs.py` junta os arquivos das três agências em uma única linha do tempo ordenada por Lamport, o que permite observar empates entre eventos concorrentes e a divergência em relação ao tempo real.

## Autenticação e Autorização

O sistema trabalha com três tipos de token, todos assinados com a mesma chave (`HS256`):

| Tipo | Origem | Permissões |
| --- | --- | --- |
| `operador` | `POST /auth/login-operador` | criar contas e operar qualquer conta da agência |
| `cliente` | `POST /auth/login` | operar exclusivamente a própria conta |
| `servico` | gerado internamente pela agência de origem | apenas a rota `creditar-remoto`, validade de 1 minuto |

- **Autenticação** (`autenticado`): valida assinatura e expiração. Falha retorna **401**.
- **Autorização** (`exige_dono`): compara o `sub` do token com a conta alvo. Falha retorna **403**.

Senhas são armazenadas com `sha256` e nunca retornam nas respostas da API. A chave secreta é lida da variável de ambiente `JWT_SEGREDO`.

## Endpoints

| Método | Rota | Autenticação | Descrição |
| --- | --- | --- | --- |
| `POST` | `/auth/login` | pública | login de cliente (id da conta + senha) |
| `POST` | `/auth/login-operador` | pública | login do operador da agência |
| `POST` | `/contas` | operador | cria uma conta na agência responsável |
| `GET` | `/contas/{id}` | dono ou operador | consulta saldo |
| `POST` | `/contas/{id}/depositar` | dono ou operador | deposita valor |
| `POST` | `/contas/{id}/sacar` | dono ou operador | saca valor |
| `POST` | `/transferencias` | dono da origem | transfere, local ou entre agências |
| `POST` | `/contas/{id}/creditar-remoto` | token de serviço | recebe crédito de outra agência |

Documentação interativa gerada automaticamente pelo FastAPI em `http://localhost:8081/docs`.

## Limitação Conhecida

Se a transferência entre agências falhar depois do débito (agência de destino fora do ar, rede indisponível), o débito **não é revertido**. O valor sai da conta de origem e não chega à de destino, e o sistema apenas registra o evento `TRANSFERENCIA_FALHOU` no log.

Isso é intencional neste sprint: é exatamente o problema que o Sprint 4 resolve com transações distribuídas (2PC ou Saga). A evidência da falha está em `evidencias/sprint1/falha-conhecida.png`.

## Tecnologias Utilizadas

### Backend

- Python `3.12`
- FastAPI `0.141`
- Uvicorn `0.52`
- Pydantic (validação de entrada)
- PyJWT `2.13` (autenticação)
- requests `2.34` (chamadas entre agências)

### Frontend

- Vue `3.5`
- Vite `8` (servidor de desenvolvimento e build)
- TypeScript `6`
- Vue Router `5` (rotas e proteção das telas internas)
- Pinia `4` (estado da sessão: token, perfil e agência escolhida)
- axios `1.20` (chamadas à API, com os interceptors de token e de erro)
- Tailwind CSS `4`

### Referência de estudo

- Node.js + Express `5` (implementação do roteiro, em `agencia-express/`)

## Estrutura do Repositório

```text
iceibank/
├── agencia/                    # backend (Python + FastAPI), roda 3 vezes
├── frontend/                   # interface web (Vue + Vite)
├── agencia-express/            # referencia do roteiro (Node.js), apenas estudo
├── evidencias/sprint1/         # prints de execucao
├── RESPOSTAS.md                # respostas das questoes do roteiro
├── ROTEIRO.md                  # enunciado do sprint
└── README.md
```

### Backend

```text
agencia/
├── requirements.txt
├── pyproject.toml              # configuracao do linter
├── mesclar_logs.py             # linha do tempo unificada das 3 agencias
├── data/                       # logs .jsonl gerados em execucao (nao versionados)
└── src/
    ├── main.py                 # composicao da app e estado da agencia
    ├── config.py               # particionamento, portas e parametros de JWT
    ├── controllers/
    │   ├── authController.py           # rotas de login
    │   ├── contasController.py         # CRUD, deposito e saque
    │   └── transferenciasController.py # transferencias e credito remoto
    └── services/
        ├── relogio_lamport.py  # as tres regras do algoritmo
        ├── registro_eventos.py # gravacao dos eventos em .jsonl
        └── auth.py             # geracao e validacao de tokens
```

### Frontend

```text
frontend/
├── package.json
├── vite.config.ts
└── src/
    ├── main.ts
    ├── App.vue                 # layout, navegacao e botao sair
    ├── router/index.ts         # rotas e bloqueio das telas internas sem token
    ├── types/index.ts          # tipos e a regra de particionamento id % 3
    ├── services/api.ts         # axios, injecao do token e tratamento de erro
    ├── stores/auth.ts          # sessao (token, perfil, conta, agencia)
    ├── components/
    │   ├── AlertaMensagem.vue  # faixa de erro ou sucesso
    │   └── SeletorAgencia.vue  # escolha da agencia de acesso
    └── views/
        ├── LoginView.vue       # login de cliente ou operador
        ├── ContaView.vue       # saldo, deposito, saque e abertura de conta
        └── TransferenciaView.vue
```

## Como Rodar o Projeto

### Pré-requisitos

- Python 3.12 ou superior
- Node.js 22.18 ou superior (para o frontend)
- Git

### 1. Preparar o ambiente

Backend:

```powershell
cd agencia
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Frontend:

```powershell
cd frontend
npm install
```

### 2. Subir as três agências

Cada agência é o mesmo código, identificado pela variável `AGENCIA_ID`. Em três terminais:

```powershell
$env:AGENCIA_ID=0; .venv\Scripts\python.exe src\main.py
$env:AGENCIA_ID=1; .venv\Scripts\python.exe src\main.py
$env:AGENCIA_ID=2; .venv\Scripts\python.exe src\main.py
```

### 3. Abrir a interface web

Em um quarto terminal:

```powershell
cd frontend
npm run dev
```

A interface fica em `http://localhost:5173`, que é a única origem liberada no CORS das agências (`ORIGENS_FRONTEND` em `config.py`). O login de operador é `operador` / `iceibank123`; o de cliente é o número da conta e a senha definida na criação. O seletor na tela de login escolhe por qual das três agências o acesso entra.

### 4. Autenticar e operar pela API

Alternativa à interface, em um quinto terminal:

```powershell
$op = Invoke-RestMethod -Uri "http://localhost:8081/auth/login-operador" -Method Post -ContentType "application/json" -Body '{"usuario":"operador","senha":"iceibank123"}'
$h = @{ Authorization = "Bearer $($op.token)" }

Invoke-RestMethod -Uri "http://localhost:8081/contas" -Method Post -Headers $h -ContentType "application/json" -Body '{"id":0,"nomeAluno":"Ana","senha":"senha-ana","saldoInicial":200}'
Invoke-RestMethod -Uri "http://localhost:8081/contas/0" -Headers $h
```

### 5. Ver a linha do tempo unificada

```powershell
.venv\Scripts\python.exe mesclar_logs.py
```

## Evidências de Teste

Prints de execução real, com a saída de `Get-Date` visível, em `evidencias/sprint1/`:

| Arquivo | O que comprova |
| --- | --- |
| `transferencia-local.png` | transferência entre contas da mesma agência, com débito e crédito no mesmo relógio |
| `transferencia-entre-agencias.png` | transferência entre agências, com o ajuste do relógio de Lamport no destino |
| `falha-conhecida.png` | agência de destino fora do ar, resposta 502 e débito não revertido |
| `linha-do-tempo.png` | linha do tempo unificada das três agências, com eventos concorrentes empatados |
| `auth-sem-token.png` | rotas protegidas rejeitando requisições sem token e com token inválido (401) |
| `auth-com-token.png` | fluxo autenticado funcionando e bloqueio de acesso a conta alheia (403) |
| `auth-token-expirado.png` | token expirado rejeitado com 401 |
| `frontend-login.png` | tela de login, com seletor de agência e perfil de operador |
| `frontend-particao.png` | agência 1 recusando a criação de uma conta que não é dela |
| `frontend-deposito.png` | depósito pela interface, com o evento no log da agência |
| `frontend-saque.png` | saque pela interface, com o evento no log da agência |
| `frontend-transferencia-local.png` | transferência entre contas da mesma agência, pela interface |
| `frontend-transferencia.png` | transferência entre agências, com o log das duas agências envolvidas |
| `frontend-erro.png` | saldo insuficiente exibido na tela, não só no console |
| `frontend-token-expirado.png` | token expirado derrubando a sessão, com o motivo visível na tela |

## Documentação do Projeto

| Documento | Finalidade |
| --- | --- |
| [`RESPOSTAS.md`](RESPOSTAS.md) | respostas às questões do roteiro e justificativas de design |
| [`ROTEIRO.md`](ROTEIRO.md) | enunciado do Sprint 1 |

## Autor

| Nome | Foto | GitHub | LinkedIn |
| --- | --- | --- | --- |
| Eric Leal | <div align="center"><img src="https://github.com/Eric-Leal.png" width="70" height="70" /></div> | <div align="center"><a href="https://github.com/Eric-Leal">@Eric-Leal</a></div> | <div align="center"><a href="https://linkedin.com/in/ericgleal">Perfil</a></div> |

---

Desenvolvido para fins acadêmicos no contexto do Laboratório de Desenvolvimento de Aplicações Móveis e Distribuídas.
