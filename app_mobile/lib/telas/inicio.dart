import 'package:flutter/material.dart';

import '../api.dart' as api;
import '../dados/banco_local.dart';
import '../dados/sincronizador.dart';
import '../formatar.dart';
import '../sessao.dart';
import '../widgets/mensagem.dart';
import '../widgets/painel_lideranca.dart';
import 'transferencia.dart';

class TelaInicio extends StatefulWidget {
  const TelaInicio({super.key});

  @override
  State<TelaInicio> createState() => _TelaInicioState();
}

class _TelaInicioState extends State<TelaInicio> {
  late final Sincronizador _sync = Sincronizador(sessao.idConta!);
  bool _saldoVisivel = true;
  String? _erro;
  String? _sucesso;
  bool _avisoDePendente = false;

  @override
  void initState() {
    super.initState();
    _sync.iniciar();
  }

  @override
  void dispose() {
    _sync.dispose();
    super.dispose();
  }

  Future<void> _operar(bool deposito) async {
    final valor = await _pedirValor(deposito ? 'Valor do depósito' : 'Valor do saque');
    if (valor == null) return;
    setState(() {
      _erro = null;
      _sucesso = null;
    });
    final nome = deposito ? 'Depósito' : 'Saque';
    try {
      final ficouPendente = await _sync.registrar(deposito ? 'DEPOSITO' : 'SAQUE', valor);
      setState(() {
        _avisoDePendente = ficouPendente;
        _sucesso = ficouPendente
            ? '$nome de ${formatarReais(valor)} guardado. Será enviado quando a conexão voltar.'
            : '$nome de ${formatarReais(valor)} realizado.';
      });
    } on api.ErroApi catch (e) {
      if (mounted) setState(() => _erro = e.mensagem);
    }
  }

