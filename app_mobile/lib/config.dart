// 10.0.2.2 e o localhost do PC visto de dentro do emulador Android.
const hostAgencias = String.fromEnvironment('HOST', defaultValue: '10.0.2.2');
const portaBase = 8081;
const numeroAgencias = 3;

String urlAgencia(int idAgencia) => 'http://$hostAgencias:${portaBase + idAgencia}';

/// Mesma regra de particionamento do backend: a conta pertence a agencia `id % 3`.
int agenciaResponsavel(int idConta) => idConta % numeroAgencias;
