/// Formata no padrao brasileiro (R$ 1.234,56) sem depender do pacote intl.
String formatarReais(double valor) {
  final partes = valor.abs().toStringAsFixed(2).split('.');
  final inteiro = partes[0].replaceAllMapped(RegExp(r'\B(?=(\d{3})+(?!\d))'), (_) => '.');
  return '${valor < 0 ? '-' : ''}R\$ $inteiro,${partes[1]}';
}
