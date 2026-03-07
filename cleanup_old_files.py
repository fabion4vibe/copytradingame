"""
cleanup_old_files.py
--------------------
Rimuove i file TASK_*.md dalla radice del progetto dopo la riorganizzazione
in tasks/. Esegui questo script UNA SOLA VOLTA dopo aver verificato che
tasks/ contenga tutti i file corretti.

Uso:
    python cleanup_old_files.py
"""

import os
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.join(ROOT, "tasks")

old_files = glob.glob(os.path.join(ROOT, "TASK_*.md"))

if not old_files:
    print("Nessun file TASK_*.md trovato nella radice. Nulla da fare.")
    exit(0)

print(f"File da rimuovere dalla radice ({len(old_files)}):")
for f in sorted(old_files):
    print(f"  {os.path.basename(f)}")

confirm = input("\nConfermi la rimozione? [s/N] ").strip().lower()
if confirm != "s":
    print("Annullato.")
    exit(0)

for f in old_files:
    # Safety check: verify the file exists in tasks/ before deleting
    name = os.path.basename(f)
    tasks_copy = os.path.join(TASKS_DIR, name)
    if not os.path.exists(tasks_copy):
        print(f"  SKIP: {name} non trovato in tasks/ — non eliminato per sicurezza.")
        continue
    os.remove(f)
    print(f"  Rimosso: {name}")

print("\nDone.")
