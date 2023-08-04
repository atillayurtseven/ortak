import requests

version = "1.0.1"

# Telefon numaranızı ve şifrenizi yazın
PHONE = "+905554443322"
PASSWORD = "Password.123!"

BASE_ENDPOINT = "https://prod.roketapp.site/"
endpoints = {
    "login": BASE_ENDPOINT + "identity/user/login",
    "order": BASE_ENDPOINT + "wallet/order",
    "wallet": BASE_ENDPOINT + "wallet/info",
    "asset": BASE_ENDPOINT + "wallet/details",
    "orders": BASE_ENDPOINT + "wallet/orders"
}

class Ortak():
    def __init__(self, verbose=True):
        self.login_data = {}
        self.token = {}
        self.wallet = {}
        self.assets = {}
        self.orders = {}
        self.verbose = verbose
        self.logged_in = False

    def check_data(self, r):
        if r.status_code == 200:
            try:
                j = r.json()
                if j["status"] == "success":
                    return j
            except:
                pass
        return False

    def login(self):
        self.logged_in = False
        payload = {
            "phoneNumber": PHONE,
            "password": PASSWORD
        }
        if self.verbose:
            print("Sisteme giriş yapılıyor...")
        r = requests.post(endpoints["login"], json=payload)
        j = self.check_data(r)
        if j:
            self.login_data = j
            self.token = j["data"]["tokenInformation"]
            self.logged_in = True
            print("Giriş başarılı!")
            return j
        else:
            print("Giriş başarısız oldu!")

    def send_order(self, order_type, side, market, size, price=0.0):
        headers = {
            "Authorization": self.token["token"]
        }
        url = f"{endpoints['order']}"
        payload = {
            "side": side,
            "orderType": order_type,
            "market": market,
            "size": size
        }
        if order_type == "LIMIT" or order_type == "STOP":
            payload["price"] = price
        r = requests.post(url=url, json=payload, headers=headers)
        j = self.check_data(r)
        if j:
            return j
        return False

    # ORDERS

    def send_market_order(self, side, market, size):
        return self.send_order(order_type="MARKET", side=side, market=market, size=size)

    def send_limit_order(self, side, market, size, price):
        return self.send_order(order_type="LIMIT", side=side, market=market, size=size, price=price)

    def send_stop_order(self, side, market, size, price):
        return self.send_order(order_type="STOP", side=side, market=market, size=size, price=price)

    def delete_order(self, order_id):
        headers = {
            "Authorization": self.token["token"]
        }
        url = f"{endpoints['order']}/{order_id}"
        r = requests.delete(url=url, headers=headers)
        j = self.check_data(r)
        if j:
            return j
        return False

    # ALIAS
    def market_buy(self, market, size):
        return self.send_order(order_type="MARKET", side="BUY", market=market, size=size)

    def market_sell(self, market, size):
        return self.send_order(order_type="MARKET", side="SELL", market=market, size=size)

    def limit_buy(self, market, size, price):
        return self.send_limit_order(side="BUY", market=market, size=size, price=price)

    def limit_sell(self, market, size, price):
        return self.send_limit_order(side="SELL", market=market, size=size, price=price)

    def stop_buy(self, market, size, price):
        return self.send_stop_order(side="BUY", market=market, size=size, price=price)

    def stop_sell(self, market, size, price):
        return self.send_stop_order(side="SELL", market=market, size=size, price=price)

    def get_wallet_info(self, currency="TRY"):
        headers = {
            "Authorization": self.token["token"]
        }
        url = f"{endpoints['wallet']}?referenceCurrency={currency}"
        r = requests.get(url, headers=headers)
        j = self.check_data(r)
        if j:
            self.wallet = j["data"]
            return j

    def get_asset_info(self, currency="TRY"):
        headers = {
            "Authorization": self.token["token"]
        }
        url = f"{endpoints['asset']}?referenceCurrency={currency}"
        r = requests.get(url, headers=headers)
        j = self.check_data(r)
        if j:
            self.assets = j["data"]["assets"]
            return self.assets

    def get_orders(self, offset=0, limit=1, search="ALL"):
        headers = {
            "Authorization": self.token["token"]
        }
        url = f"{endpoints['orders']}?limit={limit}&offset={offset}&search={search}"
        r = requests.get(url, headers=headers)
        j = self.check_data(r)
        if j:
            return j

    def get_all_orders(self):
        offset = 0
        limit = 10
        d = []
        while True:
            o = self.get_orders(offset=offset, limit=limit)
            if o:
                vals = o["data"]["orders"]
                sz = len(vals)
                if sz > 0:
                    d.extend(vals)
                    offset += sz
                if sz == 0 or sz < limit:
                    break
            else:
                break
        self.orders = d
        return d

    def get_canceled_orders(self):
        o = self.get_all_orders()
        d = []
        for order in o:
            if order["status"] == "CANCELLED":
                d.append(order)
        return d

    def get_filled_orders(self):
        o = self.get_all_orders()
        d = []
        for order in o:
            if order["status"] == "MATCH":
                d.append(order)
        return d

    def get_pending_orders(self):
        o = self.get_all_orders()
        d = []
        for order in o:
            if order["status"] == "OPEN":
                d.append(order)
        return d

    def delete_pending_orders(self):
        o = self.get_pending_orders()
        for order in o:
            r = self.delete_order(order["id"])
            if r and self.verbose:
                print(f"Emir {order['id']} silindi...")

if __name__ == "__main__":
    ortak = Ortak()
    ortak.login()
    o = ortak.get_filled_orders()
    for i in o:
        print(i)
