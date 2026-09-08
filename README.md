# SIR Toscana per Home Assistant

[![GitHub release](https://img.shields.io/github/v/release/m0m4x/ha-sir-toscana?display_name=tag)](https://github.com/m0m4x/ha-sir-toscana/releases)
[![HACS validation](https://github.com/m0m4x/ha-sir-toscana/actions/workflows/validate.yml/badge.svg)](https://github.com/m0m4x/ha-sir-toscana/actions/workflows/validate.yml)
[![hassfest](https://github.com/m0m4x/ha-sir-toscana/actions/workflows/hassfest.yml/badge.svg)](https://github.com/m0m4x/ha-sir-toscana/actions/workflows/hassfest.yml)

Custom integration per Home Assistant per acquisire i **dati in tempo reale della rete meteo-idrologica regionale** pubblicati dal **Servizio Idrologico Regionale (SIR) della Regione Toscana**.

L'integrazione permette di aggiungere una stazione inserendo semplicemente il **nome della stazione**. Il codice `TOS...` viene individuato automaticamente e i valori restituiti dal servizio pubblico SIR vengono esposti come sensori Home Assistant.

> **Progetto indipendente e non ufficiale.** Non è sviluppato, approvato o supportato dalla Regione Toscana o dal SIR.

## Installazione con HACS

Premi il pulsante seguente per aprire direttamente questo repository in HACS:

[![Apri SIR Toscana in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=m0m4x&repository=ha-sir-toscana&category=integration)

Dopo aver scaricato l'integrazione da HACS e riavviato Home Assistant, premi:

[![Aggiungi SIR Toscana a Home Assistant](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=sir_toscana)

Il primo pulsante aggiunge/apre il repository in HACS. Il secondo avvia il Config Flow di **SIR Toscana** dopo che la custom integration è stata installata.

## Funzionalità

- configurazione da interfaccia Home Assistant tramite Config Flow;
- inserimento del nome della stazione, senza necessità di conoscere il codice `TOS...`;
- ricerca case-insensitive e supporto a corrispondenze parziali univoche;
- polling del servizio pubblico SIR ogni 15 minuti, coerente con la cadenza osservata dei dati in tempo reale;
- una sola richiesta HTTP per stazione a ogni ciclo di aggiornamento;
- creazione automatica dei sensori presenti nel JSON della stazione;
- aggiunta dinamica di nuovi sensori se il SIR introduce nuovi campi nel payload;
- un dispositivo Home Assistant distinto per ogni stazione;
- supporto a più stazioni;
- unità e device class Home Assistant per le principali grandezze note;
- mantenimento dei campi sconosciuti con il nome sorgente, evitando interpretazioni arbitrarie;
- nessuna API key richiesta.

## Esempio: La Ferruccia

Configurando:

```text
La Ferruccia
```

l'integrazione individua automaticamente:

```text
TOS01001269
```

e acquisisce i dati da:

```text
https://www.sir.toscana.it/monitoraggio/actions.php?action=station&id=TOS01001269
```

Il payload può contenere sezioni come `anemo`, `pluvio`, `termo`, `igro`, `radio` e altre sezioni dipendenti dalla sensoristica installata nella singola stazione.

Per La Ferruccia vengono quindi creati, tra gli altri:

- velocità del vento in `m/s`;
- direzione del vento in gradi;
- temperatura in `°C`;
- umidità relativa in `%`;
- cumulati pluviometrici in `mm`;
- date di rilevazione;
- ulteriori valori scalari presenti nel payload SIR.

I campi tecnici `id` e `speed_label` non vengono creati come entità.

## Configurazione

L'unico parametro richiesto è il **nome della stazione** come pubblicato nelle tabelle di monitoraggio SIR.

Esempi:

```text
La Ferruccia
Prato Università
Case Passerini
Firenze Università
```

Il confronto non distingue maiuscole e minuscole. Se il testo inserito identifica una sola stazione anche come corrispondenza parziale, la stazione viene accettata. Se il nome è ambiguo, Home Assistant chiede di specificarlo meglio.

## Aggiornamento dei dati

L'integrazione interroga il servizio pubblico SIR ogni **15 minuti** tramite `DataUpdateCoordinator`.

Tutte le entità della stessa stazione utilizzano lo stesso payload, evitando una richiesta separata per ciascun sensore.

## Origine dei dati

Portale del Servizio Idrologico Regionale:

```text
https://www.sir.toscana.it/
```

Tabelle di monitoraggio in tempo reale:

```text
https://www.sir.toscana.it/monitoraggio/stazioni.php
```

Endpoint della singola stazione:

```text
https://www.sir.toscana.it/monitoraggio/actions.php?action=station&id=CODICE_STAZIONE
```

La ricerca delle stazioni utilizza le tabelle pubbliche verificate per anemometria, pluviometria, termometria, igrometria, idrometria e nivometria. Le stazioni mareografiche presenti nella tabella idrometrica sono quindi individuabili attraverso la stessa ricerca.

## Dati in tempo reale e validazione

Il SIR specifica che i dati pubblicati nelle sezioni di monitoraggio sono **acquisiti in tempo reale (ora solare) e non sottoposti a validazione**.

Questi valori non devono quindi essere confusi con eventuali serie storiche successivamente sottoposte a controllo, verifica o validazione dall'ente competente.

L'integrazione mantiene i timestamp nel formato fornito dalla fonte e non attribuisce ai dati un livello di validazione diverso da quello dichiarato dal SIR.

## Sensori dinamici

Il payload JSON viene analizzato senza presupporre che tutte le stazioni dispongano della stessa sensoristica.

Per ogni sezione del JSON della stazione vengono create entità per tutti i valori scalari, ad eccezione dei campi tecnici esclusi esplicitamente (`id` e `speed_label`).

I campi noti ricevono unità, device class e icone Home Assistant appropriate. I campi non ancora documentati dall'integrazione vengono comunque acquisiti con il nome originale restituito dalla fonte, senza inventarne il significato.

> La versione 0.1.1 considera come dati della stazione il payload JSON restituito da `actions.php?action=station`. Le tabelle riepilogative del portale possono mostrare elaborazioni aggiuntive (ad esempio massimi giornalieri o raffiche) che non fanno parte di quel payload e non vengono ancora importate come sensori.

## Installazione manuale

1. Scaricare questo repository.
2. Copiare:

   ```text
   custom_components/sir_toscana
   ```

   dentro:

   ```text
   /config/custom_components/sir_toscana
   ```

3. Riavviare Home Assistant.
4. Aprire **Impostazioni → Dispositivi e servizi → Aggiungi integrazione**.
5. Cercare **SIR Toscana**.
6. Inserire il nome della stazione.

## Limitazioni

- La disponibilità e la correttezza dei dati dipendono dal servizio pubblico SIR Toscana.
- Gli endpoint utilizzati sono servizi web pubblici del portale, ma questo progetto non li presenta come API ufficialmente documentate e stabili.
- Una modifica del portale SIR potrebbe richiedere un aggiornamento dell'integrazione.
- Per i campi non documentati viene volutamente evitata qualsiasi reinterpretazione del significato o dell'unità di misura.
- La consultazione nivometrica può essere stagionale secondo le indicazioni pubblicate dal SIR.

## Condivisione

Una volta pubblicato il repository, per condividere il progetto su WhatsApp è sufficiente inviare:

```text
https://github.com/m0m4x/ha-sir-toscana
```

Il destinatario troverà nel README il pulsante HACS per aggiungere il repository alla propria Home Assistant e il pulsante per avviare la configurazione dell'integrazione.

## Licenza

MIT.

## Disclaimer

I dati appartengono alle rispettive fonti istituzionali. Questa integrazione è esclusivamente un client non ufficiale per visualizzare in Home Assistant informazioni rese pubblicamente disponibili dal Servizio Idrologico Regionale della Regione Toscana.
