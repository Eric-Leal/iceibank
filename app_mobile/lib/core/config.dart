// 10.0.2.2 e o localhost do PC visto de dentro do emulador Android.
const hostAgencias = String.fromEnvironment('HOST', defaultValue: '10.0.2.2');
const portaBase = 8081;
const numeroAgencias = 3;

String urlAgencia(int idAgencia) => 'http://$hostAgencias:${portaBase + idAgencia}';

/// Funcionalidade adicional: sem a agencia conferir o saldo, saque offline e risco.
/// O backend tambem barra cada saque acima do limite (`LIMITE_SAQUE_OFFLINE`).
const limiteSaqueOffline = 200.0;
const maxOperacoesOffline = 5;

/// Mesma regra de particionamento do backend: a conta pertence a agencia `id % 3`.
int agenciaResponsavel(int idConta) => idConta % numeroAgencias;
