# ICEIBank

> **Disciplina:** Laboratório de Desenvolvimento de Aplicações Móveis e Distribuídas

> **Curso:** Engenharia de Software

<div align="center">

Banco simplificado dividido em agências independentes, com API REST em arquitetura MVC, comunicação entre agências por mensageria (RabbitMQ), relógio vetorial e autenticação JWT.

<p>
  <img alt="Python 3.12" src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.141-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img alt="Uvicorn" src="https://img.shields.io/badge/Uvicorn-0.52-499848?style=for-the-badge&logo=gunicorn&logoColor=white" />
  <img alt="PyJWT" src="https://img.shields.io/badge/PyJWT-2.13-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" />
  <img alt="Pydantic" src="https://img.shields.io/badge/Pydantic-2-E92063?style=for-the-badge&logo=pydantic&logoColor=white" />
  <img alt="RabbitMQ" src="https://img.shields.io/badge/RabbitMQ-CloudAMQP-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white" />
</p>

</div>

---

## Sumário

- [Uso de IA](#uso-de-ia)
- [Contexto Acadêmico](#contexto-acadêmico)
- [Visão Geral](#visão-geral)
- [Escolha de Linguagem](#escolha-de-linguagem)
- [Arquitetura](#arquitetura)
- [Mensageria (RabbitMQ)](#mensageria-rabbitmq)
- [Relógio Vetorial](#relógio-vetorial)
- [Idempotência](#idempotência)
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

- **Claude (Anthropic)**: usado para preparar o ambiente (estruturação de pastas, configuração do projeto FastAPI), traduzir para Python o código de referência que o roteiro fornece em Node.js/Express, verificar e corrigir o código implementado, ajudar na construção e no ajuste do frontend em Vue, implementar as funcionalidades adicionais de idempotência (transferências no Sprint 1, consumidor de créditos no Sprint 2), separar o backend em camadas (controllers, services, repositories e models), complementar/ajudar na formulação das respostas de [`RESPOSTAS.md`](RESPOSTAS.md) e ajudar a organizar e criar os commits do Git.
- **Pesquisa no Google (Gemini)**: usada para consultar conceitos de sistemas distribuídos (relógios lógico e vetorial, mensageria, atomicidade em transações distribuídas) e o funcionamento de JWT, abordados nas perguntas do roteiro.

## Contexto Acadêmico

Este projeto corresponde ao **Sprint 2** de um projeto único que evolui ao longo de quatro sprints, cada um alinhado a uma unidade da ementa e a um conceito de Sistemas Distribuídos:

| Sprint | Unidade | Tecnologia | Conceito de Sistemas Distribuídos |
| --- | --- | --- | --- |
| 1 | U2 - Desenvolvimento Web | API REST / MVC | Relógio lógico de Lamport |
| **2 (atual)** | U3 - Comunicação indireta | Mensageria / Pub-Sub | Relógio vetorial |
| 3 | U4 - Desenvolvimento Móvel | App Flutter | Consenso (eleição de líder) |
| 4 | U5 - Computação em Nuvem | Containers | Transações distribuídas (2PC/Saga) |

## Visão Geral

O ICEIBank simula um banco dividido em agências, onde cada agência é uma **partição independente** de contas, não uma réplica. O mesmo código é executado três vezes com identidades diferentes, e cada instância responde apenas pelas contas sob sua responsabilidade.

Funcionalidades:

- CRUD de contas com depósito e saque
- Particionamento determinístico de contas entre as três agências
- Transferência dentro da mesma agência (local) e entre agências diferentes (via RabbitMQ, assíncrona)
- Registro de todos os eventos com timestamp de relógio vetorial
- Linha do tempo causal, que mescla os logs das três agências e aponta os pares de eventos concorrentes
- Autenticação e autorização via JWT
- Interface web consumindo a API autenticada, com escolha da agência de acesso
- Idempotência na origem (transferência reenviada) e no destino (mensagem de crédito entregue duas vezes)

O que mudou do Sprint 1 para o Sprint 2:

| Sprint 1 | Sprint 2 |
| --- | --- |
| Relógio de Lamport (um contador) | Relógio vetorial (um contador por agência) |
| Chamada REST direta para `creditar-remoto` | Publicação na exchange do RabbitMQ, consumida pela agência de destino |
| Destino fora do ar: 502 e crédito perdido | Destino fora do ar: mensagem retida na fila e entregue quando ele volta |
| Token de serviço para a rota interna | Rota interna removida; o acesso ao broker é controlado pela credencial do CloudAMQP |
| Linha do tempo ordenada por Lamport | Linha do tempo por hora de parede, com pares concorrentes identificados pelo vetor |

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
   |-- destino na mesma agencia  -> credita direto
   |
   \-- destino em outra agencia  -> publica em iceibank.eventos
                                    routing key agencia.<destino>.creditar
                                    (vetor de envio + idMensagem)
                                          |
                                          v
                                    fila-agencia-<destino> (duravel)
                                          |
                                          v
                                    Agencia de destino consome e credita
```

### Camadas do backend

| Camada | Responsabilidade | Arquivos |
| --- | --- | --- |
| Controllers | Só HTTP: rotas, validação de entrada, JWT e tradução de erro para status | `controllers/` |
| Services | Regras de negócio: partição, saldo, idempotência, relógio, log e mensageria | `services/` |
| Repositories | Só acesso a dados (buscar, salvar), sem regra de negócio | `repositories/` |
| Models | A entidade `Conta`, com `creditar()` e `debitar()` | `models/` |
| Composição | Monta repositories, services e controllers e liga o consumidor do RabbitMQ | `main.py` |

Os services não conhecem FastAPI: levantam erros de negócio (`SaldoInsuficiente`, `ContaNaoEncontrada`...) e `controllers/erros.py` traduz cada um para 400, 401, 404 ou 409. A rota HTTP e o consumidor do RabbitMQ usam o mesmo `TransferenciasService`. As contas ficam em memória, dentro do `ContasRepository`; trocar por um banco mexe só nessa camada.

### Camadas do frontend

| Camada (MVC) | Responsabilidade | Arquivos |
| --- | --- | --- |
| Model | Tipos, acesso à API e estado da sessão | `types/`, `services/api.ts`, `stores/auth.ts` |
| View | Telas e componentes reaproveitáveis | `views/`, `components/` |
| Controller | Reação aos eventos da tela | `<script setup>` de cada view |

O token é injetado em toda requisição por um interceptor do axios, e um segundo interceptor derruba a sessão e leva a pessoa de volta ao login quando a API responde 401.

## Mensageria (RabbitMQ)

O RabbitMQ roda no **CloudAMQP** (plano gratuito), então não precisa instalar nada localmente.

| Elemento | Valor |
| --- | --- |
| Exchange | `iceibank.eventos`, tipo `topic`, durável |
| Filas | `fila-agencia-0`, `fila-agencia-1`, `fila-agencia-2`, duráveis |
| Routing key | `agencia.<id>.creditar`, cada fila ligada só à sua |
| Mensagens | persistentes, confirmadas (ack) só depois de processadas |

A conexão usa `connect_robust` do `aio-pika`, que reconecta sozinha se o broker cair. O consumidor sobe junto com a agência e roda em paralelo ao servidor HTTP. O script `scripts/testar_mensageria.py` testa o roteamento fora da aplicação: cada fila só recebe a mensagem da própria routing key.

## Relógio Vetorial

Cada agência mantém um vetor com um contador por agência (`[ag0, ag1, ag2]`), seguindo as três regras do algoritmo:

| Regra | Método | Comportamento |
| --- | --- | --- |
| Evento local | `evento_local()` | incrementa a própria posição |
| Ao enviar | `ao_enviar()` | incrementa a própria posição e envia o vetor junto da mensagem |
| Ao receber | `ao_receber(v)` | fica com o máximo de cada posição e incrementa a própria |

Todo evento é gravado em `data/eventos-agencia-N.jsonl`, com o vetor e a hora de parede. O script `mesclar_logs.py` junta os arquivos das três agências, ordena por hora de parede e compara os vetores de agências diferentes: se nenhum é menor ou igual ao outro em todas as posições, o par é listado como **concorrente**. O débito e o crédito de uma mesma transferência nunca aparecem como concorrentes, porque a regra 3 propaga o vetor do débito para o crédito.

## Idempotência

| Onde | Problema | Solução |
| --- | --- | --- |
| Origem (Sprint 1) | clique duplo em Transferir debitava duas vezes | o frontend manda um `idOperacao`; repetido, a agência devolve o resultado anterior e loga `TRANSFERENCIA_IGNORADA` |
| Destino (Sprint 2) | o RabbitMQ pode entregar a mesma mensagem duas vezes (entrega "pelo menos uma vez") | cada mensagem leva um `idMensagem`; repetida, a agência não credita de novo e loga `CREDITO_REMOTO_IGNORADO` |

Os ids aplicados ficam no `TransferenciasRepository`. O script `scripts/testar_idempotencia.py` publica a mesma mensagem de crédito duas vezes para demonstrar.

## Autenticação e Autorização

O sistema trabalha com dois tipos de token, assinados com a mesma chave (`HS256`):

| Tipo | Origem | Permissões |
| --- | --- | --- |
| `operador` | `POST /auth/login-operador` | criar contas e operar qualquer conta da agência |
| `cliente` | `POST /auth/login` | operar exclusivamente a própria conta |

- **Autenticação** (`autenticado`): valida assinatura e expiração. Falha retorna **401**.
- **Autorização** (`exige_dono`, `exige_operador`): compara o token com a conta alvo ou com o perfil exigido. Falha retorna **403**.

O consumidor do RabbitMQ não passa por JWT: quem consegue publicar na exchange é quem tem a URL do CloudAMQP, que fica no `agencia/.env` (fora do Git). Senhas são armazenadas com `sha256` e nunca retornam nas respostas da API. A chave do JWT é lida da variável de ambiente `JWT_SEGREDO`.

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

O crédito entre agências não é mais uma rota HTTP: chega pela fila da agência de destino.

Documentação interativa gerada automaticamente pelo FastAPI em `http://localhost:8081/docs`.

## Limitação Conhecida

A mensageria garante que o crédito **chega**, mas não que ele **dá certo**. Se a conta de destino não existir quando a mensagem for consumida (por exemplo, a agência reiniciou e perdeu as contas em memória), a agência de destino só registra `CREDITO_REMOTO_FALHOU`. O débito na origem não é revertido, e a origem nem fica sabendo, porque a resposta da transferência só confirma que a mensagem foi publicada.

Isso é intencional nesta etapa: garantir que débito e crédito aconteçam juntos ou nenhum dos dois é o assunto do Sprint 4 (transações distribuídas com 2PC ou Saga). A evidência está em `evidencias/sprint2/resiliencia-fila.png`.

## Tecnologias Utilizadas

### Backend

- Python `3.12`
- FastAPI `0.141`
- Uvicorn `0.52`
- Pydantic (validação de entrada)
- PyJWT `2.13` (autenticação)
- aio-pika (cliente assíncrono do RabbitMQ)
- python-dotenv (leitura do `agencia/.env`)
- RabbitMQ gerenciado pelo CloudAMQP

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
├── evidencias/
│   ├── sprint1/                # prints do Sprint 1
│   ├── sprint2/                # prints do Sprint 2
│   └── videos/                 # videos de apresentacao
├── RESPOSTAS.md                # indice das respostas
├── RESPOSTAS-SPRINT1.md        # respostas do Sprint 1
├── RESPOSTAS-SPRINT2.md        # respostas do Sprint 2
├── ROTEIRO-SPRINT1.md          # enunciado do Sprint 1
├── ROTEIRO-SPRINT2.md          # enunciado do Sprint 2
└── README.md
```

### Backend

```text
agencia/
├── requirements.txt
├── pyproject.toml              # configuracao do linter
├── .env.example                # modelo do .env com a RABBITMQ_URL
├── mesclar_logs.py             # linha do tempo causal e pares concorrentes
├── scripts/                    # verificacoes manuais, precisam do RabbitMQ no ar
│   ├── testar_mensageria.py    # testa o roteamento das filas fora da aplicacao
│   └── testar_idempotencia.py  # entrega a mesma mensagem de credito duas vezes
├── data/                       # logs .jsonl gerados em execucao (nao versionados)
└── src/
    ├── main.py                 # monta as camadas e liga o consumidor
    ├── config.py               # particionamento, portas e parametros de JWT
    ├── controllers/            # so HTTP
    │   ├── authController.py
    │   ├── contasController.py
    │   ├── transferenciasController.py
    │   ├── dependencias.py     # JWT, autorizacao e acesso aos services
    │   └── erros.py            # erro de negocio -> status HTTP
    ├── services/               # regras de negocio
    │   ├── auth.py             # senha, token e login
    │   ├── contas_service.py
    │   ├── transferencias_service.py
    │   ├── erros.py            # erros de negocio
    │   ├── relogio_vetorial.py # as tres regras do algoritmo
    │   ├── relogio_lamport.py  # relogio do Sprint 1, mantido como historico
    │   ├── registro_eventos.py # gravacao dos eventos em .jsonl
    │   └── mensageria.py       # publicar e assinar no RabbitMQ
    ├── repositories/           # so dados
    │   ├── contas_repository.py
    │   └── transferencias_repository.py
    └── models/
        └── conta.py
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
- Uma instância gratuita do RabbitMQ no [CloudAMQP](https://www.cloudamqp.com/)

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

### 2. Configurar o RabbitMQ

Copie o modelo e preencha a `RABBITMQ_URL` com a URL AMQP da sua instância do CloudAMQP:

```powershell
cd agencia
copy .env.example .env
```

O `.env` fica fora do Git, porque a URL carrega usuário e senha. Para conferir a conexão e o roteamento das filas:

```powershell
.venv\Scripts\python.exe scripts\testar_mensageria.py
```

### 3. Subir as três agências

Cada agência é o mesmo código, identificado pela variável `AGENCIA_ID`. Em três terminais, dentro de `agencia/`:

```powershell
$env:AGENCIA_ID=0; .venv\Scripts\python.exe src\main.py
$env:AGENCIA_ID=1; .venv\Scripts\python.exe src\main.py
$env:AGENCIA_ID=2; .venv\Scripts\python.exe src\main.py
```

### 4. Abrir a interface web

Em um quarto terminal:

```powershell
cd frontend
npm run dev
```

A interface fica em `http://localhost:5173`, que é a única origem liberada no CORS das agências (`ORIGENS_FRONTEND` em `config.py`). O login de operador é `operador` / `iceibank123`; o de cliente é o número da conta e a senha definida na criação. O seletor na tela de login escolhe por qual das três agências o acesso entra.

### 5. Autenticar e operar pela API

Alternativa à interface, em um quinto terminal:

```powershell
$op = Invoke-RestMethod -Uri "http://localhost:8081/auth/login-operador" -Method Post -ContentType "application/json" -Body '{"usuario":"operador","senha":"iceibank123"}'
$h = @{ Authorization = "Bearer $($op.token)" }

Invoke-RestMethod -Uri "http://localhost:8081/contas" -Method Post -Headers $h -ContentType "application/json" -Body '{"id":0,"nomeAluno":"Ana","senha":"senha-ana","saldoInicial":200}'
Invoke-RestMethod -Uri "http://localhost:8081/contas/0" -Headers $h
```

### 6. Ver a linha do tempo causal

Dentro de `agencia/`:

```powershell
.venv\Scripts\python.exe mesclar_logs.py
```

## Evidências de Teste

Prints de execução real, com a saída de `Get-Date` visível.

### Sprint 2 (`evidencias/sprint2/`)

| Arquivo | O que comprova |
| --- | --- |
| `transferencia-assincrona.png` | transferência entre agências completando pela mensageria, com o log das duas agências |
| `resiliencia-fila-agencia-fora.png` | agência de destino fora do ar e transferência publicada mesmo assim |
| `resiliencia-fila-retida.png` | mensagem retida na fila enquanto ninguém consumia |
| `resiliencia-fila.png` | agência de volta consumindo a mensagem, sem a conta para creditar |
| `regressao-frontend-deposito.png` | depósito pelo frontend depois da troca para mensageria |
| `regressao-log-deposito.png` | o mesmo depósito no log, já com vetor |
| `regressao-token-expirado.png` | token expirado ainda recusado |
| `linha-do-tempo-causal.png` | linha do tempo das três agências com os pares concorrentes |
| `funcionalidade-adicional.png` | mesma mensagem de crédito entregue duas vezes e aplicada uma vez só |

### Sprint 1 (`evidencias/sprint1/`)

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
| [`RESPOSTAS-SPRINT1.md`](RESPOSTAS-SPRINT1.md) | respostas e justificativas de design do Sprint 1 |
| [`RESPOSTAS-SPRINT2.md`](RESPOSTAS-SPRINT2.md) | respostas do Sprint 2 |
| [`ROTEIRO-SPRINT1.md`](ROTEIRO-SPRINT1.md) | enunciado do Sprint 1 |
| [`ROTEIRO-SPRINT2.md`](ROTEIRO-SPRINT2.md) | enunciado do Sprint 2 |

## Autor

| Nome | Foto | GitHub | LinkedIn |
| --- | --- | --- | --- |
| Eric Leal | <div align="center"><img src="https://github.com/Eric-Leal.png" width="70" height="70" /></div> | <div align="center"><a href="https://github.com/Eric-Leal">@Eric-Leal</a></div> | <div align="center"><a href="https://linkedin.com/in/ericgleal">Perfil</a></div> |

---

Desenvolvido para fins acadêmicos no contexto do Laboratório de Desenvolvimento de Aplicações Móveis e Distribuídas.