  Future<double?> _pedirValor(String titulo) {
    final campo = TextEditingController();
    return showModalBottomSheet<double>(
      context: context,
      isScrollControlled: true,
      builder: (context) => Padding(
        padding: EdgeInsets.fromLTRB(24, 24, 24, MediaQuery.of(context).viewInsets.bottom + 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(titulo, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
            const SizedBox(height: 16),
            TextField(
              controller: campo,
              autofocus: true,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(prefixText: 'R\$ '),
            ),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () {
                final valor = double.tryParse(campo.text.replaceAll(',', '.'));
                if (valor != null && valor > 0) Navigator.pop(context, valor);
              },
              child: const Text('Confirmar'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: _sync,
      builder: (context, _) {
        final conta = _sync.conta;
        return Scaffold(
          appBar: AppBar(
            backgroundColor: Colors.white,
            title: Text(conta == null ? 'Início' : 'Olá, ${conta.nomeAluno.split(' ').first}'),
            actions: [
              IconButton(tooltip: 'Sair', icon: const Icon(Icons.logout), onPressed: sessao.sair),
            ],
          ),
          body: RefreshIndicator(
            onRefresh: _sync.atualizar,
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (!_sync.online) ...[
                  const _AvisoOffline(),
                  const SizedBox(height: 12),
                ],
                for (final texto in [_erro ?? _sync.erro].whereType<String>()) ...[
                  Mensagem(texto, erro: true),
                  const SizedBox(height: 12),
                ],
                // O aviso de "guardado" envelhece: some no conflito e vira confirmacao quando a fila esvazia.
                if (_sucesso != null && !(_avisoDePendente && _sync.pendentes.isNotEmpty && !_sync.temPendentes)) ...[
                  Mensagem(_avisoDePendente && _sync.pendentes.isEmpty
                      ? 'Operações feitas offline sincronizadas com a agência.'
                      : _sucesso!),
                  const SizedBox(height: 12),
                ],
                _cartaoSaldo(context),
                if (_sync.pendentes.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  _listaPendentes(),
                ],
                const SizedBox(height: 16),
                const PainelLideranca(),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _cartaoSaldo(BuildContext context) {
    final cores = Theme.of(context).colorScheme;
    final saldo = _sync.saldoProvisorio;
    return _Cartao(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Text(_sync.temPendentes ? 'Saldo provisório' : 'Saldo',
                style: TextStyle(color: cores.primary, fontWeight: FontWeight.w600)),
            if (_sync.temPendentes) ...[const SizedBox(width: 8), const _Selo('pendente', Colors.amber)],
          ]),
          const SizedBox(height: 8),
          Row(children: [
            Text(
              saldo == null ? '...' : (_saldoVisivel ? formatarReais(saldo) : 'R\$ •••••'),
              style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w600),
            ),
            IconButton(
              tooltip: _saldoVisivel ? 'Ocultar saldo' : 'Mostrar saldo',
              color: cores.primary,
              icon: Icon(_saldoVisivel ? Icons.visibility_outlined : Icons.visibility_off_outlined),
              onPressed: () => setState(() => _saldoVisivel = !_saldoVisivel),
            ),
          ]),
          Text('Conta #${sessao.idConta} · Agência ${sessao.idAgencia}',
              style: const TextStyle(color: Colors.black54)),
          const SizedBox(height: 20),
          Row(children: [
            _Atalho(icone: Icons.add, rotulo: 'Depositar', aoTocar: () => _operar(true)),
            _Atalho(icone: Icons.remove, rotulo: 'Sacar', aoTocar: () => _operar(false)),
            _Atalho(
              icone: Icons.swap_horiz,
              rotulo: 'Transferir',
              aoTocar: () async {
                await Navigator.push(context, MaterialPageRoute(builder: (_) => const TelaTransferencia()));
                _sync.atualizar();
              },
            ),
          ]),
        ],
      ),
    );
  }

  Widget _listaPendentes() {
    return _Cartao(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Aguardando sincronização', style: TextStyle(fontWeight: FontWeight.w600)),
          for (final p in _sync.pendentes) ...[
            const Divider(height: 24),
            Row(children: [
              Icon(
                p.status == StatusPendente.pendente ? Icons.schedule : Icons.error_outline,
                color: p.status == StatusPendente.pendente ? Colors.amber.shade800 : Colors.red,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text('${p.tipo == 'DEPOSITO' ? 'Depósito' : 'Saque'} de ${formatarReais(p.valor)}',
                      style: const TextStyle(fontWeight: FontWeight.w500)),
                  Text(
                    p.status == StatusPendente.pendente ? 'Será enviado automaticamente' : 'Não aplicado: ${p.erro}',
                    style: TextStyle(
                        fontSize: 12, color: p.status == StatusPendente.pendente ? Colors.black54 : Colors.red),
                  ),
                ]),
              ),
            ]),
            if (p.status == StatusPendente.conflito) ...[
              const SizedBox(height: 8),
              Text(
                'Saldo real na agência: ${formatarReais(_sync.conta?.saldo ?? 0)}. '
                'Confira antes de reenviar.',
                style: const TextStyle(fontSize: 12),
              ),
              Row(mainAxisAlignment: MainAxisAlignment.end, children: [
                TextButton(onPressed: () => _sync.descartar(p), child: const Text('Descartar')),
                FilledButton.tonal(
                  style: FilledButton.styleFrom(minimumSize: const Size(0, 40)),
                  onPressed: () => _sync.tentarDeNovo(p),
                  child: const Text('Reenviar'),
                ),
              ]),
            ],
          ],
        ],
      ),
    );
  }
}

class _AvisoOffline extends StatelessWidget {
  const _AvisoOffline();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: Colors.grey.shade200, borderRadius: BorderRadius.circular(10)),
      child: const Row(children: [
        Icon(Icons.cloud_off, size: 20),
        SizedBox(width: 10),
        Expanded(child: Text('Sem conexão com a agência. Mostrando o último saldo conhecido.')),
      ]),
    );
  }
}

class _Selo extends StatelessWidget {
  const _Selo(this.texto, this.cor);

  final String texto;
  final MaterialColor cor;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(color: cor.shade100, borderRadius: BorderRadius.circular(20)),
      child: Text(texto, style: TextStyle(fontSize: 11, color: cor.shade900, fontWeight: FontWeight.w600)),
    );
  }
}

class _Cartao extends StatelessWidget {
  const _Cartao({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      margin: EdgeInsets.zero,
      color: Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: Colors.grey.shade300),
      ),
      child: Padding(padding: const EdgeInsets.all(20), child: child),
    );
  }
}

class _Atalho extends StatelessWidget {
  const _Atalho({required this.icone, required this.rotulo, required this.aoTocar});

  final IconData icone;
  final String rotulo;
  final VoidCallback aoTocar;

  @override
  Widget build(BuildContext context) {
    final cores = Theme.of(context).colorScheme;
    return Expanded(
      child: InkWell(
        onTap: aoTocar,
        borderRadius: BorderRadius.circular(12),
        child: Column(children: [
          CircleAvatar(
            radius: 26,
            backgroundColor: cores.primary.withValues(alpha: 0.1),
            child: Icon(icone, color: cores.primary),
          ),
          const SizedBox(height: 6),
          Text(rotulo, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
        ]),
      ),
    );
  }
}
