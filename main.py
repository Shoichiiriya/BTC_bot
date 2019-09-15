import ccxt
import requests
import Exchange_API as API
from datetime import datetime
import time

#apiを使ってログイン
exchange = ccxt.bitmex()
exchange.urls['api'] = exchange.urls['test']
exchange.apiKey = API.exchanges["bitmex_test"]["apiKey"]
exchange.secret = API.exchanges["bitmex_test"]["apiSecret"]

def print_price(price):
    print( "時間： " + datetime.fromtimestamp(price["close_time"]).strftime('%Y/%m/%d %H:%M')
        + " 始値： " + str(price["open_price"])
        + " 終値： " + str(price["close_price"]) )

def get_price(min, cnt):
    while True:
        try:
            # APIで価格を取得する
            response = requests.get("https://api.cryptowat.ch/markets/bitmex/btcusd-perpetual-futures/ohlc",params = { "periods" : min })
            response.raise_for_status()
            r = response.json()
            price = r["result"][str(min)][cnt]
            
            # 日時・終値・始値の３つを返す
            return{ "close_time" : price[0],
                    "open_price" : price[1],
                    "high_price" : price[2],
                    "low_price"  : price[3],
                    "close_price": price[4] }
        except requests.exceptions.RequestException as e:
            print("Cryptowatchの価格取得でエラー発生 : ",e)
            print("10秒待機してやり直します")
            time.sleep(10)


def check_candle(price, side):
    if side == "buy":  
        if price["open_price"] < price["close_price"]: return False
        elif ((price["close_price"] - price["open_price"]) / (price["high_price"] - price["low_price"])) > 0.5: return False
        elif ((price["close_price"] / price["open_price"]) - 1) > 0.0002: return False
        else : return True    
    elif side == "sell":  
        if price["open_price"] > price["close_price"]: return False
        elif ((price["close_price"] - price["open_price"]) / (price["high_price"] - price["low_price"])) > 0.5: return False
        elif ((price["close_price"] / price["open_price"]) - 1) < -0.0002: return False
        else : return True    


def check_ascend(price, last_price):
    if price["open_price"] > last_price["open_price"] and price["close_price"] > last_price["close_price"]:
        return True
    else:
        return False


def check_descend(price, last_price):
    if price["open_price"] < last_price["open_price"] and price["close_price"] < last_price["close_price"]:
        return True
    else:
        return False

def buy_signal( price, last_price, flag):
    if flag["buy_signal"] == 0 and check_candle(price, "buy"):
        flag["buy_signal"] = 1
    elif flag["buy_signal"] == 1 and check_candle(price, "buy"):# and check_ascend(price, last_price):
        flag["buy_signal"] = 2
        print("陽線2本")
    elif flag["buy_signal"] == 2 and check_candle(price, "buy"):# and check_ascend(price, last_price):
        flag["buy_signal"] = 3
        print("陽線3本‼　BUY!!")
        line_notify("陽線3本‼　BUY!!")
        while True:
            try:
                order = exchange.create_order(
                        symbol = 'BTC/USD',
                        type ='limit',
                        side ='buy',
                        price = price["close_price"],
                        amount ='10')
                flag["order"]["exist"] = True
                flag["order"]["side"] = "BUY"
                time.sleep(30)
                break
            except ccxt.BaseError as e:
                print("exchangeのAPIでエラー発生",e)
                print("注文の通信が失敗しました。30秒後に再トライします")
                time.sleep(30)
    else:
        flag["buy_signal"] = 0
    return flag

def sell_signal( price, last_price, flag):
    if flag["sell_signal"] == 0 and check_candle(price, "sell"):
        flag["sell_signal"] = 1
    elif flag["sell_signal"] == 1 and check_candle(price, "sell"):# and check_descend(price, last_price):
        flag["sell_signal"] = 2
        print("陰線2本")
    elif flag["sell_signal"] == 2 and check_candle(price, "sell"):# and check_descend(price, last_price):
        flag["sell_signal"] = 3
        print("陰線3本‼　SELL!!")
        line_notify("陰線3本‼　BUY!!")
        
        while True:
            try:
                order = exchange.create_order(
                        symbol = 'BTC/USD',
                        type ='limit',
                        side ='sell',
                        amount = 10,
                        price = price["close_price"]
                        )
                flag["order"]["exist"] = True
                flag["order"]["side"] = "SELL"
                time.sleep(30)
                break
            except ccxt.BaseError as e:
                print("exchangeのAPIでエラー発生",e)
                print("注文の通信が失敗しました。30秒後に再トライします")
                time.sleep(30)
    else:
        flag["sell_signal"] = 0
    return flag


