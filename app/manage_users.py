"""Trusted local account administration: python -m app.manage_users EMAIL --role admin."""
import argparse
from app.services.db_service import get_connection, init_db


def main():
    parser = argparse.ArgumentParser(description="Set the role of an existing registered account")
    parser.add_argument("email")
    parser.add_argument("--role", choices=["user", "admin"], required=True)
    args = parser.parse_args()
    init_db()
    with get_connection() as conn:
        result = conn.execute("UPDATE users SET role = ? WHERE email = ?", (args.role, args.email.strip().lower()))
        if result.rowcount == 0:
            parser.error("Account not found; register it first")
    print("Account role updated")


if __name__ == "__main__":
    main()
