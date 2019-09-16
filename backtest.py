import requests
from datetime import datetime
import time
import json
import ccxt
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# ----バックテスト用の初期設定値
chart_sec = 3600            # 5分足
lot = 100                    # 1トレードの枚数
slippage = 0.0005          # 手数料やスリッページ（0.05％初期値）
close_condition = 0        # エントリー後、n足が経過するまでは手仕舞わない（初期値０）

backdata = "./Backtest/Testdata/test_data_1h.json"

# パラーメータを指定してCryptowatchのAPIを使用する関数
def get_price(min):
    price = []
    file = open( backdata,"r",encoding="utf-8")
    data = json.load(file)
	
    for i in data["result"][str(min)]:
        if i[1] != 0 and i[2] != 0 and i[3] != 0 and i[4] != 0:
            price.append({ "close_time" : i[0],
                "close_time_dt" : datetime.fromtimestamp(i[0]).strftime('%Y/%m/%d %H:%M'),
                "open_price" : i[1],
                "high_price" : i[2],
                "low_price" : i[3],
                "close_price": i[4] })
    return price

# json形式のファイルから価格データを読み込む関数
def get_price_from_file(path):
	file = open(path,'r',encoding='utf-8')
	price = json.load(file)
	return price



# 時間と始値・終値を表示する関数
def print_price( data ):
	print( "時間： " + datetime.fromtimestamp(data["close_time"]).strftime('%Y/%m/%d %H:%M') + " 始値： " + str(data["open_price"]) + " 終値： " + str(data["close_price"]) )

# 時間と始値・終値をログに記録する関数
def log_price( data,flag ):
	log =  "時間： " + datetime.fromtimestamp(data["close_time"]).strftime('%Y/%m/%d %H:%M') + " 始値： " + str(data["open_price"]) + " 終値： " + str(data["close_price"]) + "\n"
	flag["records"]["log"].append(log)
	return flag



# 各ローソク足が陽線・陰線の基準を満たしているか確認する関数
def check_candle( data,side ):
	try:
		realbody_rate = abs(data["close_price"] - data["open_price"]) / (data["high_price"]-data["low_price"]) 
		increase_rate = data["close_price"] / data["open_price"] - 1
	except ZeroDivisionError as e:
		return False
	
	if side == "buy":
		if data["close_price"] < data["open_price"] : return False
		#elif increase_rate <  0.0003 : return False
		#elif realbody_rate < 0.5 : return False
		else : return True
		
	if side == "sell":
		if data["close_price"] > data["open_price"] : return False
		#elif increase_rate > -0.0003 : return False
		#elif realbody_rate < 0.5 : return False
		else : return True


# ローソク足が連続で上昇しているか確認する関数
def check_ascend( data,last_data ):
	if data["open_price"] > last_data["open_price"] and data["close_price"] > last_data["close_price"]:
		return True
	else:
		return False

# ローソク足が連続で下落しているか確認する関数
def check_descend( data,last_data ):
	if data["open_price"] < last_data["open_price"] and data["close_price"] < last_data["close_price"]:
		return True
	else:
		return False


# 買いシグナルが出たら指値で買い注文を出す関数
def buy_signal( data,last_data,flag ):
	if flag["buy_signal"] == 0 and check_candle( data,"buy" ):
		flag["buy_signal"] = 1

	elif flag["buy_signal"] == 1 and check_candle( data,"buy" )  and check_ascend( data,last_data ):
		flag["buy_signal"] = 2

	elif flag["buy_signal"] == 2 and check_candle( data,"buy" )  and check_ascend( data,last_data ):
		log = "３本連続で陽線 なので" + str(data["close_price"]) + "円で買い指値を入れます\n"
		flag["records"]["log"].append(log)
		flag["buy_signal"] = 3
		
		# ここにBitflyerへの買い注文コードを入れる

		flag["order"]["exist"] = True
		flag["order"]["side"] = "BUY"
		flag["order"]["price"] = round(data["close_price"] * lot)
	
	else:
		flag["buy_signal"] = 0
	return flag


