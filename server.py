# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import DBConnector
import eval
app = Flask(__name__)

app.config["JSON_SORT_KEYS"] = False #ソートをそのまま

@app.route('/image_matching/history/<int:history_id>', methods=['GET'])
def image_matching(history_id):

  dir = os.path.dirname(os.path.abspath(sys.argv[0]))

  dbConnector = DBConnector.DBConnector()
  connector = dbConnector.db_connect()
  cursor = connector.cursor()
  cursor.execute('SELECT * from histories WHERE timestamp=(select max(timestamp) from histories)')
  for row in cursor.fetchall () :
    img_path  = dir + "\\" + str(row[5])
    ckpt_path = dir + "\\model.ckpt"
  cursor.close
  dbConnector.db_disconnect(connector)

  result = {}
  eval_result = eval.evaluation(img_path,ckpt_path)

  if eval_result == True:
    result['status'] = 'success'
  else:
    result['status'] = 'faild'
  return jsonify(result)

if __name__ == "__main__":
  app.debug = True
  # app.run(host='0.0.0.0', port=3000)
  app.run(host='0.0.0.0', port=6001)
