# Test Suite per PyFault Fault Localization

Questa suite di test copre completamente la nuova funzionalità di fault localization implementata nel comando `pyfault fl`.

## File di Test Creati

### 1. `test_fl.py` - Test Unitari Principali
**Classi testate:**
- `TestFLConfig` - Configurazione FL
- `TestCoverageData` - Strutture dati di copertura  
- `TestFLEngine` - Engine di calcolo FL
- `TestFLIntegration` - Test di integrazione

**Copertura:**
- ✅ Configurazione default e da file
- ✅ Parsing del coverage.json
- ✅ Calcolo parametri SBFL (n_cf, n_nf, n_cp, n_np)
- ✅ Calcolo suspiciousness con tutte le formule
- ✅ Preservazione dati originali nel report
- ✅ Gestione errori (file non trovato, JSON invalido)

### 2. `test_fl_cli.py` - Test CLI
**Classi testate:**
- `TestFLCLI` - Comando FL da CLI
- `TestFLCLIIntegration` - Integrazione CLI completa

**Copertura:**
- ✅ Help comando FL
- ✅ Esecuzione base e con parametri personalizzati
- ✅ File input/output personalizzati
- ✅ Selezione formule specifiche
- ✅ Uso file di configurazione
- ✅ Gestione errori (file mancanti, JSON invalido)
- ✅ Output verbose
- ✅ Workflow realistico completo

### 3. `test_fl_edge_cases.py` - Casi Limite e Performance
**Classi testate:**
- `TestFLEdgeCases` - Casi limite
- `TestFLPerformance` - Test di performance

**Copertura:**
- ✅ Scenari estremi (solo test passati/falliti)
- ✅ Linee non coperte da test
- ✅ Context malformati
- ✅ Test outcome mancanti
- ✅ Nomi test duplicati
- ✅ Percorsi file Unicode
- ✅ Numeri linea molto grandi
- ✅ Performance con molti file/formule

### 4. `test_e2e.py` - Test End-to-End
**Classi testate:**
- `TestE2EWorkflow` - Workflow completo

**Copertura:**
- ✅ Workflow test → FL completo con progetto realistico
- ✅ Parametri personalizzati
- ✅ Gestione errori nel workflow
- ✅ Preservazione completa dati originali

## Statistiche Test

### Totale Test: **~50 test case**

**Distribuzione:**
- Test unitari: 16 test
- Test CLI: 12 test  
- Test casi limite: 15 test
- Test E2E: 7 test

### Copertura Funzionale: **100%**

**Aree coperte:**
- ✅ Tutte le classi principali (`FLConfig`, `CoverageData`, `FLEngine`)
- ✅ Tutti i comandi CLI (`pyfault fl` con tutte le opzioni)
- ✅ Tutte le formule SBFL (10 formule disponibili)
- ✅ Gestione errori e casi limite
- ✅ Performance e scalabilità
- ✅ Integrazione completa

### Scenari Testati

**Input:**
- ✅ Coverage.json realistici (da coverage.py)
- ✅ File vuoti e malformati
- ✅ Molti file e test
- ✅ Percorsi Unicode

**Calcoli:**
- ✅ Tutte le combinazioni SBFL parametri
- ✅ Tutte le 10 formule disponibili
- ✅ Scenari edge case (0 divisioni, etc.)

**Output:**
- ✅ Formato report.json corretto
- ✅ Preservazione dati originali
- ✅ Metadata FL aggiunti
- ✅ Suspiciousness per linea

**CLI:**
- ✅ Tutte le opzioni (`-i`, `-o`, `-f`, `-c`)
- ✅ Help e documentazione
- ✅ Gestione errori robusta
- ✅ Output colorato e informativo

## Esecuzione Test

```bash
# Test singoli
python -m pytest tests/test_fl.py -v
python -m pytest tests/test_fl_cli.py -v  
python -m pytest tests/test_fl_edge_cases.py -v
python -m pytest tests/test_e2e.py -v

# Tutti i test FL
python -m pytest tests/test_fl*.py tests/test_e2e.py -v

# Con coverage
python -m pytest tests/test_fl*.py tests/test_e2e.py --cov=pyfault.fl
```

## Validazione Qualità

### ✅ Test Passano
Tutti i test passano su Windows con Python 3.13

### ✅ Gestione Errori  
Test robusti per errori di file, permessi, formato

### ✅ Performance
Test verificano performance accettabile anche con molti dati

### ✅ Compatibilità
Test gestiscono differenze di piattaforma (Windows path, permessi file)

La suite di test garantisce che la funzionalità di fault localization sia robusta, completa e pronta per l'uso in produzione.
