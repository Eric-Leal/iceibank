import * as config from '../config.js';
import { publicar } from '../services/mensageria.js';

async function transferir(req, res) {
  const { contas, relogio, registro, idAgencia } = req.app.locals;
  const { idOrigem, idDestino, valor } = req.body;

  const contaOrigem = contas.get(idOrigem);
  if (!contaOrigem) return res.status(404).json({ erro: 'Conta de origem não encontrada nesta agência.' });
  if (contaOrigem.saldo < valor) return res.status(400).json({ erro: 'Saldo insuficiente.' });

  const agenciaDestino = config.agenciaResponsavel(idDestino);

  const vetorDebito = relogio.eventoLocal();
  contaOrigem.saldo -= valor;
  registro.registrar('TRANSFERENCIA_DEBITO', vetorDebito, { idOrigem, idDestino, valor });

  if (agenciaDestino === idAgencia) {
    const contaDestino = contas.get(idDestino);
    if (!contaDestino) {
      contaOrigem.saldo += valor;
      return res.status(404).json({ erro: 'Conta de destino não encontrada.' });
    }
    const vetorCredito = relogio.eventoLocal();
    contaDestino.saldo += valor;
    registro.registrar('TRANSFERENCIA_CREDITO', vetorCredito, { idOrigem, idDestino, valor });
    return res.json({ mensagem: 'Transferência concluída (mesma agência).' });
  }

  // Em vez de chamar a outra agência diretamente (Sprint 1), publicamos um
  // evento na exchange do RabbitMQ. A agência de destino consome quando
  // estiver disponível - mesmo que esteja fora do ar agora, a mensagem fica
  // retida na fila (durable) e é entregue quando ela voltar.
  const vetorEnvio = relogio.aoEnviar();
  await publicar(`agencia.${agenciaDestino}.creditar`, {
    idConta: idDestino,
    valor,
    vetorEnvio,
    origemAgencia: idAgencia,
  });

  res.json({ mensagem: 'Transferência publicada para a agência de destino (entrega assíncrona).' });
}

export { transferir };