# 売りシグナルが出たら指値で売り注文を出す関数
def sell_signal( data,last_data,flag ):
	if flag["sell_signal"] == 0 and check_candle( data,"sell" ):
		flag["sell_signal"] = 1

	elif flag["sell_signal"] == 1 and check_candle( data,"sell" )  and check_descend( data,last_data ):
		flag["sell_signal"] = 2

	elif flag["sell_signal"] == 2 and check_candle( data,"sell" )  and check_descend( data,last_data ):
		log = "３本連続で陰線 なので" + str(data["close_price"]) + "円で売り指値を入れます\n"
		flag["records"]["log"].append(log)
		flag["sell_signal"] = 3
		
		# ここにBitflyerへの売り注文コードを入れる

		flag["order"]["exist"] = True
		flag["order"]["side"] = "SELL"
		flag["order"]["price"] = round(data["close_price"] * lot)
		
	else:
		flag["sell_signal"] = 0
	return flag


# 手仕舞いのシグナルが出たら決済の成行注文を出す関数
def close_position( data,last_data,flag ):
	flag["position"]["count"] += 1
	
	if flag["position"]["side"] == "BUY":
		if data["close_price"] < last_data["close_price"] and flag["position"]["count"] > close_condition:
			log = "前回の終値を下回ったので" + str(data["close_price"]) + "円あたりで成行で決済します\n"
			flag["records"]["log"].append(log)
			
			# 決済の成行注文コードを入れる

			records( flag,data )
			flag["position"]["exist"] = False
			flag["position"]["count"] = 0
			
	if flag["position"]["side"] == "SELL":
		if data["close_price"] > last_data["close_price"] and flag["position"]["count"] > close_condition:
			log = "前回の終値を上回ったので" + str(data["close_price"]) + "円あたりで成行で決済します\n"
			flag["records"]["log"].append(log)
			
			# 決済の成行注文コードを入れる

			records( flag,data )
			flag["position"]["exist"] = False
			flag["position"]["count"] = 0
	return flag


# サーバーに出した注文が約定したかどうかチェックする関数
def check_order( flag ):
	
	# 注文状況を確認して通っていたら以下を実行
	# 一定時間で注文が通っていなければキャンセルする
	
	flag["order"]["exist"] = False
	flag["order"]["count"] = 0
	flag["position"]["exist"] = True
	flag["position"]["side"] = flag["order"]["side"]
	flag["position"]["price"] = flag["order"]["price"]
	
	return flag

# 各トレードのパフォーマンスを記録する関数
def records(flag,data):
	
	# 取引手数料等の計算
	entry_price = flag["position"]["price"]
	exit_price = round(data["close_price"] * lot)
	trade_cost = round( exit_price * slippage )
	
	log = "スリッページ・手数料として " + str(trade_cost) + "円を考慮します\n"
	flag["records"]["log"].append(log)
	flag["records"]["slippage"].append(trade_cost)
	
	# 値幅の計算
	buy_profit = exit_price - entry_price - trade_cost
	sell_profit = entry_price - exit_price - trade_cost
	
	# 利益が出てるかの計算
	if flag["position"]["side"] == "BUY":
		flag["records"]["buy-count"] += 1
		flag["records"]["buy-profit"].append( buy_profit )
		flag["records"]["buy-return"].append( round( buy_profit / entry_price * 100, 4 ))
		flag["records"]["gross-profit"].append( flag["records"]["gross-profit"][-1] + buy_profit )
		flag["records"]["date"].append( data["close_time_dt"])

		if buy_profit  > 0:
			flag["records"]["buy-winning"] += 1
			log = str(buy_profit) + "円の利益です\n"
			flag["records"]["log"].append(log)
		else:
			log = str(buy_profit) + "円の損失です\n"
			flag["records"]["log"].append(log)
	
	if flag["position"]["side"] == "SELL":
		flag["records"]["sell-count"] += 1
		flag["records"]["sell-profit"].append( sell_profit )
		flag["records"]["sell-return"].append( round( sell_profit / entry_price * 100, 4 ))
		flag["records"]["gross-profit"].append( flag["records"]["gross-profit"][-1] + sell_profit )
		flag["records"]["date"].append( data["close_time_dt"])
		if sell_profit > 0:
			flag["records"]["sell-winning"] += 1
			log = str(sell_profit) + "円の利益です\n"
			flag["records"]["log"].append(log)
		else:
			log = str(sell_profit) + "円の損失です\n"
			flag["records"]["log"].append(log)
	
	return flag


