import 'package:flutter/material.dart';

import '../api.dart' as api;
import '../config.dart';
import '../sessao.dart';
import '../widgets/mensagem.dart';

class TelaTransferencia extends StatefulWidget {
  const TelaTransferencia({super.key});

  @override
  State<TelaTransferencia> createState() => _TelaTransferenciaState();
}

class _TelaTransferenciaState extends State<TelaTransferencia> {
  final _destino = TextEditingController();
  final _valor = TextEditingController();
  // Nasce com a intencao de transferir, nao com o envio: dois toques mandam o mesmo id.
  String _idOperacao = api.novoIdOperacao();
  String? _erro;
  String? _sucesso;
  bool _enviando = false;

  int get _origem => sessao.idConta!;

  Future<void> _enviar() async {
    final destino = int.tryParse(_destino.text);
    final valor = double.tryParse(_valor.text.replaceAll(',', '.'));
    if (destino == null || valor == null || valor <= 0) {
      setState(() => _erro = 'Informe a conta de destino e um valor válido.');
      return;
    }
    setState(() {
      _erro = null;
      _sucesso = null;
      _enviando = true;
    });
    try {
      final mensagem = await api.transferir(_origem, destino, valor, _idOperacao);
      setState(() {
        _sucesso = mensagem;
        _valor.clear();
        _idOperacao = api.novoIdOperacao();
      });
    } on api.ErroApi catch (e) {
      if (mounted) setState(() => _erro = e.mensagem);
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final destino = int.tryParse(_destino.text);
    final tipo = destino == null
        ? '—'
        : agenciaResponsavel(destino) == agenciaResponsavel(_origem)
            ? 'Local (mesma agência)'
            : 'Entre agências (${agenciaResponsavel(_origem)} → ${agenciaResponsavel(destino)})';

    return Scaffold(
      appBar: AppBar(backgroundColor: Colors.white, title: const Text('Transferir')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextFormField(
            enabled: false,
            initialValue: '#$_origem',
            decoration: const InputDecoration(labelText: 'Conta de origem'),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _destino,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(labelText: 'Conta de destino'),
            onChanged: (_) => setState(() {}),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _valor,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w600),
            decoration: const InputDecoration(labelText: 'Valor', prefixText: 'R\$ '),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Tipo previsto'),
                Flexible(child: Text(tipo, style: const TextStyle(fontWeight: FontWeight.w600))),
              ],
            ),
          ),
          const SizedBox(height: 16),
          if (_erro != null) Mensagem(_erro!, erro: true),
          if (_sucesso != null) Mensagem(_sucesso!),
          const SizedBox(height: 8),
          FilledButton(
            onPressed: _enviando ? null : _enviar,
            child: Text(_enviando ? 'Enviando...' : 'Transferir'),
          ),
        ],
      ),
    );
  }
}