def check_order(flag):
    try:
        position = exchange.private_get_position()
        orders = exchange.fetch_open_orders(symbol = 'BTC/USD')		
    except ccxt.BaseError as e:
                    print("exchangeのAPIでエラー発生",e)
    else:
        if position:
            print("注文が約定しました！")
            flag["order"]["exist"] = False
            flag["order"]["count"] = 0
            flag["position"]["exist"] = True
            flag["position"]["side"] = flag["order"]["side"]
        else:
            if orders:
                print("まだ未約定の注文があります")
                for order in orders:
                  print( order["id"] )
                flag["order"]["count"] += 1			
                if flag["order"]["count"] > 6:
                  flag = cancel_order(orders, flag)
            else:
                print("注文が遅延しているようです")

    return flag

def close_position( price, last_price, flag):
    if flag["position"]["side"] == "BUY":
        if price["close_price"] < last_price["close_price"]:
            print("前回の終値を下回ったので" + str(price["close_price"]) + "で決済")
            line_notify("前回の終値を下回ったので" + str(price["close_price"]) + "で決済")
            while True:
                try:
                    order = exchange.create_order(
                        symbol = 'BTC/USD',
                        type='market',
                        side='sell',
                        amount='10')       
                    flag["position"]["exist"] = False
                    time.sleep(30)
                    break
                except ccxt.BaseError as e:
                    print("exchangeのAPIでエラー発生",e)
                    print("注文の通信が失敗しました。30秒後に再トライします")
                    time.sleep(30)
    if flag["position"]["side"] == "SELL":
        if price["close_price"] > last_price["close_price"]:
            print("前回の終値を上回ったので" + str(price["close_price"]) + "で決済")
            line_notify("前回の終値を上回ったので" + str(price["close_price"]) + "で決済")
            while True:
                try:
                    order = exchange.create_order(
                        symbol = 'BTC/USD',
                        type='market',
                        side='buy',
                        amount='10')
                    flag["position"]["exist"] = False
                    time.sleep(30)
                    break
                except ccxt.BaseError as e:
                    print("exchangeのAPIでエラー発生",e)
                    print("注文の通信が失敗しました。30秒後に再トライします")
                    time.sleep(30)		
    return flag

def cancel_order(orders, flag):
    try:
        for order in orders:
            exchange.cancel_order(
                symbol = "BTC/USD",
                id = order["id"])
        print("約定していない注文をキャンセルしました")
        flag["order"]["count"] = 0
        flag["order"]["exist"] = False

        time.sleep(0)
        position = exchange.private_get_position()
        if not position:
            print("現在、未決済の建玉はありません")
        else:
            print("現在、まだ未決済の建玉があります")
            flag["position"]["exist"] = True
            flag["position"]["side"] = position[0]["side"]
    except ccxt.BaseError as e:
		    print("BitflyerのAPIで問題発生 ： ", e)
    
    return flag

# 設定項目
line_token = "Yl1yEEWeWy5VH2C8MqOIeP0uidYfxHxPY6SxngSbMAX"    # さっき保存したLINEトークン

# LINEに通知する関数
def line_notify( text ):
	url = "https://notify-api.line.me/api/notify"
	data = {"message" : text}
	headers = {"Authorization": "Bearer " + line_token} 
	requests.post(url, data=data, headers=headers)



last_price = get_price(60, -2)
print_price(last_price)

flag = {
	"buy_signal":0,
	"sell_signal":0,
	"order":{
		"exist" : False,
		"side" : "",
		"count" : 0
	},
	"position":{
		"exist" : False,
		"side" : ""
	}
}
time.sleep(10)

while True:
    if flag["order"]["exist"]:
        flag = check_order(flag)

    price = get_price(60, -2)
    #前回の値と違う場合
    if price["close_time"] != last_price["close_time"]:
        print_price(price)  
        
        if flag["position"]["exist"]:
            flag = close_position(price, last_price, flag)
        else:
            flag = buy_signal(price, last_price, flag)
            flag = sell_signal(price, last_price, flag)

        last_price = price
    time.sleep(10)



#取引所のオーダーブック一覧を取得
# order_book = exchange.fetch_order_book('BTC/USD')
# print("BIDS:", order_book['asks'])
# print("ASKS:", order_book['bids'])

#買いが入っている値段と売りが入っている値段のみを抽出
# ask = order_book["asks"][0][0] #買い（赤）
# bid = order_book["bids"][0][0] #売り（緑）
# print("ask:{},bid:{}".format(ask,bid))

#発注(1BTCを$8で買うというありえない注文)
#bitmex.create_order('注文する通貨',指値(limit)か成行(market)か,量,値段)
# order = exchange.create_order('BTC/USD', type='limit', side='buy', amount=1, price=8)
# print("注文が完了しました:{}".format(order))

# キャンセルに必要なorderIDだけを取り出す

# print(order['info']['orderID'])
###注文のキャンセル
# cancel = exchange.cancel_order(order['info']['orderID'])
# print("注文をキャンセルしました:{}".format(cancel))