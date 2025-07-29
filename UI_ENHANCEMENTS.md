# PyFault Dashboard - Nuove Funzionalità

## Modifiche Implementate

### 1. Supporto per Directory di Input

Il comando `pyfault ui` ora accetta directory invece di singoli file:

```bash
# Prima (solo file JSON)
pyfault ui -d pyfault_output/summary.json

# Ora (intera directory)
pyfault ui -d pyfault_output/
```

### 2. Nuove Visualizzazioni basate sui CSV

La dashboard ora integra tutti i file CSV generati dal CSV reporter:

#### **🧪 Test Analysis Tab**
- **Metriche Overview**: Totale test, test falliti/passati, copertura media
- **Tabella Test Dettagliata**: Con filtri per outcome
- **Analisi Coverage vs Outcome**: Box plot per analizzare la relazione tra copertura e successo dei test
- **Grafici Interattivi**: 
  - Scatter plot elementi coperti vs percentuale di copertura
  - Pie chart distribuzione outcome dei test

#### **📈 Coverage Matrix Tab**
- **Heatmap della Matrice di Copertura**: Visualizzazione completa elementi vs test
- **Statistiche per Elemento**: Top elementi più coperti, distribuzione copertura
- **Statistiche per Test**: Copertura per singolo test, analisi per outcome
- **Grafici di Distribuzione**: Istogrammi e box plot per analisi approfondite

#### **🏆 Formula Comparison Tab**
- **Confronto Top-N**: Tabella side-by-side dei top elementi per ogni formula
- **Analisi di Accordo**: Matrice Jaccard similarity tra formule
- **Distribuzione Punteggi**: Box plot e violin plot per confrontare distribuzioni
- **Statistiche Riassuntive**: Media, deviazione standard, min/max per formula

### 3. File CSV Utilizzati

| File | Contenuto | Nuove Visualizzazioni |
|------|-----------|----------------------|
| `coverage_matrix.csv` | Matrice completa copertura elemento-test | Heatmap, analisi per elemento/test |
| `test_results.csv` | Dettagli per ogni test (outcome, copertura) | Analisi outcome, correlazioni |
| `ranking_*.csv` | Ranking dettagliato per ogni formula | Confronto formule, analisi accordo |

### 4. Informazioni Aggiuntive vs JSON

Le nuove visualizzazioni mostrano dati non disponibili nel `summary.json`:

- **Matrice di copertura completa** (non solo ranking finale)
- **Dettagli individuali dei test** (elementi coperti, percentuali)
- **Confronto diretto tra formule** (accordo, distribuzioni)
- **Analisi statistiche avanzate** (correlazioni, distribuzioni)

### 5. Utilizzo

```bash
# Avvia la dashboard con directory completa
pyfault ui -d examples/ex1/pyfault_output/

# Apre automaticamente il browser
pyfault ui -d examples/ex1/pyfault_output/ --auto-open

# Specifica porta personalizzata
pyfault ui -d examples/ex1/pyfault_output/ -p 8502
```

### 6. Backwards Compatibility

La dashboard mantiene la compatibilità con:
- File JSON singoli (`summary.json`)
- File CSV singoli
- Upload tramite interfaccia web

### 7. Benefici delle Nuove Visualizzazioni

1. **Analisi Test più Approfondita**: Comprensione del comportamento individuale dei test
2. **Visualizzazione Coverage Completa**: Heatmap per identificare pattern di copertura
3. **Confronto Formule Sistematico**: Valutazione comparativa delle performance SBFL
4. **Insight Statistici**: Analisi distribuzionali e correlazioni
5. **Workflow Semplificato**: Un comando per visualizzare tutti i risultati

### 8. Requisiti Tecnici

- Tutti i file CSV devono essere nella stessa directory
- I file devono seguire il formato standard generato dal CSVReporter
- La dashboard carica automaticamente tutti i file disponibili

### 9. Note di Performance

- La heatmap è limitata a 50 elementi per performance di rendering
- I grafici sono ottimizzati per dataset di dimensioni medie
- Cache integrata per migliorare la velocità di caricamento
