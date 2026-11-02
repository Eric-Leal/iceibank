import 'dart:async';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';

import '../api.dart' as api;
import 'banco_local.dart';

const _intervaloNovaTentativa = Duration(seconds: 10);

/// Estado offline-first da conta logada: cache, fila de pendentes e sincronizacao automatica.
class Sincronizador extends ChangeNotifier {
  Sincronizador(this.idConta);

  final int idConta;
  ContaLocal? conta;
  List<Pendente> pendentes = [];
  bool online = true;
  String? erro;
  bool _sincronizando = false;
  StreamSubscription<List<ConnectivityResult>>? _conectividade;
  Timer? _timer;

  /// UI otimista: ultimo saldo confirmado mais o efeito do que ainda esta na fila.
  double? get saldoProvisorio => conta == null
      ? null
      : conta!.saldo +
          pendentes.where((p) => p.status == StatusPendente.pendente).fold(0.0, (s, p) => s + p.efeito);

  bool get temPendentes => pendentes.any((p) => p.status == StatusPendente.pendente);

  Future<void> iniciar() async {
    conta = await bancoLocal.buscarConta(idConta);
    pendentes = await bancoLocal.pendentes(idConta);
    notifyListeners();

    _conectividade = Connectivity().onConnectivityChanged.listen((resultado) {
      if (!resultado.contains(ConnectivityResult.none)) atualizar();
    });
    // Cobre a agencia cair com a rede do celular ligada, que o connectivity_plus nao enxerga.
    _timer = Timer.periodic(_intervaloNovaTentativa, (_) => atualizar());
    await atualizar();
  }

  @override
  void dispose() {
    _conectividade?.cancel();
    _timer?.cancel();
    super.dispose();
  }

  /// Sincroniza a fila e depois busca o saldo real.
  Future<void> atualizar() async {
    await sincronizarFila();
    try {
      await _guardar(await api.consultarSaldo(idConta));
      online = true;
      erro = null;
    } on api.ErroApi catch (e) {
      online = !e.offline;
      erro = e.offline ? null : e.mensagem;
    }
    notifyListeners();
  }

  /// Online aplica direto; sem resposta da agencia vai para a fila. Devolve true se ficou pendente.
  Future<bool> registrar(String tipo, double valor) async {
    try {
      final resultado =
          tipo == 'DEPOSITO' ? await api.depositar(idConta, valor) : await api.sacar(idConta, valor);
      online = true;
      await _guardar(resultado);
      notifyListeners();
      return false;
    } on api.ErroApi catch (e) {
      final base = conta;
      if (!e.offline || base == null) rethrow;
      online = false;
      await bancoLocal.enfileirar(idConta, tipo, valor, base.vetor);
      await _recarregarFila();
      return true;
    }
  }

  Future<void> sincronizarFila() async {
    if (_sincronizando) return;
    _sincronizando = true;
    try {
      for (final item in await bancoLocal.pendentes(idConta)) {
        if (item.status != StatusPendente.pendente) continue;
        try {
          final resultado = await api.sincronizar(idConta, item.tipo, item.valor, item.vetorConhecido);
          online = true;
          await bancoLocal.removerPendente(item.id);
          await _guardar(resultado);
          // As proximas da fila partiram do mesmo vetor; a operacao recem-aplicada foi nossa, nao conflito.
          for (final proxima in await bancoLocal.pendentes(idConta)) {
            if (proxima.status == StatusPendente.pendente && listEquals(proxima.vetorConhecido, item.vetorConhecido)) {
              await bancoLocal.atualizarPendente(proxima.id, vetor: resultado.vetorAtual);
            }
          }
        } on api.ErroApi catch (e) {
          if (e.offline) {
            online = false;
            break;
          }
          if (e.status == 409 && e.corpo != null) {
            final atual = e.corpo!['contaAtual'] as Map<String, dynamic>;
            await _guardar(api.Conta.deJson({...atual, 'vetorAtual': e.corpo!['vetorAtual']}));
          }
          await bancoLocal.atualizarPendente(item.id, status: StatusPendente.conflito, erro: e.mensagem);
          break;
        }
      }
    } finally {
      _sincronizando = false;
      await _recarregarFila();
    }
  }

  Future<void> descartar(Pendente item) async {
    await bancoLocal.removerPendente(item.id);
    await _recarregarFila();
  }

  /// Reaplica a operacao sobre o estado mais recente que a agencia informou.
  Future<void> tentarDeNovo(Pendente item) async {
    await bancoLocal.atualizarPendente(item.id, vetor: conta?.vetor, status: StatusPendente.pendente);
    await sincronizarFila();
  }

  Future<void> _guardar(api.Conta c) async {
    conta = ContaLocal(c.id, c.nomeAluno, c.saldo, c.vetorAtual ?? conta?.vetor ?? const []);
    await bancoLocal.salvarConta(conta!);
  }

  Future<void> _recarregarFila() async {
    pendentes = await bancoLocal.pendentes(idConta);
    notifyListeners();
  }
}
