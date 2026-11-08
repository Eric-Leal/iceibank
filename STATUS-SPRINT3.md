# Status do Sprint 3

Passagem para continuar de outro PC. Roteiro completo em [`ROTEIRO-SPRINT3.md`](ROTEIRO-SPRINT3.md).

## Resumo

Todo o código do sprint está pronto, testado e no GitHub. Faltam os prints, revisar as respostas e checar a regressão dos sprints anteriores.

| Parte | O que é | Status | Commit |
|---|---|---|---|
| A | Bully: eleição e coordenador | ✅ | `5a6c773` |
| B | Heartbeat e failover automático | ✅ | `dc2a07c` |
| C | `historico_lideranca.py` | ✅ | `702fe17` |
| Extra | Redesign do frontend web (verde, estilo Mercado Pago) | ✅ | `bed1299` |
| D | App Flutter: fluxo bancário + painel da líder | ✅ | `d38c8f6` |
| E | `POST /contas/{id}/sincronizar` com 409 por vetor | ✅ | `d319be3` |
| F | App offline-first (SQLite, fila, sync automático, 409) | ✅ | `2436f84` |
| 2.1 | Funcionalidade adicional: indicador de agências ativas | ✅ código, ⬜ print | junto da D |
| 4.2 | 8 prints + print da funcionalidade adicional | ⬜ | - |
| 12 | `RESPOSTAS-SPRINT3.md` | 📝 rascunho, revisar | - |
| 12 | Regressão (JWT, frontend web, mensageria) | ⬜ | - |

## Onde está cada coisa

**Backend (`agencia/`)**
- `src/services/bully_service.py`: eleição, coordenador, heartbeat de 3s, timeout de 1s (`httpx` assíncrono).
- `src/controllers/bullyController.py`: `POST /bully/eleicao`, `POST /bully/coordenador`, `GET /bully/lider`.
- `src/main.py`: abre a eleição e liga o heartbeat no `lifespan`.
- `historico_lideranca.py`: linha do tempo de líderes a partir dos logs em `data/`.
- `src/services/comparar_vetores.py`: comparação de vetores (`python src/services/comparar_vetores.py` roda os asserts).
- `src/services/contas_service.py`: método `sincronizar`, que levanta `ConflitoSincronizacao` quando o vetor é diferente.
- `src/controllers/contasController.py`: rota `/contas/{id}/sincronizar`; saldo, depósito e saque devolvem `vetorAtual`.

**Frontend web (`frontend/`)**
- Visual novo em `App.vue`, `views/*.vue` e `assets/main.css` (tema `marca-*`, classe `campo`).
- `components/PainelLideranca.vue`: líder atual e agências online, consulta a cada 3s.
- `stores/atividades.ts`: últimas atividades da sessão (o backend não tem extrato).

**App (`app_mobile/lib/`)**
- `config.dart`: agências em `10.0.2.2:8081-8083`, o localhost do PC visto do emulador.
- `api.dart`: chamadas REST e `ErroApi` (com `offline` para falta de conexão e `status`/`corpo` para o 409).
- `sessao.dart`: token JWT no `shared_preferences`.
- `dados/banco_local.dart`: SQLite com as tabelas `contas` e `pendentes`.
- `dados/sincronizador.dart`: fila, saldo provisório, sincronização ao reconectar e a cada 10s, Descartar/Reenviar.
- `telas/`: login, início e transferência. `widgets/painel_lideranca.dart`: painel da líder.

## Preparar o outro PC

1. **Flutter.** Clonar o SDK fora de caminho com acento:

   ```powershell
   git clone https://github.com/flutter/flutter.git -b stable --depth 1 C:\src\flutter
   ```

   Pôr `C:\src\flutter\bin` no PATH.
