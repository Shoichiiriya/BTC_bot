import requests
from datetime import datetime
import time
from pprint import pprint
import json

start_unix_time = 1483196400
chart_sec = 60         # 保存したいローソク足の時間軸
file = "./test_data_1min.json"   # 保存するファイル名
start_period = "2018/05/07 00:00"
end_period = "2018/05/08 00:00"


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

def accumulate_data(min, path, before=0, after=0):
	price = []
	params = {"periods" : min }
	if before != 0:
		params["before"] = before
	if after != 0:
		params["after"] = after

	response = requests.get("https://api.cryptowat.ch/markets/bitmex/btcusd-perpetual-futures/ohlc",params)
	data = response.json()

	file = open( path,"w",encoding="utf-8")
	json.dump(data,file)

	return data

# Cryptowatchから差分だけを追加して保存する関数
def accumulate_diff_data(min, path, before=0, after=0):
	
	# APIで価格データを取得
	params = {"periods" : min }
	if before != 0:
		params["before"] = before
	if after != 0:
		params["after"] = after
	response = requests.get("https://api.cryptowat.ch/markets/bitmex/btcusd-perpetual-futures/ohlc",params)
	web_data = response.json()
	web_data_set = set( map( tuple, web_data["result"][str(min)] ))
	
	# ファイルから価格データを取得
	file = open( path,"r",encoding="utf-8")
	file_data = json.load(file)
	del file_data["result"][str(min)][-1] # 末尾は被るので削除
	file_data_set = set( map( tuple, file_data["result"][str(min)] ))

	
	# 差分を取得
	diff_data_set = web_data_set - file_data_set
	diff_data = list(diff_data_set)
		
	# 差分を追加する
	if len(diff_data) != 0:
		print("{}件の追加データがありました".format( len(diff_data) ))
		diff_data.sort( key=lambda x:x[0] )
		file_data["result"][str(min)].extend( diff_data )
		pprint(diff_data)
	
	#ファイルに書き込む
	file = open( path,"w",encoding="utf-8")
	json.dump(file_data,file)
	
	return file_data

# ---- ここからメイン ----
# ここからメイン
accumulate_data(chart_sec, file ,after=start_unix_time)
# i = 0
# add_unix = chart_sec * 6000 - 100
# while i < 3:
# 	add_unix = add_unix + (chart_sec * 6000 - 100)

# 	# 差分の価格データを保存する
# 	accumulate_diff_data(chart_sec, file, after=add_unix)



# 	i = i + 1
price = get_price_from_file(chart_sec, file)
print("--------------------------")
print("テスト期間：")
print("開始時点 : " + str(price[0]["close_time_dt"]))
print("終了時点 : " + str(price[-1]["close_time_dt"]))
print(str(len(price)) + "件のローソク足データで検証")
print("--------------------------")