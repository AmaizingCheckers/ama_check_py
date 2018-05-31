import MySQLdb
import os
from os.path import join, dirname
from dotenv import load_dotenv

class DBConnector :
  dotenv_path = join(dirname(__file__), '.env')
  load_dotenv(dotenv_path)

  def db_connect (self) :
    connector = MySQLdb.connect(
        user=os.environ.get('MYSQL_USER'),
        passwd=os.environ.get('MYSQL_PASSWORD'),
        host=os.environ.get('MYSQL_HOSTNAME'),
        port=int(os.environ.get('MYSQL_PORT')),
        db=os.environ.get('MYSQL_DATABASE')
      )

    return connector

  def db_disconnect (self, connector) :
    connector.close

