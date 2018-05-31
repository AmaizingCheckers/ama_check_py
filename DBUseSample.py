import DBConnector

dbConnector = DBConnector.DBConnector()
connector = dbConnector.db_connect()
cursor = connector.cursor()
cursor.execute('select * from classrooms')
for row in cursor.fetchall () :
  print('id:' + str(row[0]) + ' name:' + row[1])

cursor.close
dbConnector.db_disconnect(connector)
