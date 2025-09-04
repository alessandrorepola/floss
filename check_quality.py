#!/usr/bin/env python3
"""
Script per eseguire tutti i controlli di qualità del codice (Black, Flake8, MyPy)
"""
import subprocess
import sys


def run_command(command: str, description: str) -> bool:
    """Esegue un comando e stampa il risultato"""
    print(f"\n🔍 {description}")
    print("=" * 50)

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode == 0:
            print(f"✅ {description} - OK")
        else:
            print(f"❌ {description} - ERRORI TROVATI")

        return result.returncode == 0
    except Exception as e:
        print(f"❌ Errore durante l'esecuzione: {e}")
        return False


def main() -> None:
    """Esegue tutti i controlli di qualità"""
    print("🚀 Avvio controlli di qualità del codice...")

    checks = [
        ("black --check --diff pyfault/", "Controllo formattazione con Black"),
        ("flake8 pyfault/", "Controllo stile con Flake8"),
        ("mypy pyfault/", "Controllo tipi con MyPy"),
    ]

    all_passed = True

    for command, description in checks:
        passed = run_command(command, description)
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Tutti i controlli sono passati!")
        sys.exit(0)
    else:
        print("⚠️  Alcuni controlli hanno fallito. Vedi sopra per i dettagli.")
        sys.exit(1)


if __name__ == "__main__":
    main()
