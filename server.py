# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify

app = Flask(__name__)

app.config["JSON_SORT_KEYS"] = False #ソートをそのまま

@app.route('/image_matching/history/<int:history_id>', methods=['GET'])
def image_matching(history_id):
  result = {
    'historyId': history_id
  }
  return jsonify(result)

if __name__ == "__main__":
  app.debug = True
  # app.run(host='0.0.0.0', port=3000)
  app.run(host='0.0.0.0', port=6001)
