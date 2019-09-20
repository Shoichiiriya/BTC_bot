import requests
from datetime import datetime
import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv
import json
import find_parameter as fp


# バックテストのパラメーター設定
#---------------------------------------------------------------------------------------------
chart_sec_list  = [ 3600, 7200, 14400 ] # テストに使う時間軸
buy_term_list   = [ 10,15,20,25,30,35,40,45 ] # テストに使う上値ブレイクアウトの期間
sell_term_list  = [ 10,15,20,25,30,35,40,45 ] # テストに使う下値ブレイクアウトの期間
judge_price_list = [
	{"BUY":"close_price","SELL":"close_price"}, # ブレイクアウト判定に終値を使用
	{"BUY":"high_price","SELL":"low_price"}     # ブレイクアウト判定に高値・安値を使用
]
#---------------------------------------------------------------------------------------------

# テストごとの各パラメーターの組み合わせと結果を記録する配列を準備
param_buy_term  = []
param_sell_term = []
param_chart_sec = []
param_judge_price = []

result_count = []
result_winRate = []
result_returnRate = []
result_drawdown = []
result_profitFactor = []
result_gross = []

wait = 0            # ループの待機時間



# ドンチャンブレイクを判定する関数
def donchian( data,last_data ):
	
	highest = max(i["high_price"] for i in last_data[ (-1* buy_term): ])
	if data[ judge_price["BUY"] ] > highest:
		return {"side":"BUY","price":highest}
	
	lowest = min(i["low_price"] for i in last_data[ (-1* sell_term): ])
	if data[ judge_price["SELL"] ] < lowest:
		return {"side":"SELL","price":lowest}
	
	return {"side" : None , "price":0}

#---------------------------------------------------------------------------------------------

# ここからメイン処理

# バックテストに必要な時間軸のチャートをすべて取得
price_list = {}
for chart_sec in chart_sec_list:
	price_list[ chart_sec ] = fp.get_price(chart_sec)

# 総当たりのためのfor文の準備
combinations = [(chart_sec, buy_term, sell_term, judge_price)
	for chart_sec in chart_sec_list
	for buy_term  in buy_term_list
	for sell_term in sell_term_list
	for judge_price in judge_price_list]

for chart_sec, buy_term, sell_term,judge_price in combinations:
	
	price = price_list[ chart_sec ]
	last_data = []
	i = 0
	
	# フラッグ変数の初期化
	flag = fp.test_flag
	
	while i < len(price):
		
		# ドンチャンの判定に使う期間分の安値・高値データを準備する
		if len(last_data) < buy_term or len(last_data) < sell_term:
			last_data.append(price[i])
			time.sleep(wait)
			i += 1
			continue
		
		data = price[i]
		
		if flag["order"]["exist"]:
			flag = fp.check_order( flag )
		elif flag["position"]["exist"]:
			signal = donchian( data,last_data )
			flag = fp.close_position( data, last_data, signal, flag )
		else:
			signal = donchian( data,last_data )
			flag = fp.entry_signal( data, last_data, signal, flag )
		
		last_data.append( data )
		i += 1
		time.sleep(wait)

	fp.print_text(price, chart_sec, buy_term, sell_term)
	
	result = fp.backtest( flag )
	# 今回のループで使ったパラメータの組み合わせを配列に記録する
	param_buy_term.append( buy_term )
	param_sell_term.append( sell_term )
	param_chart_sec.append( chart_sec )
	if judge_price["BUY"] == "high_price":
		param_judge_price.append( "高値/安値" )
	else:
		param_judge_price.append( "終値/終値" )
	# 今回のループのバックテスト結果を配列に記録する
	result_count.append( result["トレード回数"] )
	result_winRate.append( result["勝率"] )
	result_returnRate.append( result["平均リターン"] )
	result_drawdown.append( result["最大ドローダウン"] )
	result_profitFactor.append( result["プロフィットファクタ―"] )
	result_gross.append( result["最終損益"] )
	
	

# 全てのパラメータによるバックテスト結果をPandasで１つの表にする
df = pd.DataFrame({
	"時間軸"        :  param_chart_sec,
	"買い期間"      :  param_buy_term,
	"売り期間"      :  param_sell_term,
	"判定基準"      :  param_judge_price,
	"トレード回数"  :  result_count,
	"勝率"          :  result_winRate,
	"平均リターン"  :  result_returnRate,
	"ドローダウン"  :  result_drawdown,
	"PF"            :  result_profitFactor,
	"最終損益"      :  result_gross
})

# 列の順番を固定する
df = df[[ "時間軸","買い期間","売り期間","判定基準","トレード回数","勝率","平均リターン","ドローダウン","PF","最終損益"  ]]

# トレード回数が100に満たない記録は消す
df.drop( df[ df["トレード回数"] < 100].index, inplace=True )

# 最終結果をcsvファイルに出力
df.to_csv("./log/param/result-{}.csv".format(datetime.now().strftime("%Y-%m-%d-%H-%M")) )

