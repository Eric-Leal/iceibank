# RESPOSTAS (ICEIBank - Sprint 1)

## Parte B (Relógio de Lamport e registro de eventos)

1. **Por que o relógio de Lamport usa `max(contador_local, timestampRecebido) + 1` ao receber uma mensagem, em vez de simplesmente adotar o timestamp recebido diretamente?**

   **Resposta:** A regra existe para o contador ficar **sempre maior que os dois valores** (o local e o recebido), e cada metade da fórmula resolve um problema.

   O `max` impede que o contador **retroceda**: se a agência está em 10 e recebe 3, adotar o 3 faria eventos futuros dela receberem timestamps menores que eventos que ela já registrou, quebrando a ordem dos seus próprios eventos.

   O `+ 1` garante que o recebimento seja **estritamente posterior** ao envio. Sem ele, envio e recebimento ficariam com o mesmo timestamp e a relação *happened-before* entre os dois sumiria do relógio. É isso que sustenta a ordem parcial de causa e efeito: se A aconteceu antes de B causalmente, então `timestamp(A) < timestamp(B)`.

   No código, é o `ao_receber` de `relogio_lamport.py`, usado pela agência de destino quando recebe um crédito remoto de outra agência.

2. **Se a Agência 0 está no evento de contador 10 e recebe uma mensagem com timestamp 3 (de uma agência mais "atrasada"), qual o novo valor do contador da Agência 0? O que isso implica sobre agências que processam muitos eventos rapidamente versus agências mais lentas?**

   **Resposta:** `max(10, 3) + 1 = 11`. A mensagem atrasada não puxa a Agência 0 pra trás, ela só avança 1, como em qualquer evento local.

   Isso significa que o ajuste só acontece **para cima**: a agência lenta salta pra frente ao receber mensagem de uma rápida, mas a rápida nunca é freada pela lenta. Como cada uma conta só os próprios eventos, duas agências rodando ao mesmo tempo podem ter contadores bem diferentes.

   Ou seja, o contador não mede tempo real nem quantidade de trabalho, ele só garante a ordem de causa e efeito entre eventos que se comunicaram.

## Parte D (Transferências)

1. **No trecho `agenciaDestino === idAgencia`, por que a transferência local não precisa da lógica de `aoEnviar()`/`aoReceber()` do relógio de Lamport, enquanto a transferência entre agências precisa?**

2. **Reproduza a falha conhecida e observe o saldo da conta de origem depois do erro. Ele foi revertido? O que isso significa em termos de consistência do sistema bancário?**

3. **Pensando à frente para o Sprint 4: cite, em alto nível, duas formas possíveis de corrigir esse problema.**

## Parte E (Linha do tempo unificada)

1. **O relógio de Lamport garante que, se A aconteceu antes de B causalmente, `timestamp(A) < timestamp(B)`. Ele não garante a volta. O que isso significa na prática quando você vê dois eventos com timestamps diferentes na linha do tempo, mas sem saber se um realmente influenciou o outro?**

2. **O relógio de Lamport, sozinho, seria suficiente para um sistema que precisa distinguir com certeza "A e B são concorrentes" de "A aconteceu antes de B"? Por que isso motiva o relógio vetorial do Sprint 2?**

Observação do passo 3 da tarefa (eventos com mesmo timestamp, comparação com `horaParede`):

## Parte F (Autenticação JWT)

1. **Qual a diferença entre autenticação e autorização? Sua implementação verifica só uma das duas, ou as duas?**

2. **Por que o servidor não precisa consultar um banco de dados para validar a assinatura de um JWT a cada requisição? O que isso implica sobre escalabilidade?**

3. **O que aconteceria com a segurança do sistema se a chave secreta usada para assinar o JWT vazasse?**

Decisões de design (formato das credenciais, expiração do token, tratamento da chamada `creditar-remoto` entre agências):

## Parte G (Frontend)

1. **Como o frontend "lembra" de reenviar o token em cada requisição depois do login?**

2. **Se o token expirar enquanto alguém está usando o frontend no meio de uma operação, o que acontece na sua implementação?**

3. **No seu frontend, onde fica o "M" (Model), o "V" (View) e o "C" (Controller)?**

## Funcionalidade adicional (seção 2.1)

Descrição da funcionalidade escolhida e justificativa:
