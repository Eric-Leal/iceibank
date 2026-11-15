import 'package:flutter/material.dart';

class Mensagem extends StatelessWidget {
  const Mensagem(this.texto, {super.key, this.erro = false});

  final String texto;
  final bool erro;

  @override
  Widget build(BuildContext context) {
    final cor = erro ? Colors.red : const Color(0xFF027A48);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: cor.withValues(alpha: 0.08),
        border: Border.all(color: cor.withValues(alpha: 0.4)),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Text(texto, style: TextStyle(color: cor)),
    );
  }
}
