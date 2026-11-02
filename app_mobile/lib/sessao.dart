import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Token JWT e agencia de acesso, persistidos para sobreviver ao fechamento do app.
class Sessao extends ChangeNotifier {
  String? token;
  int? idConta;
  int idAgencia = 0;

  bool get autenticada => token != null;

  Future<void> carregar() async {
    final prefs = await SharedPreferences.getInstance();
    token = prefs.getString('token');
    idConta = prefs.getInt('idConta');
    idAgencia = prefs.getInt('idAgencia') ?? 0;
  }

  Future<void> entrar(String novoToken, int conta, int agencia) async {
    token = novoToken;
    idConta = conta;
    idAgencia = agencia;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', novoToken);
    await prefs.setInt('idConta', conta);
    await prefs.setInt('idAgencia', agencia);
    notifyListeners();
  }

  Future<void> sair() async {
    token = null;
    idConta = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    await prefs.remove('idConta');
    notifyListeners();
  }
}

final sessao = Sessao();
