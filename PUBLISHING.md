# Pubblicazione GitHub e HACS

## Repository GitHub

Nome:

```text
ha-sir-toscana
```

Owner:

```text
m0m4x
```

Descrizione consigliata:

```text
Integrazione Home Assistant per i dati in tempo reale della rete meteo-idrologica regionale del SIR Toscana.
```

Website:

```text
https://www.sir.toscana.it/
```

Topics consigliati:

```text
home-assistant
homeassistant
hacs
italy
toscana
sir-toscana
weather
meteorology
hydrology
```

Abilitare **Issues** nel repository.

Il file `hacs.json` è volutamente minimale e contiene `name` e `country: IT`, sufficienti per questo repository territoriale.

## Primo push

Creare su GitHub un repository pubblico vuoto `m0m4x/ha-sir-toscana`, senza inizializzarlo con README, .gitignore o licenza, quindi dalla cartella locale:

```bash
git init
git add .
git commit -m "Initial release of SIR Toscana integration"
git branch -M main
git remote add origin https://github.com/m0m4x/ha-sir-toscana.git
git push -u origin main
```

## Controlli GitHub

Aprire la scheda **Actions** e verificare che risultino verdi:

- HACS validation
- Validate with hassfest

La validazione HACS controlla anche requisiti del repository che esistono solo dopo la pubblicazione, come Description, Topics e Issues.

## Prima installazione HACS

Usare:

```text
https://my.home-assistant.io/redirect/hacs_repository/?owner=m0m4x&repository=ha-sir-toscana&category=integration
```

oppure aggiungere manualmente il repository a HACS come **Custom repository → Integration**.

Dopo l'installazione riavviare Home Assistant e configurare la prima stazione, ad esempio `La Ferruccia`.

## Prima release

Dopo che le Actions sono verdi e il test reale su Home Assistant ha avuto esito positivo, creare su GitHub una **Release**, non soltanto un tag:

```text
Tag: v0.1.1
Title: SIR Toscana v0.1.1
```

Usare come note il contenuto della sezione `0.1.1` di `CHANGELOG.md`.

HACS usa le vere GitHub Releases per mostrare correttamente le versioni disponibili.

## Catalogo HACS predefinito

L'integrazione può essere usata immediatamente come custom repository. Per chiederne successivamente l'inclusione nel catalogo HACS predefinito:

1. repository GitHub pubblico;
2. HACS Action verde senza `ignore`;
3. Hassfest verde;
4. almeno una GitHub Release;
5. Description, Topics e Issues configurati;
6. `country: IT` in `hacs.json`;
7. brand asset presente;
8. aprire la PR prevista dal progetto `hacs/default` per la categoria `integration`.
