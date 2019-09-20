import requests
from datetime import datetime
import time
from pprint import pprint
import json

chart_sec = 60      # ローソク足の時間軸
file = "./Testdata/test_data_1min.json"    # 読み込む価格ファイル
start_period = "2019/09/12 00:00"
end_period = "2019/09/15 00:00"


# 価格ファイルからローソク足データを読み込む関数
def get_price_from_file( min,path,start_period = None, end_period = None ):
	file = open(path,"r",encoding="utf-8")
	data = json.load(file)
	
	start_unix = 0
	end_unix = 9999999999
	
	if start_period:
		start_period = datetime.strptime(start_period,"%Y/%m/%d %H:%M")
		start_unix = int(start_period.timestamp())
	if end_period:
		end_period = datetime.strptime( end_period,"%Y/%m/%d %H:%M")
		end_unix = int(end_period.timestamp())
	
	price = []
	for i in data["result"][str(min)]:
		if i[0] >= start_unix and i[0] <= end_unix:
			if i[1] != 0 and i[2] != 0 and i[3] != 0 and i[4] != 0:
				price.append({ "close_time" : i[0],
					"close_time_dt" : datetime.fromtimestamp(i[0]).strftime('%Y/%m/%d %H:%M'),
					"open_price" : i[1],
					"high_price" : i[2],
					"low_price" : i[3],
					"close_price": i[4] })
	
	return price

# ---- ここからメイン処理 ----

#ファイルから価格データを読み込む
price = get_price_from_file(chart_sec, file)


print("--------------------------")
print("テスト期間：")
print("開始時点 : " + str(price[0]["close_time_dt"]))
print("終了時点 : " + str(price[-1]["close_time_dt"]))
print(str(len(price)) + "件のローソク足データで検証")
print("--------------------------")

# どの時間のデータが抜けてるか調べる
num = int( datetime.strptime(start_period,"%Y/%m/%d %H:%M").timestamp() )
for i in range( len(price) ):
	match = False
	for p in price:
		if num == p["close_time"]:
			match = True
	if match == False:
		print("{} の価格データが存在しません".format(datetime.fromtimestamp(num)))
	num += chart_sec