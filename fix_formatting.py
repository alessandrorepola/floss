#!/usr/bin/env python3
"""
Script per correggere automaticamente i problemi di formattazione
"""
import subprocess


def run_command(command: str, description: str) -> bool:
    """Esegue un comando e stampa il risultato"""
    print(f"\n🔧 {description}")
    print("=" * 50)

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode == 0:
            print(f"✅ {description} - COMPLETATO")
        else:
            print(f"❌ {description} - ERRORI")

        return result.returncode == 0
    except Exception as e:
        print(f"❌ Errore durante l'esecuzione: {e}")
        return False


def main() -> None:
    """Applica le correzioni automatiche"""
    print("🔧 Avvio correzioni automatiche...")

    # Applica Black
    run_command("black pyfault/", "Applicazione formattazione Black")

    # Applica isort per gli import (se installato)
    try:
        subprocess.run(["isort", "--version"], capture_output=True, check=True)
        run_command("isort pyfault/", "Ordinamento import con isort")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ℹ️  isort non installato, installalo con: pip install isort")

    print("\n" + "=" * 50)
    print("🎉 Correzioni automatiche completate!")
    print("💡 Ora esegui 'python check_quality.py' per verificare i risultati")


if __name__ == "__main__":
    main()
