# backend.py

import sqlite3

class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS expense_manager (person_name TEXT, amount_paid INT, edate TEXT)"
        )
        self.conn.commit()

    def fetchRecord(self, query):
        self.cur.execute(query)
        rows = self.cur.fetchall()
        return rows

    def insertRecord(self, person_name, amount_paid, edate):
        self.cur.execute("INSERT INTO expense_manager VALUES (?, ?, ?)",
                         (person_name, amount_paid, edate))
        self.conn.commit()

    def removeRecord(self, rowid):
        self.cur.execute("DELETE FROM expense_manager WHERE rowid=?", (rowid,))
        self.conn.commit()

    def updateRecord(self, person_name, amount_paid, edate, rowid):
        self.cur.execute("UPDATE expense_manager SET person_name = ?, amount_paid = ?, edate = ? WHERE rowid = ?",
                         (person_name, amount_paid, edate, rowid))
        self.conn.commit()

    def __del__(self):
        self.conn.close()
