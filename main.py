from database import connect_database

connection = connect_database()

if connection:
    print("Claimsure System Started!")
    connection.close()