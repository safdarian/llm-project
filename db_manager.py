import mysql.connector
from utils import ConfigManager
from logging_config import LoggerManager

class DBManager:
    def __init__(self, db_info) -> None:
        self.connection = mysql.connector.connect(
            host=db_info["host"],
            user=db_info["user"],
            password=db_info["password"],
            database=db_info["database"]
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def query(self, query):
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result
    
    def get_tables(self):
        return [list(i.values())[0] for i in self.query("SHOW Tables")]
    
    def get_table_columns(self, table_name):
        q = f"SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, EXTRA FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{self.connection.database}' AND TABLE_NAME = '{table_name}'"
        return [i["COLUMN_NAME"] for i in self.query(q)]
    def get_schema(self):
        tables = self.get_tables()
        d = {t:self.get_table_columns(t) for t in tables}
        schema = ""
        for k, v in d.items():
            schema += k + " "
            schema += f'({", ".join(v)})\n'
        return schema
    
    def get_db_head(self):
        tables = self.get_tables()
        d = {t:self.get_table_columns(t) for t in tables}
        head = ""
        for k, v in d.items():
            head += "Table Name: " + '"{}"'.format(k) + "\n"
            head += 'Columns Name: ' + "(" + ", ".join(['"{}"'.format(item) for item in v]) + ")\n"
            q = f"SELECT * FROM {k} LIMIT 1"
            current = self.query(q)
            LoggerManager.log_flow(f"Generated Query: {current}", node=self.__class__.__name__)
            this_line = ""
            if len(current) > 0:
                print(current[0].items())
                this_line = "First Row Values: " + "(" + ", ".join([str(item0_v) for item0, item0_v in current[0].items()]) + ")"
            head += this_line + "\n"
        return head




if __name__ == "__main__":
    config = ConfigManager()
    db = DBManager(config["database"])

    # print(db.query("SHOW Tables;"))
    # print(db.get_schema())
    
    # print(db.get_table_columns(db.get_tables()[0]))
    # print(db.query("select * from Product"))
    # print(db.query(q))
