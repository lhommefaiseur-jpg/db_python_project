import mysql.connector 
from mysql.connector import Error 




def connection_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password ="amjad",
            database="ipam_db",
        )
    except Error as e:
        print("Database connection error:", e)
        return None


def run_query(sql, params=None):
    connection = connection_db()
    if connection is None:
        return []

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params)
        return cursor.fetchall()
    except Error as e:
        print("Query error:", e)
        return []
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()



def run_transaction(statements, expect_one_row=False):
    connection = connection_db()
    if connection is None:
        return False

    cursor = None
    try:
        cursor = connection.cursor()
        for sql, params in statements:
            cursor.execute(sql, params)
            if expect_one_row and cursor.rowcount != 1:
                connection.rollback()
                return False
        connection.commit()
        return True
    except Error as e:
        connection.rollback()
        print("Transaction error:", e)
        return False
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()



def run_command(sql, params=None):
    return run_transaction([(sql, params)])
