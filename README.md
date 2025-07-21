# PyFault: Spectrum-Based Fault Localization for Python

PyFault è un framework Python moderno per la localizzazione automatica di errori tramite Spectrum-Based Fault Localization (SBFL), ispirato a GZoltar. Il framework offre un'interfaccia sia programmatica che da riga di comando per identificare elementi di codice sospetti che potrebbero contenere bug.

## ✨ Caratteristiche Principali

- **🔍 Raccolta Copertura**: Utilizza `coverage.py` con hook personalizzati per raccogliere dati di copertura line e branch
- **📊 Algoritmi SBFL**: Implementazione completa di formule SBFL consolidate (Ochiai, Tarantula, Jaccard, D*, Kulczynski2)
- **🧪 Integrazione Test**: Supporto nativo per pytest con filtri personalizzabili
- **💻 Interfaccia CLI**: Potente CLI basata su `Click` per analisi batch e automazione
- **📱 Dashboard Interattiva**: UI web moderna con Streamlit per visualizzazione e analisi in tempo reale
- **📝 Generazione Report**: Report multipli (HTML, CSV, JSON) con ranking dettagliati e visualizzazioni
- **🎯 Analisi Comparativa**: Confronto simultaneo di multiple formule SBFL per migliori risultati

## 🚀 Installazione

### Requisiti
- Python = 3.12
- pytest ≥ 7.0.0
- coverage ≥ 7.0.0

### Installazione Standard
```bash
# Clona il repository
git clone <repository-url>
cd PyFault

# Installa il package
pip install -e .
```

### Installazione per Sviluppo
```bash
# Installa con dipendenze di sviluppo
pip install -e ".[dev]"

# Verifica installazione
pyfault --help
```

## 💡 Utilizzo

### 🔧 Interfaccia CLI

#### Analisi Completa (Raccomandato)
```bash
# Esecuzione completa: test + fault localization + report
pyfault run --source-dir src --test-dir tests --output-dir results

# Con formule specifiche
pyfault run -s src -t tests -f ochiai -f tarantula -f dstar

# Con filtro test e coverage branch
pyfault run -s src -t tests -k "test_critical" --branch-coverage --top 10
```

#### Solo Fault Localization
```bash
# Analizza dati di copertura esistenti
pyfault fl --coverage-file coverage_matrix.csv --output-dir results

# Con formule multiple
pyfault fl -c coverage_data.csv -f ochiai -f jaccard --top 15
```

#### Raccolta Copertura
```bash
# Solo raccolta dati (senza analisi SBFL)
pyfault test --source-dir src --test-dir tests --output-dir coverage_data
```

#### Dashboard Interattiva
```bash
# Avvia UI con dati esistenti
pyfault ui --data-file results/summary.json --auto-open

# Avvia UI vuota (upload manuale)
pyfault ui --port 8502

# Con dati CSV per analisi real-time
pyfault ui --data-file coverage_matrix.csv
```

### 🐍 API Python

```python
from pyfault import FaultLocalizer
from pyfault.formulas import OchiaiFormula, TarantulaFormula, DStarFormula

# Configurazione base
localizer = FaultLocalizer(
    source_dirs=['src'],
    test_dirs=['tests'],
    formulas=[OchiaiFormula(), TarantulaFormula(), DStarFormula()],
    output_dir='results'
)

# Esegui analisi completa
result = localizer.run()

# Accedi ai risultati
for formula_name, scores in result.scores.items():
    print(f"\n=== {formula_name.upper()} ===")
    for score in scores[:10]:  # Top 10
        element = score.element
        print(f"{element.file_path}:{element.line_number} -> {score.score:.4f}")

# Genera report personalizzati
from pyfault.reporters import HTMLReporter, CSVReporter

html_reporter = HTMLReporter(output_dir='custom_reports')
html_reporter.write_report(result)
```

### 🎯 Esempi Pratici

#### Esempio 1: Progetto Web (FastAPI/Flask)
```bash
# Analisi completa per web app
pyfault run -s app -t tests -f ochiai -f tarantula --branch-coverage --top 15

# Apri dashboard per analisi interattiva
pyfault ui --data-file pyfault_output/summary.json --auto-open
```

