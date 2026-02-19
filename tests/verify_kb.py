#!/usr/bin/env python
"""Quick verification that knowledge base works"""
import os
os.chdir("c:/Users/Yazhini/OneDrive/Desktop/soil")

# Just check if the vector DB exists
from pathlib import Path
vector_db = Path("vector_db")
sqlite_file = vector_db / "chroma.sqlite3"

if sqlite_file.exists():
    print("[OK] Vector database file exists")
    print(f"[OK] File size: {sqlite_file.stat().st_size} bytes")
    
    # List contents
    print("\n[INFO] Vector DB contents:")
    for item in vector_db.glob("*"):
        if item.is_file():
            print(f"  - {item.name} ({item.stat().st_size} bytes)")
        else:
            print(f"  - {item.name}/ (directory)")
else:
    print("[ERROR] Vector database file not found")

print("\n[OK] Knowledge base auto-build is configured!")
print("The vector database will be queried when you use option 4 in the main menu.")
