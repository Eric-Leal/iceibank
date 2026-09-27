import express from 'express';
import * as config from './config.js';
import RelogioVetorial from './services/vectorClock.js';
import RegistroEventos from './services/eventLog.js';
import { assinar } from './services/mensageria.js';
import routes from './routes.js';

const idAgencia = parseInt(process.env.AGENCIA_ID || '0', 10);
const agenciaConfig = config.AGENCIAS.find((a) => a.id === idAgencia);

if (!agenciaConfig) {
  console.error(`Agência ${idAgencia} não configurada em config.js`);
  process.exit(1);
}

const app = express();
app.use(express.json());

const relogio = new RelogioVetorial(idAgencia, config.NUMERO_AGENCIAS);
const registro = new RegistroEventos(`agencia-${idAgencia}`);
const contas = new Map();

app.locals.idAgencia = idAgencia;
app.locals.relogio = relogio;
app.locals.registro = registro;
app.locals.contas = contas;

app.use('/', routes);

// Consumidor: processa creditos vindos de outras agencias via RabbitMQ
assinar(idAgencia, (mensagem) => {
  const { idConta, valor, vetorEnvio, origemAgencia } = mensagem;
  const vetor = relogio.aoReceber(vetorEnvio);

  const conta = contas.get(idConta);
  if (!conta) {
    registro.registrar('CREDITO_REMOTO_FALHOU', vetor, { idConta, valor, origemAgencia, motivo: 'conta nao encontrada' });
    return;
  }

  conta.saldo += valor;
  registro.registrar('TRANSFERENCIA_CREDITO_REMOTO', vetor, { idConta, valor, origemAgencia });
});

const porta = new URL(agenciaConfig.url).port;
app.listen(porta, () => {
  console.log(`[Agência ${idAgencia}] ouvindo na porta ${porta}`);
});
