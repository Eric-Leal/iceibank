import 'dart:async';

import 'package:flutter/material.dart';

import '../api.dart' as api;
import '../config.dart';

const _intervalo = Duration(seconds: 3);

/// Consulta /bully/lider nas 3 agencias a cada 3s: se uma cair, as outras respondem.
class PainelLideranca extends StatefulWidget {
  const PainelLideranca({super.key});

  @override
  State<PainelLideranca> createState() => _PainelLiderancaState();
}

class _PainelLiderancaState extends State<PainelLideranca> {
  int? _lider;
  List<bool> _ativas = List.filled(numeroAgencias, false);
  bool _consultou = false;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _atualizar();
    _timer = Timer.periodic(_intervalo, (_) => _atualizar());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _atualizar() async {
    final respostas = await Future.wait([
      for (var id = 0; id < numeroAgencias; id++)
        api.consultarLider(id).then<(bool, int?)>((l) => (true, l)).catchError((_) => (false, null)),
    ]);
    if (!mounted) return;
    setState(() {
      _consultou = true;
      _ativas = [for (final r in respostas) r.$1];
      // Na transicao duas agencias podem discordar; vale a de maior id que respondeu.
      _lider = respostas.where((r) => r.$1 && r.$2 != null).map((r) => r.$2).lastOrNull;
    });
  }

  @override
  Widget build(BuildContext context) {
    final cores = Theme.of(context).colorScheme;
    return Card(
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
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Líder atual', style: TextStyle(fontWeight: FontWeight.w600)),
                Row(children: [
                  Icon(Icons.circle, size: 8, color: cores.primary),
                  const SizedBox(width: 4),
                  const Text('ao vivo', style: TextStyle(fontSize: 12, color: Colors.black54)),
                ]),
              ],
            ),
            const SizedBox(height: 14),
            Row(children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(color: Colors.amber.shade100, borderRadius: BorderRadius.circular(12)),
                child: Icon(Icons.workspace_premium, color: Colors.amber.shade800),
              ),
              const SizedBox(width: 12),
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(
                  !_consultou
                      ? 'Consultando...'
                      : !_ativas.contains(true)
                          ? 'Sem conexão'
                          : (_lider == null ? 'Sem líder' : 'Agência $_lider'),
                  style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w600),
                ),
                const Text('Eleita pelo algoritmo de Bully',
                    style: TextStyle(fontSize: 12, color: Colors.black54)),
              ]),
            ]),
            const SizedBox(height: 14),
            for (var id = 0; id < numeroAgencias; id++)
              Container(
                margin: const EdgeInsets.only(top: 6),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(8)),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Agência $id'),
                    Row(children: [
                      Icon(Icons.circle, size: 8, color: _ativas[id] ? cores.primary : Colors.red),
                      const SizedBox(width: 6),
                      Text(
                        _ativas[id] ? 'Online' : 'Fora do ar',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: _ativas[id] ? cores.primary : Colors.red,
                        ),
                      ),
                    ]),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
