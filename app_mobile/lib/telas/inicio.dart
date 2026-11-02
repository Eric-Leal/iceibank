import 'package:flutter/material.dart';

import '../api.dart' as api;
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
  api.Conta? _conta;
  bool _saldoVisivel = true;
  String? _erro;
  String? _sucesso;

  int get _idConta => sessao.idConta!;

  @override
  void initState() {
    super.initState();
    _buscar();
  }

  Future<void> _buscar() async {
    try {
      final conta = await api.consultarSaldo(_idConta);
      setState(() {
        _conta = conta;
        _erro = null;
      });
    } on api.ErroApi catch (e) {
      if (mounted) setState(() => _erro = e.mensagem);
    }
  }

  Future<void> _operar(bool deposito) async {
    final valor = await _pedirValor(deposito ? 'Valor do depósito' : 'Valor do saque');
    if (valor == null) return;
    setState(() {
      _erro = null;
      _sucesso = null;
    });
    try {
      final conta = deposito ? await api.depositar(_idConta, valor) : await api.sacar(_idConta, valor);
      setState(() {
        _conta = conta;
        _sucesso = '${deposito ? 'Depósito' : 'Saque'} de ${formatarReais(valor)} realizado.';
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
    final cores = Theme.of(context).colorScheme;
    final conta = _conta;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        title: Text(conta == null ? 'Início' : 'Olá, ${conta.nomeAluno.split(' ').first}'),
        actions: [
          IconButton(tooltip: 'Sair', icon: const Icon(Icons.logout), onPressed: sessao.sair),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _buscar,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (_erro != null) ...[Mensagem(_erro!, erro: true), const SizedBox(height: 12)],
            if (_sucesso != null) ...[Mensagem(_sucesso!), const SizedBox(height: 12)],
            Card(
              elevation: 0,
              color: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: BorderSide(color: Colors.grey.shade300),
              ),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Saldo', style: TextStyle(color: cores.primary, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 8),
                    Row(children: [
                      Text(
                        conta == null ? '...' : (_saldoVisivel ? formatarReais(conta.saldo) : 'R\$ •••••'),
                        style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w600),
                      ),
                      IconButton(
                        tooltip: _saldoVisivel ? 'Ocultar saldo' : 'Mostrar saldo',
                        color: cores.primary,
                        icon: Icon(_saldoVisivel ? Icons.visibility_outlined : Icons.visibility_off_outlined),
                        onPressed: () => setState(() => _saldoVisivel = !_saldoVisivel),
                      ),
                    ]),
                    Text('Conta #$_idConta · Agência ${sessao.idAgencia}',
                        style: const TextStyle(color: Colors.black54)),
                    const SizedBox(height: 20),
                    Row(children: [
                      _Atalho(icone: Icons.add, rotulo: 'Depositar', aoTocar: () => _operar(true)),
                      _Atalho(icone: Icons.remove, rotulo: 'Sacar', aoTocar: () => _operar(false)),
                      _Atalho(
                        icone: Icons.swap_horiz,
                        rotulo: 'Transferir',
                        aoTocar: () async {
                          await Navigator.push(
                              context, MaterialPageRoute(builder: (_) => const TelaTransferencia()));
                          _buscar();
                        },
                      ),
                    ]),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            const PainelLideranca(),
          ],
        ),
      ),
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
