import 'dart:convert';

import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

class ContaLocal {
  ContaLocal(this.id, this.nomeAluno, this.saldo, this.vetor);
  final int id;
  final String nomeAluno;
  final double saldo;
  final List<int> vetor;
}

enum StatusPendente { pendente, conflito }

class Pendente {
  Pendente({
    required this.id,
    required this.idConta,
    required this.tipo,
    required this.valor,
    required this.vetorConhecido,
    required this.status,
    this.erro,
  });

  final int id;
  final int idConta;
  final String tipo; // DEPOSITO ou SAQUE, como o backend espera
  final double valor;
  final List<int> vetorConhecido;
  final StatusPendente status;
  final String? erro;

  /// Efeito esperado no saldo, usado na UI otimista.
  double get efeito => tipo == 'DEPOSITO' ? valor : -valor;

  factory Pendente._deLinha(Map<String, Object?> l) => Pendente(
        id: l['id'] as int,
        idConta: l['id_conta'] as int,
        tipo: l['tipo'] as String,
        valor: (l['valor'] as num).toDouble(),
        vetorConhecido: List<int>.from(jsonDecode(l['vetor_conhecido'] as String)),
        status: StatusPendente.values.byName(l['status'] as String),
        erro: l['erro'] as String?,
      );
}

/// Cache do ultimo saldo conhecido e fila de operacoes feitas sem conexao.
class BancoLocal {
  Database? _db;

  Future<Database> get _banco async => _db ??= await openDatabase(
        join(await getDatabasesPath(), 'iceibank.db'),
        version: 1,
        onCreate: (db, _) async {
          await db.execute(
              'CREATE TABLE contas (id INTEGER PRIMARY KEY, nome_aluno TEXT, saldo REAL, vetor TEXT)');
          await db.execute('CREATE TABLE pendentes (id INTEGER PRIMARY KEY AUTOINCREMENT, '
              'id_conta INTEGER, tipo TEXT, valor REAL, vetor_conhecido TEXT, status TEXT, erro TEXT)');
        },
      );

  Future<void> salvarConta(ContaLocal c) async {
    await (await _banco).insert(
      'contas',
      {'id': c.id, 'nome_aluno': c.nomeAluno, 'saldo': c.saldo, 'vetor': jsonEncode(c.vetor)},
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<ContaLocal?> buscarConta(int id) async {
    final linhas = await (await _banco).query('contas', where: 'id = ?', whereArgs: [id]);
    if (linhas.isEmpty) return null;
    final l = linhas.first;
    return ContaLocal(l['id'] as int, l['nome_aluno'] as String, (l['saldo'] as num).toDouble(),
        List<int>.from(jsonDecode(l['vetor'] as String)));
  }

  Future<void> enfileirar(int idConta, String tipo, double valor, List<int> vetorConhecido) async {
    await (await _banco).insert('pendentes', {
      'id_conta': idConta,
      'tipo': tipo,
      'valor': valor,
      'vetor_conhecido': jsonEncode(vetorConhecido),
      'status': StatusPendente.pendente.name,
    });
  }

  Future<List<Pendente>> pendentes(int idConta) async {
    final linhas = await (await _banco)
        .query('pendentes', where: 'id_conta = ?', whereArgs: [idConta], orderBy: 'id');
    return linhas.map(Pendente._deLinha).toList();
  }

  Future<void> atualizarPendente(int id, {List<int>? vetor, StatusPendente? status, String? erro}) async {
    await (await _banco).update(
      'pendentes',
      {
        if (vetor != null) 'vetor_conhecido': jsonEncode(vetor),
        if (status != null) 'status': status.name,
        'erro': erro,
      },
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<void> removerPendente(int id) async {
    await (await _banco).delete('pendentes', where: 'id = ?', whereArgs: [id]);
  }
}

final bancoLocal = BancoLocal();
