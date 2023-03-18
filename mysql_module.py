import mysql.connector
import config
from dotenv import load_dotenv, find_dotenv
import config
import os


load_dotenv(find_dotenv())
HOST = os.environ.get("HOST")
USER = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
DATABASE = os.environ.get("DATABASE")
TABLE = 'trades'
global connection

class Mysql:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            try:
                conn = cls.connectToMysql()
                cursor = conn.cursor(buffered=True)
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
                cursor.execute(f"USE {DATABASE}")
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS {TABLE} (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        pair VARCHAR(50) NOT NULL,
                        order_type VARCHAR(50) NOT NULL,
                        side VARCHAR(50) NOT NULL,
                        quantity DECIMAL(20, 10) NOT NULL,
                        status VARCHAR(50) NOT NULL,
                        exchange VARCHAR(50) NOT NULL,
                        order_id BIGINT,
                        price DECIMAL(20, 10),
                        avg_fill_price DECIMAL(20, 10)
                    )
            """)
                conn.close()
                cls._instance = super().__new__(cls)
                cls._instance.mydb = cls.connectToMysql(DATABASE)
                cls._instance.cursor = cls._instance.mydb.cursor()
            except mysql.connector.Error as e:
                print(e)
        return cls._instance

    
    def connectToMysql(db=None):
            try:
                conn = mysql.connector.connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=db
                )
                print(f'Connected {USER} to {db if db != None else "MySQL process"} {f"on host {HOST}" if db != None else ""}')
                return conn
            except Exception as e: print(e)

    def insert_order(self,pair, order_type, side, quantity, status, exchange, order_id,price):
        # Connect to MySQL
        conn = self._instance.mydb
        # Insert the new row
        cursor = conn.cursor()
        sql = f"INSERT INTO {TABLE} (pair, order_type, side, quantity, status, exchange, order_id, price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (pair, order_type, side, quantity, status, exchange, order_id,price)
        cursor.execute(sql, val)
        
        # Commit the changes and close the connection
        conn.commit()
        print(f'Created new entry in {TABLE}, {val}')

    
    def select_by_status(self, status):
        try:
            sql = f"SELECT * FROM {TABLE} WHERE status = %s"
            val = (status,)
            self.cursor.execute(sql, val)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)





    def update(self, order_id, status=None,avg_fill_price=None):
        try:
            update_fields = []
            val = []
            if status is not None:
                update_fields.append("status = %s")
                val.append(status)
            if avg_fill_price is not None:
                update_fields.append("avg_fill_price = %s")
                val.append(avg_fill_price)
            val.append(order_id)
            sql = f"UPDATE {TABLE} SET " + ", ".join(update_fields) + " WHERE order_id = %s"
            self.cursor.execute(sql, tuple(val))
            self.mydb.commit()
            return True if self.cursor.rowcount > 0 else False
        except Exception as e: print(e)

    def delete(self, order_id):
        try:
            sql = f"DELETE FROM {TABLE} WHERE order_id = %s"
            val = (order_id,)
            self.cursor.execute(sql, val)
            self.mydb.commit()
            return True if self.cursor.rowcount > 0 else False
        except Exception as e: print(e)

    