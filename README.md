# SIR Toscana per Home Assistant

[![GitHub release](https://img.shields.io/github/v/release/m0m4x/ha-sir-toscana?display_name=tag)](https://github.com/m0m4x/ha-sir-toscana/releases)
[![HACS validation](https://github.com/m0m4x/ha-sir-toscana/actions/workflows/validate.yml/badge.svg)](https://github.com/m0m4x/ha-sir-toscana/actions/workflows/validate.yml)
[![hassfest](https://github.com/m0m4x/ha-sir-toscana/actions/workflows/hassfest.yml/badge.svg)](https://github.com/m0m4x/ha-sir-toscana/actions/workflows/hassfest.yml)

Custom integration per Home Assistant per acquisire i **dati in tempo reale della rete meteo-idrologica regionale** pubblicati dal **Servizio Idrologico Regionale (SIR) della Regione Toscana**.

L'integrazione acquisisce automaticamente l'elenco delle stazioni disponibili dal portale SIR della Regione Toscana. L'utente seleziona la stazione dal Config Flow e il relativo codice `TOS...` viene memorizzato come identificativo stabile. I valori restituiti dal servizio pubblico SIR vengono quindi esposti come sensori Home Assistant.

> **Progetto indipendente e non ufficiale.** Non è sviluppato, approvato o supportato dalla Regione Toscana o dal SIR.

## Installazione con HACS

Premi il pulsante seguente per aprire direttamente questo repository in HACS:

[![Apri SIR Toscana in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=m0m4x&repository=ha-sir-toscana&category=integration)

Dopo aver scaricato l'integrazione da HACS e riavviato Home Assistant, premi:

[![Aggiungi SIR Toscana a Home Assistant](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=sir_toscana)

Il primo pulsante aggiunge/apre il repository in HACS. Il secondo avvia il Config Flow di **SIR Toscana** dopo che la custom integration è stata installata.

## Funzionalità

- configurazione da interfaccia Home Assistant tramite Config Flow;
- selezione delle tipologie di dati disponibili per ciascuna stazione;
- elenco delle stazioni acquisito automaticamente dal portale SIR;
- selezione della stazione tramite menu Home Assistant;
- nessuna necessità di conoscere o digitare il codice `TOS...`;
- polling del servizio pubblico SIR ogni 15 minuti;
- una sola richiesta HTTP per stazione a ogni ciclo di aggiornamento;
- creazione automatica dei sensori presenti nel JSON della stazione;
- aggiunta dinamica di nuovi sensori se il SIR introduce nuovi campi nel payload;
- un dispositivo Home Assistant distinto per ogni stazione;
- supporto a più stazioni;
- nomi, unità e device class Home Assistant per le principali grandezze note;
- nessuna API key richiesta.

## Esempio: Prato Università

Nel Config Flow è possibile selezionare:

```text
Prato Università — TOS01001205
```

L'integrazione acquisisce i dati da:

```text
https://www.sir.toscana.it/monitoraggio/actions.php?action=station&id=TOS01001205
```

La stazione Prato Università è presente nelle tabelle di monitoraggio SIR per più grandezze meteorologiche.

## Nomi dei sensori

I nomi delle entità seguono il più possibile la terminologia utilizzata nelle visualizzazioni del portale SIR.

Esempi:

```text
Velocità vento
Direzione vento
Temperatura
Umidità aria
Radiazione diretta
Precipitazioni cumulate 15 minuti
Precipitazioni cumulate 1 ora
Precipitazioni cumulate 3 ore
Precipitazioni cumulate 6 ore
Precipitazioni cumulate 12 ore
Precipitazioni cumulate 24 ore
Precipitazioni cumulate 36 ore
Tempo di ritorno precipitazione 1 ora
Precipitazioni step 00–03 (24 h)
```

I timestamp vengono esposti come entità diagnostiche, ad esempio:

```text
Data rilevazione vento
Data rilevazione temperatura
Data rilevazione umidità aria
Data rilevazione precipitazioni
```

I campi tecnici `id` e `speed_label` non vengono creati come entità.

## Configurazione

1. Aprire **Impostazioni → Dispositivi e servizi → Aggiungi integrazione**.
2. Cercare **SIR Toscana**.
3. Selezionare la stazione desiderata dall'elenco.

Ogni voce mostra il nome pubblicato dal SIR e il relativo codice identificativo:

```text
Prato Università — TOS01001205
```

![Selezione della stazione SIR Toscana](docs/images/config-flow-station.jpg)

Il codice viene salvato internamente come identificativo stabile della stazione, mentre il nome pubblicato dal SIR viene utilizzato come nome del dispositivo Home Assistant.

### Selezione delle tipologie di dati

Dopo la scelta della stazione, il Config Flow interroga il relativo endpoint SIR e propone **tutte le macro-tipologie supportate effettivamente presenti nel payload**.

![Selezione delle tipologie di dati SIR](docs/images/config-flow-data-types.jpg)

Le tipologie gestite sono:

- `anemo` — Anemometria / vento;
- `radio` — Radiometria / radianza, in `W/m²`;
- `pluvio` — Pluviometria / precipitazioni;
- `termo` — Termometria / temperatura;
- `igro` — Igrometria / umidità relativa;
- `idro` — Idrometria / livelli e portate;
- `nivo` — Nivometria / neve.

Tutte le tipologie disponibili sono preselezionate; l'utente può deselezionare quelle che non desidera esporre in Home Assistant.

La richiesta HTTP al SIR continua a restituire l'intero payload della stazione. La selezione determina quali sezioni vengono trasformate in entità Home Assistant.

Le configurazioni create con versioni precedenti, prive del campo `data_types`, mantengono il comportamento precedente ed espongono tutte le sezioni restituite dal SIR.

### Dispositivo e sensori

Al termine della configurazione Home Assistant crea un dispositivo distinto per la stazione, con i sensori relativi alle tipologie selezionate e le entità diagnostiche disponibili.

![Esempio del dispositivo SIR Toscana in Home Assistant](docs/images/device-overview.jpg)

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

La ricerca delle stazioni utilizza le tabelle pubbliche verificate per anemometria, pluviometria, termometria, igrometria, idrometria e nivometria.

## Dati in tempo reale e validazione

Il SIR specifica che i dati pubblicati nelle sezioni di monitoraggio sono **acquisiti in tempo reale (ora solare) e non sottoposti a validazione**.

Questi valori non devono quindi essere confusi con eventuali serie storiche successivamente sottoposte a controllo, verifica o validazione dall'ente competente.

L'integrazione mantiene i timestamp nel formato fornito dalla fonte e non attribuisce ai dati un livello di validazione diverso da quello dichiarato dal SIR.

## Sensori dinamici

Il payload JSON viene analizzato senza presupporre che tutte le stazioni dispongano della stessa sensoristica.

Per ogni sezione del JSON della stazione vengono create entità per tutti i valori scalari, ad eccezione dei campi tecnici esclusi esplicitamente (`id` e `speed_label`).

I campi noti ricevono nomi leggibili, unità, device class e icone Home Assistant appropriate. I campi non ancora documentati vengono comunque acquisiti con un nome derivato dalla sezione e dal campo sorgente.

> La versione 0.1.1 considera come dati della stazione il payload JSON restituito da `actions.php?action=station`. Le tabelle riepilogative del portale possono mostrare elaborazioni aggiuntive, come massimi giornalieri o raffiche, che non fanno parte di quel payload e non vengono ancora importate come sensori.

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
6. Selezionare la stazione desiderata.

## Limitazioni

- La disponibilità e la correttezza dei dati dipendono dal servizio pubblico SIR Toscana.
- Gli endpoint utilizzati sono servizi web pubblici del portale, ma questo progetto non li presenta come API ufficialmente documentate e stabili.
- Una modifica del portale SIR potrebbe richiedere un aggiornamento dell'integrazione.
- Per i campi non documentati viene volutamente evitata qualsiasi reinterpretazione del significato o dell'unità di misura.
- La consultazione nivometrica può essere stagionale secondo le indicazioni pubblicate dal SIR.

## Licenza

MIT.

## Disclaimer

I dati appartengono alle rispettive fonti istituzionali. Questa integrazione è esclusivamente un client non ufficiale per visualizzare in Home Assistant informazioni rese pubblicamente disponibili dal Servizio Idrologico Regionale della Regione Toscana.
