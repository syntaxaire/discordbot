import pymysql.cursors


class db:
    def __init__(self, _db, username, password):
        self._db = _db
        self.user = username
        self.passw = password

    def build(self):
        self.connection = pymysql.connect(host='fartcannon.com', user=self.user, password=self.passw,
                                          db=self._db, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    def do_query(self, db_, query, args=''):
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
        return result

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

    def do_insertmany(self, query, args):
        self.build()
        try:
            with self.connection.cursor() as cursor:
                cursor.executemany(query, args)
                self.connection.commit()
                cursor.close()
        finally:
            pass

    def close(self):
        self.connection.close()
