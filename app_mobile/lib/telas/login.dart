import 'package:flutter/material.dart';

import '../api.dart' as api;
import '../config.dart';
import '../sessao.dart';
import '../widgets/mensagem.dart';

class TelaLogin extends StatefulWidget {
  const TelaLogin({super.key});

  @override
  State<TelaLogin> createState() => _TelaLoginState();
}

class _TelaLoginState extends State<TelaLogin> {
  final _conta = TextEditingController();
  final _senha = TextEditingController();
  int _agencia = sessao.idAgencia;
  String? _erro;
  bool _carregando = false;

  Future<void> _entrar() async {
    final idConta = int.tryParse(_conta.text);
    if (idConta == null || _senha.text.isEmpty) {
      setState(() => _erro = 'Informe o número da conta e a senha.');
      return;
    }
    setState(() {
      _erro = null;
      _carregando = true;
    });
    // A requisicao de login ja precisa ir para a agencia escolhida.
    sessao.idAgencia = _agencia;
    try {
      final token = await api.login(idConta, _senha.text);
      await sessao.entrar(token, idConta, _agencia);
    } on api.ErroApi catch (e) {
      setState(() => _erro = e.mensagem);
    } finally {
      if (mounted) setState(() => _carregando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final cores = Theme.of(context).colorScheme;
    return Scaffold(
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const SizedBox(height: 32),
            Row(children: [
              Container(
                width: 44,
                height: 44,
                alignment: Alignment.center,
                decoration: BoxDecoration(color: cores.primary, borderRadius: BorderRadius.circular(12)),
                child: const Text('IB', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
              const SizedBox(width: 10),
              const Text('ICEIBank', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600)),
            ]),
            const SizedBox(height: 40),
            const Text('Entrar', style: TextStyle(fontSize: 26, fontWeight: FontWeight.w600)),
            const SizedBox(height: 4),
            const Text('Escolha a agência e informe seus dados.', style: TextStyle(color: Colors.black54)),
            const SizedBox(height: 24),
            DropdownButtonFormField<int>(
              initialValue: _agencia,
              decoration: const InputDecoration(labelText: 'Agência de acesso'),
              items: [
                for (var id = 0; id < numeroAgencias; id++)
                  DropdownMenuItem(value: id, child: Text('Agência $id (porta ${portaBase + id})')),
              ],
              onChanged: (id) => setState(() => _agencia = id!),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _conta,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Número da conta'),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _senha,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'Senha'),
              onSubmitted: (_) => _entrar(),
            ),
            const SizedBox(height: 16),
            if (_erro != null) Mensagem(_erro!, erro: true),
            const SizedBox(height: 8),
            FilledButton(
              onPressed: _carregando ? null : _entrar,
              child: Text(_carregando ? 'Entrando...' : 'Entrar'),
            ),
          ],
        ),
      ),
    );
  }
}
