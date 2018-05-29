# -*- coding: utf-8 -*-

import cv2
import numpy as np
import os

#HAAR分類器の顔検出用の特徴量
cascade_path = "haarcascade_frontalface_alt.xml"


# 使用ファイルと入出力ディレクトリ
image_file = "./test.png"
output_file = "./output.png"
#image_path = "./python/test.png"
# ディレクトリ確認用(うまく行かなかった時用)

#print(os.path.exists(image_path))

#ファイル読み込み

image = cv2.imread(image_file)

#グレースケール変換
image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#カスケード分類器の特徴量を取得する
cascade = cv2.CascadeClassifier(cascade_path)

#物体認識（顔認識）の実行
#image – CV_8U 型の行列．ここに格納されている画像中から物体が検出されます
#objects – 矩形を要素とするベクトル．それぞれの矩形は，検出した物体を含みます
#scaleFactor – 各画像スケールにおける縮小量を表します
#minNeighbors – 物体候補となる矩形は，最低でもこの数だけの近傍矩形を含む必要があります
#flags – このパラメータは，新しいカスケードでは利用されません．古いカスケードに対しては，cvHaarDetectObjects 関数の場合と同じ意味を持ちます
#minSize – 物体が取り得る最小サイズ．これよりも小さい物体は無視されます
facerect = cascade.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=1, minSize=(40, 40))

#print(facerect)
color = (255, 255, 255) #白

# 検出した場合
if len(facerect) > 0:
	path = os.path.splitext(image_file)
	dir_path = 'pickup_face'

i = 0;
for rect in facerect:
    
	#顔だけ切り出して保存
	x = rect[0]
	y = rect[1]
	width = rect[2]
	height = rect[3]
	dst = image[y:y+height, x:x+width]
	new_image_path = dir_path + '/' + str(i) + path[1];
	cv2.imwrite(new_image_path, dst)
	i += 1