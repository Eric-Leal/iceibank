# ICEIBank

> **Disciplina:** Laboratório de Desenvolvimento de Aplicações Móveis e Distribuídas

> **Curso:** Engenharia de Software

<div align="center">

Banco simplificado dividido em agências independentes, com API REST em arquitetura MVC, comunicação entre agências por mensageria (RabbitMQ), relógio vetorial, autenticação JWT, eleição de líder (Bully) e app Flutter offline-first.

<p>
  <img alt="Python 3.12" src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.141-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img alt="Uvicorn" src="https://img.shields.io/badge/Uvicorn-0.52-499848?style=for-the-badge&logo=gunicorn&logoColor=white" />
  <img alt="PyJWT" src="https://img.shields.io/badge/PyJWT-2.13-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" />
  <img alt="Pydantic" src="https://img.shields.io/badge/Pydantic-2-E92063?style=for-the-badge&logo=pydantic&logoColor=white" />
  <img alt="RabbitMQ" src="https://img.shields.io/badge/RabbitMQ-CloudAMQP-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white" />
  <img alt="Flutter" src="https://img.shields.io/badge/Flutter-3.47-02569B?style=for-the-badge&logo=flutter&logoColor=white" />
  <img alt="Dart" src="https://img.shields.io/badge/Dart-3.13-0175C2?style=for-the-badge&logo=dart&logoColor=white" />
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
- [Eleição de Líder (Bully)](#eleição-de-líder-bully)
- [App Flutter e Offline-first](#app-flutter-e-offline-first)
- [Endpoints](#endpoints)
- [Limitação Conhecida](#limitação-conhecida)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Como Rodar o Projeto](#como-rodar-o-projeto)
- [Evidências de Teste](#evidências-de-teste)
- [Documentação do Projeto](#documentação-do-projeto)
- [Autor](#autor)

## Uso de IA

- **Claude (Anthropic)**: usado para preparar o ambiente (estruturação de pastas, configuração do projeto FastAPI), traduzir para Python o código de referência que o roteiro fornece em Node.js/Express, verificar e corrigir o código implementado, ajudar na construção e no ajuste do frontend em Vue, implementar as funcionalidades adicionais de idempotência (transferências no Sprint 1, consumidor de créditos no Sprint 2), separar o backend em camadas (controllers, services, repositories e models), configurar o ambiente Flutter e o emulador Android, adaptar o algoritmo de Bully do exemplo em Node para Python, escrever o app Flutter e o redesign do frontend web, implementar o limite de saque offline (funcionalidade adicional do Sprint 3), complementar/ajudar na formulação das respostas de [`RESPOSTAS.md`](RESPOSTAS.md).
- **Pesquisa no Google (Gemini)**: usada para consultar conceitos de sistemas distribuídos (relógios lógico e vetorial, mensageria, atomicidade em transações distribuídas) e o funcionamento de JWT, abordados nas perguntas do roteiro.

## Contexto Acadêmico

Este projeto corresponde ao **Sprint 3** de um projeto único que evolui ao longo de quatro sprints, cada um alinhado a uma unidade da ementa e a um conceito de Sistemas Distribuídos:

| Sprint | Unidade | Tecnologia | Conceito de Sistemas Distribuídos |
| --- | --- | --- | --- |
| 1 | U2 - Desenvolvimento Web | API REST / MVC | Relógio lógico de Lamport |
| 2 | U3 - Comunicação indireta | Mensageria / Pub-Sub | Relógio vetorial |
| **3 (atual)** | U4 - Desenvolvimento Móvel | App Flutter | Consenso (eleição de líder) |
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
- Eleição de líder entre as agências pelo algoritmo de Bully, com heartbeat e failover automático
- App Flutter com o fluxo bancário e um painel ao vivo da líder e das agências ativas
- Modo offline-first no app: fila local em SQLite, saldo provisório e sincronização automática com detecção de conflito por vetor
- Limite para saques feitos offline (funcionalidade adicional do Sprint 3)

O que mudou do Sprint 2 para o Sprint 3:

| Sprint 2 | Sprint 3 |
| --- | --- |
| Agências como pares, sem coordenação | Uma líder eleita pelo Bully, reeleita sozinha se cair |
| Só o frontend web | App Flutter consumindo a mesma API |
| Cliente sempre online | App funciona sem conexão e sincroniza ao voltar |
| Vetor usado só na linha do tempo | Vetor também usado para detectar conflito na sincronização (409) |

O que mudou do Sprint 1 para o Sprint 2:

| Sprint 1 | Sprint 2 |
| --- | --- |
| Relógio de Lamport (um contador) | Relógio vetorial (um contador por agência) |
| Chamada REST direta para `creditar-remoto` | Publicação na exchange do RabbitMQ, consumida pela agência de destino |
| Destino fora do ar: 502 e crédito perdido | Destino fora do ar: mensagem retida na fila e entregue quando ele volta |
| Token de serviço para a rota interna | Rota interna removida; o acesso ao broker é controlado pela credencial do CloudAMQP |
| Linha do tempo ordenada por Lamport | Linha do tempo por hora de parede, com pares concorrentes identificados pelo vetor |

## Escolha de Linguagem

O roteiro traz o código de referência em Node.js/Express, mas a entrega não pode ser em Node. Escolhi **Python (FastAPI)** para o backend e **Vue** para o frontend. O app mobile é obrigatoriamente em **Flutter**.

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

## Eleição de Líder (Bully)

As agências elegem uma líder entre si; vence a de maior ID que estiver no ar. Hoje a líder é só informativa: no Sprint 4 ela passa a coordenar as transações distribuídas.

| Mensagem | Rota | Quando |
| --- | --- | --- |
| Eleição | `POST /bully/eleicao` | a agência pergunta às de ID maior se alguém está vivo |
| Coordenador | `POST /bully/coordenador` | quem venceu avisa a todas as outras |
| Consulta | `GET /bully/lider` | quem é a líder para esta agência (usado pelo app e pelo frontend) |

- **Subida:** cada agência abre uma eleição no `lifespan` do FastAPI. Se nenhuma de ID maior responder em 1s (`TIMEOUT_S`), ela se declara líder e manda `coordenador` para todas.
- **Heartbeat:** a cada 3s as agências que não são líder chamam `/bully/lider` na líder. Sem resposta, registram `LIDER_NAO_RESPONDEU` e abrem uma eleição: é o failover automático.
- **Relógio:** as mensagens do Bully levam o vetor (`vetorEnvio`) e passam pelas mesmas regras do relógio vetorial.
- **Histórico:** o script `historico_lideranca.py` lê os logs `data/*.jsonl` e mostra a linha do tempo de quem foi líder e a partir de quando.

O `receber_coordenador` aceita qualquer `liderId` sem comparar IDs. Se a eleição de uma agência menor chegar antes da maior terminar de subir, a liderança pode ficar invertida até alguma agência reiniciar. Detalhes na Parte B de [`RESPOSTAS-SPRINT3.md`](RESPOSTAS-SPRINT3.md).

## App Flutter e Offline-first

O app consome a mesma API do frontend web: login JWT, saldo, depósito, saque e transferência. Na tela inicial, um painel consulta `/bully/lider` nas três agências a cada 3s e mostra a líder e quais agências estão respondendo.

| Camada | Responsabilidade | Arquivos |
| --- | --- | --- |
| Core | Chamadas REST e tradução de erro, endereço das agências, sessão JWT | `core/api.dart`, `core/config.dart`, `core/sessao.dart` |
| Dados | Cache e fila em SQLite, sincronização automática | `dados/banco_local.dart`, `dados/sincronizador.dart` |
| Telas | Login, início e transferência | `telas/` |
| Shared | Painel de liderança, mensagens e formatação em reais | `shared/` |

Sem conexão, depósito e saque não dão erro:

1. A operação vai para a tabela `pendentes` do SQLite junto com o vetor que o app conhecia (`vetorAtual` da última consulta de saldo).
2. A tela mostra "Saldo provisório" com o selo "pendente" e a lista "Aguardando sincronização".
3. Quando a rede volta (ou a cada 10s), o app manda cada pendente para `POST /contas/{id}/sincronizar`.
4. A agência aplica só se o vetor recebido for igual ao atual. Se mudou, responde **409** com `vetorConhecido`, `vetorAtual` e `contaAtual`, e o app mostra a operação em vermelho com "Descartar" e "Reenviar".

Transferência offline não entra na fila, porque mexe em duas contas e possivelmente em duas agências.

**Limite offline (funcionalidade adicional).** Uma operação offline não teve o saldo conferido pela agência. Por isso o app aceita no máximo **R$ 200** em saques somados na fila e no máximo **5** operações pendentes (`core/config.dart`). O backend também recusa com **422** um saque acima de `LIMITE_SAQUE_OFFLINE` no `/sincronizar`, porque não confia no cliente. Depósito offline continua livre.

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
| `POST` | `/contas/{id}/sincronizar` | dono ou operador | aplica uma operação feita offline; 409 se o vetor mudou, 422 se o saque passa do limite |
| `GET` | `/bully/lider` | pública | líder atual segundo esta agência |
| `POST` | `/bully/eleicao` | pública (entre agências) | mensagem de eleição do Bully |
| `POST` | `/bully/coordenador` | pública (entre agências) | anúncio da nova líder |

Saldo, depósito e saque passam a devolver também o `vetorAtual`, que o app guarda para a sincronização.

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
- httpx (chamadas assíncronas entre agências no Bully)
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

### App mobile

- Flutter `3.47` / Dart `3.13`
- http (chamadas à API)
- shared_preferences (token JWT e conta logada)
- sqflite + path (cache da conta e fila de operações offline)
- connectivity_plus (detecta a volta da rede para sincronizar)

### Referência de estudo

- Node.js + Express `5` (implementação do roteiro, em `agencia-express/`)

## Estrutura do Repositório

```text
iceibank/
├── agencia/                    # backend (Python + FastAPI), roda 3 vezes
├── frontend/                   # interface web (Vue + Vite)
├── app_mobile/                 # app Flutter (Sprint 3)
├── agencia-express/            # referencia do roteiro (Node.js), apenas estudo
├── evidencias/
│   ├── sprint1/                # prints do Sprint 1
│   ├── sprint2/                # prints do Sprint 2
│   ├── sprint3/                # prints do Sprint 3
│   └── videos/                 # videos de apresentacao
├── RESPOSTAS.md                # indice das respostas
├── RESPOSTAS-SPRINT1.md        # respostas do Sprint 1
├── RESPOSTAS-SPRINT2.md        # respostas do Sprint 2
├── RESPOSTAS-SPRINT3.md        # respostas do Sprint 3
├── ROTEIRO-SPRINT1.md          # enunciado do Sprint 1
├── ROTEIRO-SPRINT2.md          # enunciado do Sprint 2
├── ROTEIRO-SPRINT3.md          # enunciado do Sprint 3
└── README.md
```

### Backend

```text
agencia/
├── requirements.txt
├── pyproject.toml              # configuracao do linter
├── .env.example                # modelo do .env com a RABBITMQ_URL
├── mesclar_logs.py             # linha do tempo causal e pares concorrentes
├── historico_lideranca.py      # linha do tempo de lideres a partir dos logs
├── scripts/                    # verificacoes manuais
│   ├── testar_mensageria.py    # testa o roteamento das filas fora da aplicacao
│   ├── testar_idempotencia.py  # entrega a mesma mensagem de credito duas vezes
│   └── testar_limite_offline.py # limite de saque offline, sem precisar do RabbitMQ
├── data/                       # logs .jsonl gerados em execucao (nao versionados)
└── src/
    ├── main.py                 # monta as camadas e liga o consumidor
    ├── config.py               # particionamento, portas e parametros de JWT
    ├── controllers/            # so HTTP
    │   ├── authController.py
    │   ├── bullyController.py  # eleicao, coordenador e consulta da lider
    │   ├── contasController.py # inclui /sincronizar do app offline
    │   ├── transferenciasController.py
    │   ├── dependencias.py     # JWT, autorizacao e acesso aos services
    │   └── erros.py            # erro de negocio -> status HTTP
    ├── services/               # regras de negocio
    │   ├── auth.py             # senha, token e login
    │   ├── contas_service.py
    │   ├── transferencias_service.py
    │   ├── erros.py            # erros de negocio
    │   ├── bully_service.py    # eleicao, heartbeat e failover
    │   ├── comparar_vetores.py # vetor anterior, posterior, igual ou concorrente
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
    ├── stores/
    │   ├── auth.ts             # sessao (token, perfil, conta, agencia)
    │   └── atividades.ts       # ultimas operacoes da sessao
    ├── utils/formatar.ts       # valores em reais
    ├── components/
    │   ├── AlertaMensagem.vue  # faixa de erro ou sucesso
    │   ├── Icone.vue           # icones da interface
    │   ├── PainelLideranca.vue # lider atual e agencias online
    │   └── SeletorAgencia.vue  # escolha da agencia de acesso
    └── views/
        ├── LoginView.vue       # login de cliente ou operador
        ├── ContaView.vue       # saldo, deposito, saque e abertura de conta
        └── TransferenciaView.vue
```

### App mobile

```text
app_mobile/
├── pubspec.yaml
├── android/                    # projeto Android (permissao de internet e HTTP local)
└── lib/
    ├── main.dart               # troca entre login e inicio conforme a sessao
    ├── core/
    │   ├── api.dart            # chamadas REST e ErroApi (offline, status, corpo)
    │   ├── config.dart         # endereco das agencias e limites offline
    │   └── sessao.dart         # token JWT no shared_preferences
    ├── dados/
    │   ├── banco_local.dart    # SQLite: tabelas contas e pendentes
    │   └── sincronizador.dart  # fila, saldo provisorio, sync e limite offline
    ├── telas/
    │   ├── login.dart
    │   ├── inicio.dart         # saldo, operacoes, fila e painel da lider
    │   └── transferencia.dart
    └── shared/
        ├── utils/formatar.dart
        └── widgets/
            ├── mensagem.dart
            └── painel_lideranca.dart
```

## Como Rodar o Projeto

### Pré-requisitos

- Python 3.12 ou superior
- Node.js 22.18 ou superior (para o frontend)
- Flutter 3.47 com Android SDK e JDK 17 (para o app)
- Celular Android com depuração USB, ou um emulador
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

### 7. Acompanhar a eleição de líder

Com as três agências no ar:

```powershell
8081..8083 | % { Invoke-RestMethod "http://localhost:$_/bully/lider" }
```

Derrube a agência 2 (Ctrl+C) e rode de novo: em alguns segundos, a 0 e a 1 respondem `liderAtual: 1`. Para ver a linha do tempo de líderes, dentro de `agencia/`:

```powershell
.venv\Scripts\python.exe historico_lideranca.py
```

### 8. Rodar o app Flutter

O Flutter e o Gradle quebram com acento no caminho (ex.: "Área de Trabalho"). Nesse caso, mapeie o repositório num drive:

```powershell
subst I: "<caminho do repositorio>"
cd I:\app_mobile
flutter pub get
```

**No emulador**, o app acessa o PC por `10.0.2.2` (o padrão):

```powershell
flutter run
```

**Num celular real por USB**, o `adb reverse` faz o `localhost` do celular apontar para as agências no PC, sem depender do Wi-Fi:

```powershell
adb reverse tcp:8081 tcp:8081
adb reverse tcp:8082 tcp:8082
adb reverse tcp:8083 tcp:8083
flutter run --release --dart-define=HOST=127.0.0.1
```

Para testar o modo offline no celular por USB, ligue o modo avião e rode `adb reverse --remove-all` (o cabo continua conectado no modo avião). Para voltar, recrie os três `adb reverse`.

## Evidências de Teste

Prints de execução real, com a saída de `Get-Date` visível.

### Sprint 3 (`evidencias/sprint3/`)

Os prints do app foram tirados num celular real (USB com `adb reverse`), com a hora na barra de status.

| Arquivo | O que comprova |
| --- | --- |
| `eleicao-inicial.png` | as três agências no ar e `/bully/lider` respondendo `liderAtual: 2` em todas |
| `failover.png` | agência 2 derrubada e as agências 0 e 1 elegendo a 1 sozinhas |
| `historico-lideranca.png` | linha do tempo de líderes gerada pelo `historico_lideranca.py` |
| `conflito-sincronizacao.png` | `/contas/3/sincronizar` recusando com 409 e devolvendo os dois vetores e a conta atual |
| `app-lider-atual.png` | painel do app com a Agência 2 como líder e as três online |
| `app-failover.png` | painel do app depois da queda da 2: Agência 1 líder e a 2 fora do ar |
| `app-offline.png` | app em modo avião com saldo provisório e o depósito na fila |
| `app-sincronizacao.png` | app depois de reconectar: fila enviada sozinha e saldo confirmado |
| `funcionalidade-adicional-limite.png` | saque offline de R$ 250 recusado pelo limite de R$ 200 |
| `funcionalidade-adicional-soma.png` | saque de R$ 150 na fila e saque de R$ 100 recusado com R$ 50 disponível |

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
| [`RESPOSTAS-SPRINT3.md`](RESPOSTAS-SPRINT3.md) | respostas do Sprint 3 |
| [`ROTEIRO-SPRINT1.md`](ROTEIRO-SPRINT1.md) | enunciado do Sprint 1 |
| [`ROTEIRO-SPRINT2.md`](ROTEIRO-SPRINT2.md) | enunciado do Sprint 2 |
| [`ROTEIRO-SPRINT3.md`](ROTEIRO-SPRINT3.md) | enunciado do Sprint 3 |

## Autor

| Nome | Foto | GitHub | LinkedIn |
| --- | --- | --- | --- |
| Eric Leal | <div align="center"><img src="https://github.com/Eric-Leal.png" width="70" height="70" /></div> | <div align="center"><a href="https://github.com/Eric-Leal">@Eric-Leal</a></div> | <div align="center"><a href="https://linkedin.com/in/ericgleal">Perfil</a></div> |

---

Desenvolvido para fins acadêmicos no contexto do Laboratório de Desenvolvimento de Aplicações Móveis e Distribuídas.
