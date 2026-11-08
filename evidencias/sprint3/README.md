# Evidências - Sprint 3

Prints exigidos pela seção 4.2 do roteiro. Todos com `Get-Date` visível em algum terminal.

| Arquivo | O que mostrar | Status |
|---|---|---|
| `eleicao-inicial.png` | As 3 agências no ar e `/bully/lider` nas 3 respondendo `liderAtual: 2` | ⬜ |
| `failover.png` | Agência 2 derrubada e, segundos depois, `/bully/lider` nas agências 0 e 1 respondendo `liderAtual: 1` | ⬜ |
| `historico-lideranca.png` | Saída de `python historico_lideranca.py` com líder inicial -> queda -> nova líder | ⬜ |
| `app-lider-atual.png` | App no emulador com o painel "Líder atual: Agência 2" e as 3 online | ⬜ |
| `app-failover.png` | Mesmo painel depois de derrubar a agência 2: "Agência 1" e a 2 "Fora do ar" (antes/depois) | ⬜ |
| `conflito-sincronizacao.png` | Resposta 409 do `/contas/3/sincronizar` com `vetorConhecido`, `vetorAtual` e `contaAtual` | ⬜ |
| `app-offline.png` | App em modo avião com "Saldo provisório", selo "pendente" e o depósito em "Aguardando sincronização" | ⬜ |
| `app-sincronizacao.png` | App depois de reconectar, sem tocar em nada: saldo confirmado e fila vazia | ⬜ |
| `funcionalidade-adicional.png` | Indicador de agências ativas (web ou app) com uma agência "Fora do ar" | ⬜ |

## Como reproduzir cada cenário

Subir as 3 agências, uma por terminal, dentro de `agencia/`:

```powershell
$env:AGENCIA_ID=0; .\.venv\Scripts\python.exe src\main.py
```

(repetir com `1` e `2`). Consultar a líder:

```powershell
Get-Date; 8081..8083 | % { Invoke-RestMethod "http://localhost:$_/bully/lider" }
```

Criar a conta de teste (contas ficam em memória, recriar a cada reinício):

```powershell
$op = (Invoke-RestMethod -Method Post http://localhost:8081/auth/login-operador -ContentType 'application/json' -Body '{"usuario":"operador","senha":"iceibank123"}').token
Invoke-RestMethod -Method Post http://localhost:8081/contas -Headers @{Authorization="Bearer $op"} -ContentType 'application/json' -Body '{"id":3,"nomeAluno":"Eric Leal","senha":"teste123","saldoInicial":1500}'
```

Conflito de sincronização (seção 9.5):

```powershell
$t = (Invoke-RestMethod -Method Post http://localhost:8081/auth/login -ContentType 'application/json' -Body '{"id":3,"senha":"teste123"}').token
$h = @{Authorization="Bearer $t"}
$antigo = (Invoke-RestMethod http://localhost:8081/contas/3 -Headers $h).vetorAtual
Invoke-RestMethod -Method Post http://localhost:8081/contas/3/depositar -Headers $h -ContentType 'application/json' -Body '{"valor":100}'
$corpo = @{tipo='DEPOSITO'; valor=50; vetorConhecido=$antigo} | ConvertTo-Json -Compress
Get-Date; try { Invoke-RestMethod -Method Post http://localhost:8081/contas/3/sincronizar -Headers $h -ContentType 'application/json' -Body $corpo } catch { $_.ErrorDetails.Message }
```

Modo avião no emulador:

```powershell
adb shell cmd connectivity airplane-mode enable
adb shell cmd connectivity airplane-mode disable
```