#### Esempio 2: Libreria Data Science
```bash
# Focus su test specifici
pyfault run -s src/datalib -t tests -k "test_calculation" -f dstar -f kulczynski2

# Analisi coverage esistente
pyfault fl -c existing_coverage.csv -o analysis_results
```

## 🏗️ Architettura

PyFault segue un'architettura modulare ispirata a GZoltar:

```
src/pyfault/
├── core/                      # 🧠 Logica centrale e modelli
│   ├── fault_localizer.py     # Orchestratore principale
│   └── models.py              # Modelli dati (CoverageMatrix, TestResult, etc.)
├── coverage/                  # 📊 Raccolta copertura del codice
│   └── collector.py           # Integrazione con coverage.py
├── formulas/                  # 🧮 Formule SBFL
│   ├── base.py                # Classe base astratta
│   └── sbfl_formulas.py       # Implementazioni concrete
├── test_runner/               # 🧪 Esecuzione test
│   └── pytest_runner.py       # Runner per pytest
├── reporters/                 # 📝 Generazione report
│   ├── html_reporter.py       # Report HTML interattivi
│   ├── csv_reporter.py        # Export/import CSV
│   └── json_reporter.py       # Serializzazione JSON
├── ui/                        # 🎨 Dashboard web
│   └── dashboard.py           # Interfaccia Streamlit
├── cli/                       # 💻 Interfaccia riga di comando
│   └── main.py                # Comandi CLI con Click
└── benchmarking/              # 📈 Strumenti di benchmark
```

### 🔄 Flusso di Lavoro

1. **Raccolta Copertura**: `CoverageCollector` instrumenta il codice e raccoglie dati durante i test
2. **Esecuzione Test**: `PytestRunner` esegue i test con raccolta copertura
3. **Calcolo SBFL**: Le formule calcolano il punteggio di sospetto per ogni elemento
4. **Generazione Report**: I reporter creano output in vari formati
5. **Visualizzazione**: Dashboard interattiva per analisi approfondita

## 🎨 Dashboard Interattiva

La dashboard web di PyFault offre un'esperienza di analisi moderna e intuitiva:

### ✨ Funzionalità Principali

- **📊 Visualizzazioni Interattive**: 
  - Istogrammi di distribuzione suspiciousness
  - Grafici a barre per top elementi sospetti
  - Treemap per analisi gerarchica dei file
  - Scatter plot per confronto formule

- **🔍 Code Viewer Integrato**: 
  - Evidenziazione sintassi con colori
  - Linee sospette highlight in base al punteggio
  - Navigazione rapida tra file e funzioni

- **📁 Analisi Multi-livello**: 
  - Vista per progetto/package
  - Raggruppamento per file
  - Drill-down su singoli elementi

- **🎛️ Controlli Dinamici**: 
  - Filtri per soglia di punteggio
  - Selezione tipi di file
  - Top-N elementi configurabile
  - Modalità comparison tra formule

### 🚀 Quick Start Dashboard

```bash
# Metodo 1: Analisi completa + UI
pyfault run -s src -t tests && pyfault ui --data-file pyfault_output/summary.json --auto-open

# Metodo 2: Carica dati esistenti
pyfault ui --data-file my_analysis.json --port 8080

# Metodo 3: Analisi real-time da CSV
pyfault ui --data-file coverage_matrix.csv
```

> 📖 **Per esempi dettagliati e screenshot**: Vedi [UI_USAGE.md](UI_USAGE.md)

## 📊 Formule SBFL Supportate

PyFault implementa un set completo di formule SBFL consolidate dalla letteratura:

| Formula | Descrizione | Efficacia | Caso d'Uso |
|---------|-------------|-----------|-------------|
| **Ochiai** | Formula più efficace, basata su coefficiente di correlazione | ⭐⭐⭐⭐⭐ | Raccomandato per la maggior parte dei casi |
| **Tarantula** | Formula classica SBFL, prima ampiamente adottata | ⭐⭐⭐⭐ | Buona baseline, confronti storici |
| **Jaccard** | Coefficiente di similarità Jaccard | ⭐⭐⭐ | Progetti con alta copertura test |
| **D*** | Formula binaria ottimizzata per precisione | ⭐⭐⭐⭐ | Quando è importante minimizzare falsi positivi |
| **Kulczynski2** | Formula di correlazione bilanciata | ⭐⭐⭐ | Analisi comparativa |


## 🛠️ Sviluppo e Contributi

### Setup Ambiente di Sviluppo

```bash
# 1. Clone del repository
git clone <repository-url>
cd PyFault

# 2. Installa dipendenze di sviluppo
pip install -e ".[dev]"

# 3. Setup pre-commit hooks
pre-commit install

# 4. Verifica installazione
pyfault --help
pytest --version
```

### 🧪 Testing

```bash
# Esegui tutti i test
pytest tests/ -v

# Test con coverage
pytest tests/ --cov=src/pyfault --cov-report=html

# Test specifici
pytest tests/test_formulas.py -v
pytest tests/test_integration.py::test_full_pipeline -v
```

### 📏 Quality Assurance

```bash
# Formattazione codice
black src tests examples

# Linting
flake8 src tests examples

# Type checking
mypy src

# Controllo completo
black src tests && flake8 src tests && mypy src && pytest
```

### 🏗️ Struttura del Progetto

```
PyFault/
├── src/pyfault/           # 📦 Codice sorgente principale
├── tests/                 # 🧪 Test suite completa
├── examples/              # 📚 Esempi di utilizzo
│   ├── datalib/           # Esempio progetto creato con LLM
│   └── fastapi/           # Esempio caso reale
├── docs/                  # 📖 Documentazione (se presente)
├── pyproject.toml        # ⚙️ Configurazione progetto
├── dev_setup.txt         # 🔧 Istruzioni setup
└── README.md             # 📝 Questo file
```

### 🤝 Contributing Guidelines

1. **Fork** il repository
2. Crea un **branch feature** (`git checkout -b feature/new-feature`)
3. **Commit** le modifiche (`git commit -m 'Add new feature'`)
4. **Push** al branch (`git push origin feature/new-feature`)
5. Apri una **Pull Request**

### 📋 Checklist per Contributi

- [ ] Test aggiornati/aggiunti per nuove funzionalità
- [ ] Documentazione aggiornata (docstring, README, etc.)
- [ ] Code style conforme (black, flake8)
- [ ] Type hints aggiunti/aggiornati
- [ ] Tutti i test passano (`pytest`)
- [ ] No regressioni nelle performance

## 📈 Esempi e Benchmark

Il progetto include esempi reali per dimostrare le capacità di PyFault:

### 📊 Esempi Disponibili

- **`examples/datalib/`**: Libreria di calcolo con bug intenzionali creata con LLM
- **`examples/fastapi/`**: Framework web complesso (caso reale) - fonte [BugsInPy](https://github.com/soarsmu/BugsInPy)

### 🎯 Esecuzione Esempi

```bash
# Esempio datalib - analisi completa
cd examples/datalib
pyfault run -s src -t tests -f ochiai -f tarantula --auto-open

# Confronto con coverage esistente
pyfault fl -c coverage.xml -o results
pyfault ui --data-file results/summary.json
```

## 🔗 Integrazione con Altri Tool

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Run PyFault Analysis
  run: |
    pip install -e .
    pyfault run -s src -t tests -o fault_analysis
    pyfault ui --data-file fault_analysis/summary.json --port 8501 &
```

## 📚 Risorse e Documentazione

- **📖 Tutorial UI (Ancora in fase di sviluppo)**: Vedi [UI_USAGE.md](UI_USAGE.md)
- **🔬 Paper di Riferimento**: Spectrum-Based Fault Localization literature
- **🏗️ Architettura**: Ispirata a GZoltar e tool SBFL moderni
- **🤝 Community**: Issues GitHub per supporto e feature request

---

<div align="center">

**🔍 Trova i bug più velocemente con PyFault!** 

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](#testing)

</div>
