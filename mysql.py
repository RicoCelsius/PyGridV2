import mysql.connector
import config
from dotenv import load_dotenv, find_dotenv
import config
import os


load_dotenv(find_dotenv())
HOST = os.environ.get("HOST")
USER = os.environ.get("USER")
PASSWORD = os.environ.get("PASSWORD")
DATABASE = os.environ.get("DATABASE")

class Mysql:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            try:
                mydb = mysql.connector.connect(
                    host=f'{config.mysql_host}',
                    user=f'{config.mysql_username}',
                    password=f'{config.mysql_password}',
                    database=f'{config.mysql_database}',
                    auth_plugin='mysql_native_password'
                )
                cls._instance = super().__new__(cls)
                cls._instance.mydb = mydb
                cls._instance.isConnected = True
                cls._instance.cursor = mydb.cursor()
                if cls._instance.database_exists(DATABASE) != DATABASE:
                    cls._instance.create_database(DATABASE) 
            except Exception as e: 
                print(e)
        return cls._instance
    
    def database_exists(self, db_name):
        self.cursor.execute("SHOW DATABASES")
        result = self.cursor.fetchall()
        db_list = [item[0] for item in result]
        return db_name in db_list
    
    def create_database(self, db_name):
        sql = f"CREATE DATABASE {db_name}"
        self.cursor.execute(sql)
        return True

    def create(self, name, age):
        sql = "INSERT INTO example_table (name, age) VALUES (%s, %s)"
        val = (name, age)
        self.cursor.execute(sql, val)
        self.mydb.commit()
        return self.cursor.lastrowid

    def read(self, id):
        sql = "SELECT * FROM example_table WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        if result:
            return {'id': result[0], 'name': result[1], 'age': result[2]}
        else:
            return None

    def update(self, id, name=None, age=None):
        if name is None and age is None:
            return False
        update_fields = []
        val = []
        if name is not None:
            update_fields.append("name = %s")
            val.append(name)
        if age is not None:
            update_fields.append("age = %s")
            val.append(age)
        val.append(id)
        sql = "UPDATE example_table SET " + ", ".join(update_fields) + " WHERE id = %s"
        self.cursor.execute(sql, tuple(val))
        self.mydb.commit()
        return True if self.cursor.rowcount > 0 else False

    def delete(self, id):
        sql = "DELETE FROM example_table WHERE id = %s"
        val = (id,)
        self.cursor.execute(sql, val)
        self.mydb.commit()
        return True if self.cursor.rowcount > 0 else False

