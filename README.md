# PyFault: Spectrum-Based Fault Localization for Python

PyFault è un framework Python per la localizzazione automatica di errori tramite Spectrum-Based Fault Localization (SBFL), ispirato a GZoltar.

## Features

- **Coverage Collection**: Raccolta automatica della copertura del codice durante l'esecuzione dei test
- **SBFL Algorithms**: Implementazione di formule SBFL popolari (Ochiai, Tarantula, Jaccard, D*, Barinel, etc.)
- **Test Integration**: Integrazione con pytest e altri framework di testing
- **CLI Interface**: Interfaccia a riga di comando per esecuzione batch
- **Interactive UI**: Dashboard web interattiva con Streamlit per visualizzazione e analisi
- **Report Generation**: Generazione di report HTML, CSV e JSON con ranking dei sospetti
- **Visualization**: Visualizzazioni interattive per analisi dei risultati

## Installazione

```bash
pip install -e .
```

## Utilizzo Rapido

### Via CLI

```bash
# Esecuzione completa: instrumentazione, test e fault localization
pyfault run --source-dir src --test-dir tests --output-dir results

# Solo fault localization su dati esistenti
pyfault fl --coverage-file coverage.json --test-results tests.json

# 🆕 Dashboard interattiva per visualizzazione e analisi in tempo reale
pyfault ui --data-file results/summary.json --auto-open
```

### Via Python API

```python
from pyfault import FaultLocalizer
from pyfault.formulas import OchiaiFormula

# Inizializza il localizzatore
localizer = FaultLocalizer(
    source_dirs=['src'],
    test_dirs=['tests'],
    formulas=[OchiaiFormula(), TarantulaFormula()]
)

# Esegui fault localization
results = localizer.run()

# Visualizza i risultati
for element, score in results.get_ranking('ochiai')[:10]:
    print(f"{element}: {score:.4f}")
```

## Architettura

```
pyfault/
├── core/           # Logica centrale
├── coverage/       # Raccolta copertura
├── formulas/       # Formule SBFL
├── test_runner/    # Esecuzione test
├── reporters/      # Generazione report
├── ui/            # Dashboard web interattiva
└── cli/           # Interfaccia CLI
```

## 🖥️ Dashboard Interattiva

La nuova UI web fornisce un'esperienza di analisi moderna e intuitiva:

- **📊 Visualizzazioni Interactive**: Grafici di distribuzione, classifiche, treemap
- **🔍 Viewer del Codice Sorgente**: Linee sospette evidenziate con colori
- **📁 Analisi per File**: Raggruppamento degli elementi sospetti per file
- **🎛️ Filtri Dinamici**: Soglie di punteggio, tipi di file, top-N elementi
- **📈 Confronto Formule**: Analisi comparativa di diverse formule SBFL

### Esempio di utilizzo

```bash
# Esegui analisi e apri dashboard
pyfault run -s src -t tests && pyfault ui --data-file pyfault_output/summary.json

# Carica dati esistenti
pyfault ui --data-file my_results.json --port 8080 --auto-open
```

Vedi [UI_USAGE.md](UI_USAGE.md) per esempi dettagliati.

## Formule SBFL Supportate

- **Ochiai**: Formula più efficace per fault localization
- **Tarantula**: Formula classica SBFL
- **Jaccard**: Coefficiente di similarità
- **D\***: Formula binaria ottimizzata
- **Barinel**: Formula probabilistica
- **Kulczynski2**: Formula di correlazione
- **SBI**: Similarity-Based Index

## Sviluppo

```bash
# Installa dipendenze di sviluppo
pip install -e ".[dev]"

# Esegui test
pytest

# Formattazione codice
black src tests
flake8 src tests

# Type checking
mypy src
```

## Licenza

MIT License
