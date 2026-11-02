import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math';

import 'package:http/http.dart' as http;

import 'config.dart';
import 'sessao.dart';

const _timeout = Duration(seconds: 5);

class ErroApi implements Exception {
  ErroApi(this.mensagem, {this.offline = false, this.status, this.corpo});
  final String mensagem;
  /// Sem resposta da agencia: a operacao pode ir para a fila offline.
  final bool offline;
  final int? status;
  final Map<String, dynamic>? corpo;

  @override
  String toString() => mensagem;
}

class Conta {
  Conta(this.id, this.nomeAluno, this.saldo, this.vetorAtual);
  final int id;
  final String nomeAluno;
  final double saldo;
  final List<int>? vetorAtual;

  factory Conta.deJson(Map<String, dynamic> json) => Conta(
        json['id'] as int,
        json['nomeAluno'] as String,
        (json['saldo'] as num).toDouble(),
        json['vetorAtual'] == null ? null : List<int>.from(json['vetorAtual'] as List),
      );
}

Future<dynamic> _requisitar(String metodo, String caminho, {Object? corpo}) async {
  final uri = Uri.parse('${urlAgencia(sessao.idAgencia)}$caminho');
  final cabecalhos = {
    'Content-Type': 'application/json',
    if (sessao.token != null) 'Authorization': 'Bearer ${sessao.token}',
  };

  final http.Response resposta;
  try {
    resposta = await (metodo == 'GET'
            ? http.get(uri, headers: cabecalhos)
            : http.post(uri, headers: cabecalhos, body: jsonEncode(corpo)))
        .timeout(_timeout);
  } on SocketException {
    throw ErroApi('Agência fora do ar ou inacessível.', offline: true);
  } on TimeoutException {
    throw ErroApi('Agência fora do ar ou inacessível.', offline: true);
  } on http.ClientException {
    throw ErroApi('Agência fora do ar ou inacessível.', offline: true);
  }

  final dados = resposta.body.isEmpty ? null : jsonDecode(utf8.decode(resposta.bodyBytes));
  if (resposta.statusCode >= 400) {
    final detalhe = dados is Map ? dados['detail'] : null;
    if (resposta.statusCode == 401) {
      await sessao.sair();
      throw ErroApi(detalhe is String ? detalhe : 'Sessão expirada. Faça login novamente.');
    }
    throw ErroApi(
      detalhe is String ? detalhe : 'Erro ${resposta.statusCode} na agência.',
      status: resposta.statusCode,
      corpo: dados is Map<String, dynamic> ? dados : null,
    );
  }
  return dados;
}

Future<String> login(int idConta, String senha) async {
  final dados = await _requisitar('POST', '/auth/login', corpo: {'id': idConta, 'senha': senha});
  return dados['token'] as String;
}

Future<Conta> consultarSaldo(int id) async =>
    Conta.deJson(await _requisitar('GET', '/contas/$id'));

Future<Conta> depositar(int id, double valor) async =>
    Conta.deJson(await _requisitar('POST', '/contas/$id/depositar', corpo: {'valor': valor}));

Future<Conta> sacar(int id, double valor) async =>
    Conta.deJson(await _requisitar('POST', '/contas/$id/sacar', corpo: {'valor': valor}));

Future<Conta> sincronizar(int id, String tipo, double valor, List<int> vetorConhecido) async =>
    Conta.deJson(await _requisitar('POST', '/contas/$id/sincronizar',
        corpo: {'tipo': tipo, 'valor': valor, 'vetorConhecido': vetorConhecido}));

Future<String> transferir(int idOrigem, int idDestino, double valor, String idOperacao) async {
  final dados = await _requisitar('POST', '/transferencias', corpo: {
    'idOrigem': idOrigem,
    'idDestino': idDestino,
    'valor': valor,
    'idOperacao': idOperacao,
  });
  return dados['mensagem'] as String;
}

/// Rota publica, consultada direto na agencia indicada com timeout curto.
Future<int?> consultarLider(int idAgencia) async {
  final resposta = await http
      .get(Uri.parse('${urlAgencia(idAgencia)}/bully/lider'))
      .timeout(const Duration(milliseconds: 1500));
  if (resposta.statusCode != 200) throw ErroApi('Agência $idAgencia não respondeu.');
  return jsonDecode(resposta.body)['liderAtual'] as int?;
}

String novoIdOperacao() {
  final aleatorio = Random.secure();
  return List.generate(16, (_) => aleatorio.nextInt(256).toRadixString(16).padLeft(2, '0')).join();
}
