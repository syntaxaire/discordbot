import pymysql.cursors
from config import *


class db:
    def __init__(self):
        pass

    def build(self):
        self.connection = pymysql.connect(host='fartcannon.com', user=db_secrets[0], password=db_secrets[1],
                                          db=db_secrets[2], charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    def do_query(self, query, args=''):
        self.build()
        try:
            with self.connection.cursor() as cursor:
                # Read a single record
                if args:
                    cursor.execute(query, args)
                else:
                    cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
        finally:
            pass
        return (result)

    def do_insert(self, query, args):
        self.build()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, args)
                self.connection.commit()
                cursor.close()
        finally:
            pass

    def close(self):
        self.connection.close()
