import psycopg2

connection = psycopg2.connect(database="plo", user="postgres", password="changeme", host="localhost", port=5432)

cursor = connection.cursor()

cursor.execute("select * from game where status = 'ongoing'")

# Fetch all rows from database
record = cursor.fetchall()

print("Data from Database:- ", record)