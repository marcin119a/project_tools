#!/usr/bin/env python3
"""
Prosty skrypt do sprawdzania zawartości bazy danych SQLite
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("sql_app.db")

if not DB_PATH.exists():
    print(f"❌ Baza danych {DB_PATH} nie istnieje!")
    sys.exit(1)

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

# Sprawdź jakie tabele istnieją
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

if not tables:
    print("📭 Baza danych jest pusta - brak tabel")
    conn.close()
    sys.exit(0)

print(f"📊 Znalezione tabele: {[t[0] for t in tables]}\n")

# Sprawdź tabelę location jeśli istnieje
if any("location" in t[0].lower() for t in tables):
    cursor.execute("SELECT * FROM location")
    rows = cursor.fetchall()
    
    # Pobierz nazwy kolumn
    cursor.execute("PRAGMA table_info(location)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"📍 Lokalizacje w bazie ({len(rows)} rekordów):")
    print("=" * 80)
    
    if rows:
        for row in rows:
            print(f"\nID: {row[0]}")
            for i, col_name in enumerate(columns[1:], 1):
                if row[i] is not None:
                    print(f"  {col_name}: {row[i]}")
    else:
        print("  (Brak lokalizacji w bazie)")
    
    print("\n" + "=" * 80)
else:
    print("⚠️  Tabela 'location' nie istnieje w bazie danych")
    print("💡 Uruchom migracje Alembic lub uruchom aplikację (tabele utworzą się automatycznie)")

conn.close()

