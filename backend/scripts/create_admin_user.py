#!/usr/bin/env python3
"""
Script para crear un usuario Admin en la base de datos local usando el CRUD del proyecto.

Uso:
  export DATABASE_URL="..."
  python3 backend/scripts/create_admin_user.py --email admin@admin --password admin1234

Nota: Este script usa directamente los modelos/CRUD del proyecto, así que ejecutarlo
desde la raíz del repo (o ajustar PYTHONPATH) para que las importaciones funcionen.
"""
import argparse
import os
import sys

# Asegurarse de que el path de la app esté en PYTHONPATH
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.database import SessionLocal
from app.crud import user_crud
from app.utils.schemas import UserCreate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--name', default='Admin')
    args = parser.parse_args()

    db = SessionLocal()
    try:
        existing = user_crud.get_user_by_email(db, args.email)
        if existing:
            print(f"Usuario con email {args.email} ya existe. id={existing.id}")
            return

        user_in = UserCreate(email=args.email, name=args.name, password=args.password, role='Admin')
        user = user_crud.create_user(db, user_in)
        print(f"Admin creado: id={user.id} email={user.email}")
    except Exception as e:
        print("Error creando admin:", e)
    finally:
        db.close()


if __name__ == '__main__':
    main()
