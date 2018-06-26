#!/usr/bin/env python 
#! -*- coding: utf-8 -*-

import sys
import numpy as np
import cv2
import tensorflow as tf
import os
import random
import main
import DBConnector
from datetime import datetime

dir = os.path.dirname(os.path.abspath(sys.argv[0]))
#print(dir)
# OpenCVのデフォルトの顔の分類器のpath
cascade_path    = dir + '\\haarcascade_frontalface_default.xml'
faceCascade     = cv2.CascadeClassifier(cascade_path)
redsquare_path  = dir + '\\pickup_face\\red_square'
cutface_path    = dir + '\\pickup_face\\cut_face'
# 識別ラベルと各ラベル番号に対応する名前
student_name = []
m = 0
dbConnector = DBConnector.DBConnector()
connector = dbConnector.db_connect()
cursor = connector.cursor()
cursor.execute('SELECT * from students')
for row in cursor.fetchall () :
  student_name.append(row[1])
cursor.close
dbConnector.db_disconnect(connector)

HUMAN_NAMES = {}
for i in range(len(student_name)):
  HUMAN_NAMES[m] = student_name[m]
  m += 1

#指定した画像(img_path)を学習結果(ckpt_path)を用いて判定する
def evaluation(img_path, ckpt_path):
  # GraphのReset(らしいが、何をしているのかよくわかっていない…)
  tf.reset_default_graph()

  # ファイルを開く
  f = open(img_path, 'r')
  img = cv2.imread(img_path, cv2.IMREAD_COLOR)

  # モノクロ画像に変換
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  face = faceCascade.detectMultiScale(gray, 1.1, 3)

  if len(face) > 0:
    for rect in face:
      # 加工した画像に何でもいいので適当な名前をつけたかった。日付秒数とかでいいかも
      random_str = str(random.random())

      # 顔部分を赤線で書こう
      cv2.rectangle(img, tuple(rect[0:2]), tuple(rect[0:2]+rect[2:4]), (0, 0, 255), thickness=2)

      # 顔部分を赤線で囲った画像の保存先
      face_detect_img_path = redsquare_path + "/red_square" + random_str + '.jpg'

      # 顔部分を赤線で囲った画像の保存
      cv2.imwrite(face_detect_img_path, img)
      x = rect[0]
      y = rect[1]
      w = rect[2]
      h = rect[3]

      # 検出した顔を切り抜いた画像を保存
      cv2.imwrite(cutface_path + "/cut_face" + random_str + '.jpg', img[y:y+h, x:x+w])

      # TensorFlowへ渡す切り抜いた顔画像
      target_image_path = cutface_path + "/cut_face" + random_str + '.jpg'
  else:
    # 顔が見つからなければ処理終了
    print ('image:No Face')
    return False
    f.close()
    f = open(target_image_path, 'r')

  # データを入れる配列
  image = []
  img = cv2.imread(target_image_path)
  img = cv2.resize(img, (28, 28))

  # 画像情報を一列にした後、0-1のfloat値にする
  image.append(img.flatten().astype(np.float32)/255.0)
  # numpy形式に変換し、TensorFlowで処理できるようにする
  image = np.asarray(image)

  # 入力画像に対して、各ラベルの確率を出力して返す(main.pyより呼び出し)
  logits = main.inference(image, 1.0)

  # We can just use 'c.eval()' without passing 'sess'
  sess = tf.InteractiveSession()

  # restore(パラメーター読み込み)の準備
  saver = tf.train.Saver()

  # 変数の初期化
  sess.run(tf.global_variables_initializer())

  if ckpt_path:
    # 学習後のパラメーターの読み込み
    saver.restore(sess, ckpt_path)

  # sess.run(logits)と同じ
  softmax = logits.eval()

  # 判定結果
  result = softmax[0]
  
  # 判定結果を%にして四捨五入
  rates = [round(n * 100.0, 1) for n in result]
  humans = []

  # ラベル番号、名前、パーセンテージのHashを作成
  for index, rate in enumerate(rates):
    name = HUMAN_NAMES[index]
    humans.append({
      'label': index,
      'name': name,
      'rate': rate
    })

  # パーセンテージの高い順にソート
  rank = sorted(humans, key=lambda x: x['rate'], reverse=True)

  # 結果をコンソールに出力
  print (rank)
  #print (rank[0]['name'])
  name2 = rank[0]['name']


  # 結果をDBに挿入
  student_id = []
  history_id = []

  #ヒストリーIDとサブジェクトIDの取得
  dbConnector = DBConnector.DBConnector()
  connector = dbConnector.db_connect()
  cursor = connector.cursor()
  cursor.execute('SELECT * from histories')
  for row in cursor.fetchall () :
    subject_id = row[2]
    history_id = row[0]

  #一致するサブジェクトIDのstudent_idをリストで取ってくる
  cursor.execute('SELECT * from subject_students')
  for row in cursor.fetchall () :
    if subject_id == row[1]:
      student_id.append(row[2])
  #print (student_id)
  #print (subject_id)
  #print (history_id)
  
  #結果と一致する名前の行からstudent_idを取ってきて挿入
  cursor.execute("SELECT * from students where name='%s'" % name2)
  for row in cursor.fetchall () : 
    #print(row)
    n = 0
    for i in student_id :
      if student_id[n] == row[0] :
        date = (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        sql_insert = ("INSERT into history_students(history_id,student_id,created_at,updated_at) values (%s,%s,%s,%s)")
        cursor.execute(sql_insert,(history_id,student_id[n],date,date))
        #print("ok")
        break
      else:
        n += 1
        #print("miss")
  cursor.close
  dbConnector.db_disconnect(connector)

  # 判定結果と加工した画像のpathを返す
  return True

# コマンドラインからのテスト用
if __name__ == '__main__':
  dbConnector = DBConnector.DBConnector()
  connector = dbConnector.db_connect()
  cursor = connector.cursor()
  cursor.execute('SELECT * from histories WHERE timestamp=(select max(timestamp) from histories)')
  for row in cursor.fetchall () :
    evaluation(dir + "\\" + str(row[5]), dir + "\\model.ckpt")
  cursor.close
  dbConnector.db_disconnect(connector)