# バックテストの集計用の関数
def backtest(flag):
	
	buy_gross_profit = np.sum(flag["records"]["buy-profit"])
	sell_gross_profit = np.sum(flag["records"]["sell-profit"])
	
	print("バックテストの結果")
	print("--------------------------")
	print("買いエントリの成績")
	print("--------------------------")
	print("トレード回数  :  {}回".format(flag["records"]["buy-count"] ))
	print("勝率          :  {}％".format(round(flag["records"]["buy-winning"] / flag["records"]["buy-count"] * 100,1)))
	print("平均リターン  :  {}％".format(round(np.average(flag["records"]["buy-return"]),4)))
	print("総損益        :  {}円".format( np.sum(flag["records"]["buy-profit"]) ))
	
	print("--------------------------")
	print("売りエントリの成績")
	print("--------------------------")
	print("トレード回数  :  {}回".format(flag["records"]["sell-count"] ))
	print("勝率          :  {}％".format(round(flag["records"]["sell-winning"] / flag["records"]["sell-count"] * 100,1)))
	print("平均リターン  :  {}％".format(round(np.average(flag["records"]["sell-return"]),4)))
	print("総損益        :  {}円".format( np.sum(flag["records"]["sell-profit"]) ))
	
	print("--------------------------")
	print("総合の成績")
	print("--------------------------")
	print("総損益        :  {}円".format( np.sum(flag["records"]["sell-profit"]) + np.sum(flag["records"]["buy-profit"]) ))
	print("手料合計    :  {}円".format( np.sum(flag["records"]["slippage"]) ))
	
    # 損益曲線をプロット
	del flag["records"]["gross-profit"][0] # X軸/Y軸のデータ数を揃えるため、先頭の0を削除
	date_list = pd.to_datetime( flag["records"]["date"] ) # 日付型に変換

	plt.plot( date_list, flag["records"]["gross-profit"] )
	plt.xlabel("Date")
	plt.ylabel("Balance")
	plt.xticks(rotation=50) # X軸の目盛りを50度回転
        
	plt.show()

	# ログファイルの出力
	file =  open("./{0}-log.txt".format(datetime.now().strftime("%Y-%m-%d-%H-%M")),'wt',encoding='utf-8')
	file.writelines(flag["records"]["log"])
	
# ここからメインの実行処理

# 価格チャートを取得
price = get_price(chart_sec)

print("--------------------------")
print("テスト期間：")
print("開始時点 : " + str(price[0]["close_time_dt"]))
print("終了時点 : " + str(price[-1]["close_time_dt"]))
print(str(len(price)) + "件のローソク足データで検証")
print("--------------------------")



last_data = price[0] # 初期値となる価格データをセット


flag = {
	"buy_signal":0,
	"sell_signal":0,
	"order":{
		"exist" : False,
		"side" : "",
		"price" : 0,
		"count" : 0
	},
	"position":{
		"exist" : False,
		"side" : "",
		"price": 0,
		"count":0
	},
	"records":{
		"buy-count": 0,
		"buy-winning" : 0,
		"buy-return":[],
		"buy-profit": [],
		
		"sell-count": 0,
		"sell-winning" : 0,
		"sell-return":[],
		"sell-profit":[],
        
		"date":[],
	    "gross-profit":[0],
		"slippage":[],
		"log":[]
	}
}

i = 1
while i < len(price):
	if flag["order"]["exist"]:
		flag = check_order( flag )
	
	data = price[i]
	flag = log_price(data,flag)
	
	if flag["position"]["exist"]:
		flag = close_position( data,last_data,flag )			
	else:
		flag = buy_signal( data,last_data,flag )
		flag = sell_signal( data,last_data,flag )
	last_data["close_time"] = data["close_time"]
	last_data["open_price"] = data["open_price"]
	last_data["close_price"] = data["close_price"]
	i+=1

backtest(flag)