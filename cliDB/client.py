import mysql.connector

class SQLClient:
    
    def __init__(self, host, user, password, database, table_name):
        self.conn = mysql.connector.connect(
            host = host,
            user = user,
            password = password,
            database = database,
            auth_plugin='mysql_native_password'
        )
        self.cur = self.conn.cursor()
        self.table_name = table_name
    
    def get_all(self, limit = -1):
        if limit < 0:
            query = f"SELECT * FROM {self.table_name }"
        else:
            query = f"SELECT * FROM {self.table_name } limit {limit}"

        result = self.cur.execute(query)
        rows = self.cur.fetchall()
        return rows