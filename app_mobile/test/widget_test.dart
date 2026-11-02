import 'package:flutter_test/flutter_test.dart';

import 'package:iceibank/formatar.dart';

void main() {
  test('formata no padrao brasileiro', () {
    expect(formatarReais(1750), r'R$ 1.750,00');
    expect(formatarReais(1234567.5), r'R$ 1.234.567,50');
    expect(formatarReais(-0.3), r'-R$ 0,30');
  });
}