2. **JDK 17** (Java novo demais quebra o Gradle):

   ```powershell
   winget install Microsoft.OpenJDK.17
   ```

   Depois apontar o Flutter pra ele:

   ```powershell
   flutter config --jdk-dir "C:\Program Files\Microsoft\jdk-17..."
   ```
3. **Android SDK.** Pelo Android Studio, ou pelo cmdline-tools em `%LOCALAPPDATA%\Android\Sdk`. Pacotes: `platform-tools`, `emulator`, `platforms;android-36`, `build-tools;36.0.0`, `build-tools;28.0.3` e `system-images;android-35;google_apis;x86_64`. Licenças: `yes | sdkmanager --licenses` (pelo Git Bash; pelo PowerShell o pipe não funciona).
4. **AVD:**

   ```powershell
   avdmanager create avd -n iceibank -k "system-images;android-35;google_apis;x86_64" -d pixel_7
   ```
5. **Conferir:** `flutter doctor` tem que ficar todo verde, menos o Visual Studio, que só serve pra app Windows.

**Se o repositório estiver num caminho com acento** (ex.: "Área de Trabalho"), o `flutter analyze` e o Gradle quebram. Mapeie num drive com `subst I: "<caminho do repo>"` e rode o Flutter de `I:\app_mobile`. O `kotlin.incremental=false` no `android/gradle.properties` já está commitado por causa disso.

## Rodar tudo

1. **Agências.** Um terminal por agência, dentro de `agencia/`, com o `.env` do CloudAMQP presente:

   ```powershell
   $env:AGENCIA_ID=0; .\.venv\Scripts\python.exe src\main.py
   ```

   Repetir com `1` e `2`. Se o venv não existir: `python -m venv .venv` e `.\.venv\Scripts\pip install -r requirements.txt`.
2. **Frontend:**

   ```powershell
   npm --prefix frontend install
   ```

   ```powershell
   npm --prefix frontend run dev
   ```

   Abre em `http://localhost:5173`.
3. **App:**

   ```powershell
   emulator -avd iceibank
   ```

   Depois, em `app_mobile`: `flutter pub get` e `flutter run`.
4. **Conta de teste.** As contas ficam em memória e somem quando a agência reinicia. Os comandos para recriar estão em [`evidencias/sprint3/README.md`](evidencias/sprint3/README.md).

## O que falta (em ordem)

1. **Prints.** A lista dos 9 e como reproduzir cada cenário está em [`evidencias/sprint3/README.md`](evidencias/sprint3/README.md). Os nomes de arquivo já são os referenciados no `RESPOSTAS-SPRINT3.md`.
2. **Revisar `RESPOSTAS-SPRINT3.md`.** O rascunho usa o que observamos nos testes. Confira se os números batem com os seus prints, ajuste o texto pra conseguir defender cada resposta e complete a seção "Uso de IA" se precisar.
3. **Regressão.** Login JWT pelo frontend web, depósito e saque, transferência local e entre agências (RabbitMQ), e o `scripts/testar_mensageria.py`. Testar também a transferência pelo app, que ainda não foi testada.
4. **Commit e push** dos prints e das respostas.

## Observações dos testes

- **Tempestade de eleições:** na subida, a agência 2 declarou `TORNOU_LIDER` 3 vezes em menos de 1s. É esperado e responde a pergunta 7.3.
- **Tempo de failover:** a nova líder apareceu em menos de 8s.
- **Conflitos falsos:** o vetor da agência avança com mensagens do Bully, então uma reeleição sozinha já gera 409 numa sincronização offline. É a simplificação da pergunta 9.6.2.
- **Liderança invertida:** o `receber_coordenador` aceita qualquer `liderId` sem comparar IDs. Se a rede ficar lenta, a líder pode acabar sendo a agência 1 com a 2 viva (pergunta 6.4.3).
- **Teste do offline (10.2):** passou de ponta a ponta. Depósito offline, sync automático ao sair do modo avião, conflito 409 visível e persistido depois de reabrir o app, "Reenviar" aplicando.
