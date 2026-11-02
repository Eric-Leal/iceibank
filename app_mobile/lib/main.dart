import 'package:flutter/material.dart';

import 'sessao.dart';
import 'telas/inicio.dart';
import 'telas/login.dart';

const corMarca = Color(0xFF039855);

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await sessao.carregar();
  runApp(const IceiBankApp());
}

class IceiBankApp extends StatelessWidget {
  const IceiBankApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ICEIBank',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: corMarca, primary: corMarca),
        scaffoldBackgroundColor: const Color(0xFFF8FAFC),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            minimumSize: const Size.fromHeight(48),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
        ),
      ),
      // Troca de tela sozinho quando a sessao muda (login, logout ou 401).
      home: ListenableBuilder(
        listenable: sessao,
        builder: (context, _) => sessao.autenticada ? const TelaInicio() : const TelaLogin(),
      ),
    );
  }
}
