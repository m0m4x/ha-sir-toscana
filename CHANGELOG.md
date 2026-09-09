# Changelog

## 0.2.1

- Aggiunto il secondo step del Config Flow per selezionare le tipologie di dati.
- Tutte le tipologie SIR supportate sono selezionabili: `anemo`, `radio`, `pluvio`, `termo`, `igro`, `idro`, `nivo`.
- Le opzioni mostrate dipendono dai blocchi realmente restituiti dalla stazione.
- Tutte le tipologie disponibili sono preselezionate per impostazione predefinita.
- Aggiunta `radio` alla discovery delle stazioni.
- Corretto il parsing della tabella idrometrica, dove il nome della stazione è preceduto dal nome del fiume.
- `radio.value` è esposto come Radianza in `W/m²` con device class `irradiance`.
- Mantenuta la compatibilità con le configurazioni precedenti prive di `data_types`.


## 0.1.1

- Allineato il polling a 15 minuti.
- Aggiornato il Config Flow al tipo `ConfigFlowResult` corrente.
- Associato il `ConfigEntry` al `DataUpdateCoordinator`.
- Aggiunta la device class Home Assistant per la direzione del vento.
- Reso `hacs.json` minimale e conforme alla documentazione corrente.
- Preparazione del repository `m0m4x/ha-sir-toscana` per GitHub e HACS.
- Aggiunti `codeowners`, `integration_type`, `country` e link del progetto.
- Aggiunte le GitHub Actions ufficiali HACS e Hassfest.
- Aggiunti brand locali per Home Assistant 2026.3+.
- Migliorata la ricerca della stazione e la gestione dei nomi con suffissi RADIO/GPRS.
- Aggiunto il supporto alla tabella nivometrica nella ricerca delle stazioni.
- I nuovi campi che compaiono nel payload dopo il setup vengono aggiunti dinamicamente come sensori.
- I valori numerici generici vengono esposti come numeri, quando possibile.
- Evitata la generazione di statistiche long-term scorrette sulla direzione del vento.
- Migliorate tracciabilità e metadati delle entità.

## 0.1.0

- Prima versione dell'integrazione SIR Toscana.
- Config Flow tramite nome della stazione.
- Risoluzione automatica del codice stazione.
- Sensori generati dal payload SIR.
- Polling tramite DataUpdateCoordinator.
