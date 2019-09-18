import pandas as pd

# 上の配列データをくっつけて１つの表データにする

Date = ["2018-02-04","2018-02-04","2018-02-05","2018-03-06","2018-03-08"]
Profit = [20143,22121,33412,-2312,-16125]
Side = ["BUY","SELL","SELL","BUY","SELL"]
Rate = [0.024,0.012,0.014,-0.022,-0.019]
Periods = [6,14,13,15,9]


records = pd.DataFrame({
	"Date":pd.to_datetime(Date), # 文字を日付型に変換
	"Profit":Profit,
	"Side":Side,
	"Rate":Rate,
	"Periods":Periods
})
print( records.Profit.mean() )