import amqp from 'amqplib';

const URL_RABBITMQ = process.env.RABBITMQ_URL;
const EXCHANGE = 'iceibank.eventos';

if (!URL_RABBITMQ) {
  console.error('Defina a variável de ambiente RABBITMQ_URL com a URL AMQP da sua instância CloudAMQP antes de iniciar.');
  process.exit(1);
}

let canalCache = null;

async function obterCanal() {
  if (canalCache) return canalCache;
  const conexao = await amqp.connect(URL_RABBITMQ);
  const canal = await conexao.createChannel();
  await canal.assertExchange(EXCHANGE, 'topic', { durable: true });
  canalCache = canal;
  return canal;
}

async function publicar(routingKey, mensagem) {
  const canal = await obterCanal();
  canal.publish(EXCHANGE, routingKey, Buffer.from(JSON.stringify(mensagem)), { persistent: true });
}

async function assinar(idAgencia, aoReceberMensagem) {
  const canal = await obterCanal();
  const nomeFila = `fila-agencia-${idAgencia}`;
  await canal.assertQueue(nomeFila, { durable: true });
  await canal.bindQueue(nomeFila, EXCHANGE, `agencia.${idAgencia}.creditar`);
  canal.consume(nomeFila, (msg) => {
    if (msg) {
      const conteudo = JSON.parse(msg.content.toString());
      aoReceberMensagem(conteudo);
      canal.ack(msg);
    }
  });
}

export { publicar, assinar };
