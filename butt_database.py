import pymysql.cursors


class Db:
    def __init__(self, _db, username, password, test_environment):
        self._db = _db
        self.user = username
        self.passw = password
        self.test_environment = test_environment

    def build(self):
        try:
            self.connection = pymysql.connect(host='fartcannon.com', user=self.user, password=self.passw,
                                              db=self._db, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        except pymysql.err.OperationalError:
            if self.test_environment:
                #bot was loaded with test environment enabled, ignore this error
                raise
            else:
                #TODO: handle connection recovery when we can't connect.
                raise

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
        with self.connection.cursor() as cursor:
            try:
                cursor.executemany(query, args)
                self.connection.commit()
                cursor.close()
            except:
                print("Error executing this mysql query: %s" % cursor._last_executed)
                raise
            finally:
                pass
