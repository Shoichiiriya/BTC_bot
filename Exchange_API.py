exchanges = {
"bitmex": {
    "apiKey": "B9w9XWQcQy1VzS_BrKPOkMIz",
    "apiSecret": "AucUI6RK6guU88FIHIJaHJ04QyUAW73y9OHqGTOZP5wJnX1t"
  },
  "bitmex_test": {
    "apiKey": "1kU4p8N1RBSSocUHvCcUr5r0",
    "apiSecret": "z49PYqXtFUg_W7IQBBEMhv386v9fMR83zgaQ2GKJa2BpOh29"
  }
}


# 設定項目
line_token = "Yl1yEEWeWy5VH2C8MqOIeP0uidYfxHxPY6SxngSbMAX"    # さっき保存したLINEトークン

Butmex_criptwatch = "https://api.cryptowat.ch/markets/bitmex/btcusd-perpetual-futures/ohlc"

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