# PyFault Fault Localization Command

Il comando `pyfault fl` calcola i punteggi di suspiciousness per la fault localization a partire da un file coverage.json generato dal comando `pyfault test`.

## Utilizzo

```bash
# Utilizzo base - usa configurazione da pyfault.conf
pyfault fl

# Specifica file di input e output
pyfault fl -i coverage.json -o report.json

# Usa formule specifiche
pyfault fl -f ochiai -f tarantula -f dstar2

# Con file di configurazione personalizzato
pyfault fl -c my_config.conf
```

## Configurazione

Nel file `pyfault.conf`, aggiungere la sezione `[fl]`:

```ini
[fl]
input_file = coverage.json
output_file = report.json
formulas = ochiai, tarantula, jaccard, dstar2
```

## Formule Disponibili

- `ochiai` - Formula di Ochiai (molto efficace)
- `tarantula` - Formula di Tarantula (classica)
- `jaccard` - Coefficiente di Jaccard
- `dstar2` - D* con esponente 2 
- `dstar3` - D* con esponente 3
- `kulczynski2` - Formula di Kulczynski2
- `naish1` - Formula di Naish1
- `russellrao` - Russell-Rao
- `sorensendice` - Sorensen-Dice
- `sbi` - Similarity-Based Index

## Output

Il comando genera un file `report.json` che estende il file `coverage.json` originale aggiungendo:

1. **Sezione `suspiciousness`** per ogni file con punteggi per ogni linea coperta
2. **Metadata `fl_metadata`** con informazioni sulle formule usate

Esempio di output:
```json
{
  "files": {
    "src/example.py": {
      "suspiciousness": {
        "5": {
          "ochiai": 0.5,
          "tarantula": 0.5,
          "jaccard": 0.33
        }
      }
    }
  },
  "fl_metadata": {
    "formulas_used": ["ochiai", "tarantula", "jaccard"],
    "total_lines_analyzed": 10
  }
}
```

## Workflow Completo

```bash
# 1. Esegui test con raccolta copertura
pyfault test

# 2. Calcola fault localization
pyfault fl

# 3. Il file report.json contiene i risultati
```
