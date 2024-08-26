import psycopg2

connection = psycopg2.connect(database="postgres", user="postgres", password="changeme", host="localhost", port=5432)

cursor = connection.cursor()

cursor.execute("SELECT 1;")

# Fetch all rows from database
record = cursor.fetchall()

print("Data from Database:- ", record)