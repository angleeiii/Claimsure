import mysql.connector


def connect_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="claimsure_db"
        )

        if connection.is_connected():
            print("Connected to Claimsure Database!")
            return connection

    except mysql.connector.Error as error:
        print("Database connection failed:", error)
        return None