import pymysql.cursors
import sqlite3


class Db:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)

    @staticmethod
    def close():
        pass

    def do_query(self, query, args=''):
        with self.conn:
            c = self.conn.cursor()
            if args:
                c.execute(query, args)
            else:
                c.execute(query)
        a = c.fetchall()
        return a

    def do_insert(self, query, args):
        # backawrds compatible
        self.do_query(query, args)

    def do_insertmany(self, query, args):
        with self.conn:
            c = self.conn.cursor()
            c.executemany(query, args)