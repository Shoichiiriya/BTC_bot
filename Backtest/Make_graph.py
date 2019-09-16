import matplotlib.pyplot as plt
import pandas as pd

# 日付の配列データ（x軸）
date_list = [
	"2018/1/1",
	"2018/1/2",
	"2018/1/3",
	"2018/1/4",
	"2018/1/5",
	"2018/1/6",
	"2018/1/7",
	"2018/1/8",
	"2018/1/9",
	"2018/1/10",
	"2018/1/11",
	"2018/1/12",
	"2018/1/13",
	"2018/1/14"
]

# BTC価格（ドル）のデータ（y軸）
price_list = [
	13657,
	14982,
	15201,
	15599,
	17429,
	17527,
	16477,
	15170,
	14595,
	14973,
	13405,
	13980,
	14360,
	13772
]

# 日付データに変換
date_list = pd.to_datetime(date_list)

# plot(x,y)でx軸とy軸を指定
plt.plot( date_list,price_list )
plt.xlabel("Date")
plt.ylabel("Price")

# 描写を実行
plt.show()