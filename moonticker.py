
import rumps
import requests
from ConfigParser import SafeConfigParser
import sys

is_py2app = hasattr(sys, "frozen")
pem_path = "lib/python2.7/certifi/cacert.pem" if is_py2app else None 

class CEX():
    title = "CEX"
    menu_title="CEX.io"

    def __init__(self):
        self.api_endpoint = 'https://cex.io/api'
        self.products = {
            'ETH': {
                'USD': '/ticker/ETH/USD'
            },
            'BTC': {
                'USD': '/ticker/BTC/USD'
            }
        }

    def getTick(self, product='ETH', conversion='USD'):
        if (product in self.products and conversion in self.products[product]):
            r = requests.get(self.api_endpoint + self.products[product][conversion], verify=pem_path).json()
            return {
                "bid": float(r['bid']),
                "ask": float(r['ask']),
                "last": float(r['last'])
            }
        else:
            return  {
                "bid": "-",
                "ask": "-",
                "last": "-"
            }


class Kraken():
    title = "Kraken"
    menu_title="Kraken"

    def __init__(self):
        self.api_endpoint = 'https://api.kraken.com/0'
        self.products = {
            'ETH': {
                'USD': '/public/Ticker?pair=ETHUSD'
            },
            'BTC': {
                'USD': '/public/Ticker?pair=XBTUSD'
            }
        }

    def getTick(self, product='ETH', conversion='USD'):
        if (product in self.products and conversion in self.products[product]):
            r = requests.get(self.api_endpoint + self.products[product][conversion], verify=pem_path).json()
            resultName = 'XETHZUSD' if product == 'ETH' else 'XXBTZUSD'
            return {
                "bid": float(r['result'][resultName]['b'][0]),
                "ask": float(r['result'][resultName]['a'][0]),
                "last": float(r['result'][resultName]['c'][0])
            }
        else:
            return  {
                "bid": "-",
                "ask": "-",
                "last": "-"
            }

class Gemini():
    title = "Gemini"
    menu_title="Gemini"

    def __init__(self):
        self.api_endpoint = 'https://api.gemini.com/v1'
        self.products = {
            'ETH': {
                'USD': '/pubticker/ethusd'
            },
            'BTC': {
                'USD': '/pubticker/btcusd'
            }
        }

    def getTick(self, product='ETH', conversion='USD'):
        if (product in self.products and conversion in self.products[product]):
            r = requests.get(self.api_endpoint + self.products[product][conversion], verify=pem_path).json()
            return {
                "bid": float(r['bid']),
                "ask": float(r['ask']),
                "last": float(r['last'])
            }
        else:
            return  {
                "bid": "-",
                "ask": "-",
                "last": "-"
            }

class GDAX():
    title = "GDAX"
    menu_title="GDAX (Coinbase)"

    def __init__(self):
        self.api_endpoint = "https://api.gdax.com"
        self.products = {
            'ETH': {
                'USD': '/products/ETH-USD/ticker'
            },
            'BTC': {
                'USD': '/products/BTC-USD/ticker'
            }
        }

    def getTick(self, product='ETH', conversion='USD'):
        if (product in self.products and conversion in self.products[product]):
            r = requests.get(self.api_endpoint + self.products[product][conversion], verify=pem_path).json()
            return {
                "bid": float(r['bid']),
                "ask": float(r['ask']),
                "last": float(r['price'])
            }
        else:
            return  {
                "bid": "-",
                "ask": "-",
                "last": "-"
            }


class MoonTickerApp(rumps.App):

    def __init__(self, name):
        rumps.App.__init__(self, name)
        self.exchanges = set()
        self.currencies = set()
        
        self.gemini = Gemini()
        self.gdax = GDAX()
        self.kraken = Kraken()
        self.cex = CEX()

        self.config = SafeConfigParser()
        self.config.read ('settings.ini')
        if (not self.config.has_option('preferences', 'initialized')):
            # no self.config yet
            self.config.add_section('preferences')
            self.config.set('preferences', 'initialized', 'True')
            self.config.set('preferences', 'use_price', 'True')
            self.config.set('preferences', 'use_ask', 'False')
            self.config.set('preferences', 'use_bid', 'False')
            self.config.set('preferences', 'exchanges', 'Gemini')
            self.config.set('preferences', 'currencies', 'ETH')
            self.config.set('preferences', 'display_progress', 'False')
            self.config.set('preferences', 'currency_sign', '')
            self.config.set('preferences', 'timer_interval', '5')
            with open('settings.ini', 'w') as f:
                self.config.write(f)

        # defaults
        self.timer_interval = self.config.getint('preferences', 'timer_interval')
        self.use_price = self.config.getboolean('preferences', 'use_price')
        self.use_ask = self.config.getboolean('preferences', 'use_ask')
        self.use_bid = self.config.getboolean('preferences', 'use_bid')
        exchange_list = self.config.get('preferences', 'exchanges').split(',')
        for exchange in exchange_list:
            if (exchange == self.gemini.title):
                self.exchanges.add(self.gemini)
            elif (exchange == self.gdax.title):
                self.exchanges.add(self.gdax)
            elif (exchange == self.kraken.title):
                self.exchanges.add(self.kraken)
            elif (exchange == self.cex.title):
                self.exchanges.add(self.cex)
        currency_list = self.config.get('preferences', 'currencies').split(',')
        for currency in currency_list:
            self.currencies.add(currency)
        self.count = 0
        self.display_progress = self.config.getboolean('preferences', 'display_progress')
        self.currency_sign = self.config.get('preferences', 'currency_sign')

        # Alerts
        self.alerts = {}

        # Menus
        preferences_menu = rumps.MenuItem("Preferences")
        
        interval_menu = rumps.MenuItem("interval")
        for i in ["1s", "5s", "10s", "30s", "60s"]:
            interval_menu.add(i)
        interval_menu[str(self.timer_interval)+"s"].state = 1
        preferences_menu.add(interval_menu)
        
        display_menu = rumps.MenuItem("display")
        for d in ["ask", "bid", "price", "show spinner"]:
            display_menu.add(d)
        if self.use_price: 
            display_menu["price"].state = 1
        if self.use_ask:
            display_menu["ask"].state = 1
        if self.use_bid:
            display_menu["bid"].state = 1
        if self.display_progress:
            display_menu["show spinner"].state = 1
        preferences_menu.add(display_menu)
        
        exchanges_menu = rumps.MenuItem("Exchanges")
        for e in [self.gdax.menu_title, self.gemini.menu_title, 
        self.kraken.menu_title, self.cex.menu_title]:
            exchanges_menu.add(e)
        for exchange in self.exchanges:
            exchanges_menu[exchange.menu_title].state = 1
        
        currencies_menu = rumps.MenuItem("Currencies")
        for c in ["Ethereum (ETH)", "Bitcoin (BTC)"]:
            currencies_menu.add(c)
        # todo: make currencies a class
        if ("ETH" in self.currencies):
            currencies_menu["Ethereum (ETH)"].state = 1
        if ("BTC" in self.currencies):
            currencies_menu["Bitcoin (BTC)"].state = 1

        self.menu = [preferences_menu, exchanges_menu, currencies_menu]

        self.timer = rumps.Timer(self.update_title, self.timer_interval)
        self.timer.start()

    def save_config(self):
        self.config.set('preferences', 'use_price', str(self.use_price))
        self.config.set('preferences', 'use_ask', str(self.use_ask))
        self.config.set('preferences', 'use_bid', str(self.use_bid))
        exchange_list = []
        for exchange in self.exchanges:
            exchange_list.append(exchange.title)
        self.config.set('preferences', 'exchanges', str.join(',', exchange_list))
        self.config.set('preferences', 'currencies', str.join(',', self.currencies))
        self.config.set('preferences', 'display_progress', str(self.display_progress))
        self.config.set('preferences', 'currency_sign', str(self.currency_sign))
        self.config.set('preferences', 'timer_interval', str(self.timer_interval))
        with open('settings.ini', 'w') as f:
            self.config.write(f)

    @rumps.clicked("Exchanges", "Gemini")
    def set_gemini(self, sender):
        sender.state = not sender.state
        self.exchanges.add(self.gemini) if sender.state else self.exchanges.remove(self.gemini)
        self.save_config()
        self.update_title()
        

    @rumps.clicked("Exchanges", "GDAX (Coinbase)")
    def set_coinbase(self, sender):
        sender.state = not sender.state
        self.exchanges.add(self.gdax) if sender.state else self.exchanges.remove(self.gdax)
        self.save_config()
        self.update_title()

    @rumps.clicked("Exchanges", "Kraken")
    def set_kraken(self, sender):
        sender.state = not sender.state
        self.exchanges.add(self.kraken) if sender.state else self.exchanges.remove(self.kraken)
        self.save_config()
        self.update_title()
        
    @rumps.clicked("Exchanges", "CEX.io")
    def set_cex(self, sender):
        sender.state = not sender.state
        self.exchanges.add(self.cex) if sender.state else self.exchanges.remove(self.cex)
        self.save_config()
        self.update_title()

    @rumps.clicked("Currencies", "Ethereum (ETH)")
    def set_eth(self, sender):
        sender.state = not sender.state
        self.currencies.add('ETH') if (sender.state) else self.currencies.remove('ETH')
        self.save_config()
        self.update_title()
        

    @rumps.clicked("Currencies", "Bitcoin (BTC)")
    def set_btc(self, sender):
        sender.state = not sender.state
        self.currencies.add('BTC') if (sender.state) else self.currencies.remove('BTC')
        self.save_config()
        self.update_title()
        
    def update_title(self, _=None):
        # coinmarketcap = Market()
        title = ""
        show_alert = False
        alert_message = ""
        for exchange in self.exchanges:
            exchange_title = ""
            for currency in self.currencies:
                tick = exchange.getTick(product=currency, conversion='USD')
                price = tick["last"]
                bid = tick["bid"]
                ask = tick["ask"]
                if (self.use_price and not self.use_bid and not self.use_ask):
                    exchange_title += "{}: {}{:.{prec}f}".format(currency, self.currency_sign, price, prec=2) + ", "
                elif (not self.use_price and self.use_bid and not self.use_ask):
                    exchange_title += "{}: {}{:.{prec}f}".format(currency, self.currency_sign, bid, prec=2) + ", "
                elif (not self.use_price and not self.use_bid and self.use_ask):
                    exchange_title += "{}: {}{:.{prec}f}".format(currency, self.currency_sign, ask, prec=2) + ", "
                elif (self.use_price and self.use_bid and not self.use_ask):
                    exchange_title += "{}: {}{:.{prec}f}|{:.{prec}f}".format(currency, self.currency_sign, bid, price, prec=2) + ", "
                elif (self.use_price and not self.use_bid and self.use_ask):
                    exchange_title += "{}: {}{:.{prec}f}|{:.{prec}f}".format(currency, self.currency_sign, ask, price, prec=2) + ", "
                elif (not self.use_price and self.use_bid and self.use_ask):
                    exchange_title += "{}: {}{:.{prec}f}|{:.{prec}f}".format(currency, self.currency_sign, ask, bid, prec=2) + ", "
                elif (self.use_price and self.use_bid and self.use_ask):
                    exchange_title += "{}: {}{:.{prec}f}|{:.{prec}f}|{:.{prec}f}".format(currency, self.currency_sign, ask, bid, price, prec=2) + ", "
                
                conversion = "USD" #temp
                if (currency in self.alerts and conversion in self.alerts[currency]):
                    currency_alerts = self.alerts[currency][conversion]
                    if ('high' in currency_alerts and price > currency_alerts['high']):
                        show_alert = True
                        alert_message += "\n" + currency + " is higher than " + str(currency_alerts['high']) + " on " + exchange.title
                        del self.alerts[currency][conversion]['high']
                    if ('low' in currency_alerts and price < currency_alerts['low']):
                        show_alert = True
                        alert_message += "\n" + currency + " is lower than " + str(currency_alerts['low']) + " on " + exchange.title
                        del self.alerts[currency][conversion]['low']
                
            if exchange_title and len(exchange_title) > 2:
                title += exchange_title[:-2] if (len(self.exchanges) == 1) else exchange.title + " [" + exchange_title[:-2] + "] "

        if (title):
            self.title = title
            self.count+= 1
            if (self.display_progress):
                self.title += " " + self.get_progress()

        if show_alert:
            rumps.alert(title="Moon Alert", message=alert_message)

    @rumps.clicked("Preferences", "interval", "1s")
    def set_interval_1(self, sender):
        for key in self.menu['Preferences']['interval']:
            menu = self.menu['Preferences']['interval'][key]
            menu.state = 0; # turn all other options OFF
        sender.state = 1; # set this option to ON
        self.timer.stop()
        self.timer.interval = 1
        self.timer.start()
        self.timer_interval = 1
        self.save_config()

    @rumps.clicked("Preferences", "interval", "5s")
    def set_interval_5(self, sender):
        for key in self.menu['Preferences']['interval']:
            menu = self.menu['Preferences']['interval'][key]
            menu.state = 0; # turn all other options OFF
        sender.state = 1; # set this option to ON
        self.timer.stop()
        self.timer.interval = 5
        self.timer.start()
        self.timer_interval = 5
        self.save_config()

    @rumps.clicked("Preferences", "interval", "10s")
    def set_interval_10(self, sender):
        for key in self.menu['Preferences']['interval']:
            menu = self.menu['Preferences']['interval'][key]
            menu.state = 0; # turn all other options OFF
        sender.state = 1; # set this option to ON
        self.timer.stop()
        self.timer.interval = 10
        self.timer.start()
        self.timer_interval = 10
        self.save_config()

    @rumps.clicked("Preferences", "interval", "30s")
    def set_interval_30(self, sender):
        for key in self.menu['Preferences']['interval']:
            menu = self.menu['Preferences']['interval'][key]
            menu.state = 0; # turn all other options OFF
        sender.state = 1; # set this option to ON
        self.timer.stop()
        self.timer.interval = 30
        self.timer.start()
        self.timer_interval = 30
        self.save_config()

    @rumps.clicked("Preferences", "interval", "60s")
    def set_interval_60(self, sender):
        for key in self.menu['Preferences']['interval']:
            menu = self.menu['Preferences']['interval'][key]
            menu.state = 0; # turn all other options OFF
        sender.state = 1; # set this option to ON
        self.timer.stop()
        self.timer.interval = 60
        self.timer.start()
        self.timer_interval = 60
        self.save_config()

    @rumps.clicked("Preferences", "display", "price")
    def set_price_pref(self, sender):
        sender.state = not sender.state
        self.use_price = sender.state
        self.save_config()

    @rumps.clicked("Preferences", "display", "ask")
    def set_ask_pref(self, sender):
        sender.state = not sender.state
        self.use_ask = sender.state
        self.save_config()

    @rumps.clicked("Preferences", "display", "bid")
    def set_bid_pref(self, sender):
        sender.state = not sender.state
        self.use_bid = sender.state
        self.save_config()

    @rumps.clicked("Preferences", "display", "show spinner")
    def set_display_progress(self, sender):
        sender.state = not sender.state
        self.display_progress = sender.state
        self.save_config()

    @rumps.clicked("Preferences", "display", "set currency symbol")
    def set_currency_symbol(self, sender):
        window = rumps.Window()
        window.title = 'Set currency symbol'
        window.message = "Enter a symbol you wish to use for currency (e.g. $)"
        window.default_text = self.currency_sign
        response = window.run()
        self.currency_sign = response.text
        self.save_config()

    @rumps.clicked("Alerts", "clear alerts")
    def clear_alerts(self, sender):
        self.alerts = {}
        self.save_config()

    @rumps.clicked("Alerts", "ETH", "set high alert")
    def set_high_alert_eth(self, sender):
        self.set_alert(product="ETH", conversion="USD", mode="high")

    @rumps.clicked("Alerts", "ETH", "set low alert")
    def set_low_alert_eth(self, sender):
        self.set_alert(product="ETH", conversion="USD", mode="low")

    @rumps.clicked("Alerts", "BTC", "set high alert")
    def set_high_alert_btc(self, sender):
        self.set_alert(product="BTC", conversion="USD", mode="high")

    @rumps.clicked("Alerts", "BTC", "set low alert")
    def set_low_alert_btc(self, sender):
        self.set_alert(product="BTC", conversion="USD", mode="low")

    def set_alert(self, product="ETH", conversion="USD", mode='high'):
        window = rumps.Window()
        window.title = 'Set alert for when {} goes {} given amount (must be a valid number, do not include currency symbols)'.format(product, 'above' if mode == 'high' else 'below')
        response = window.run()
        if (not product in self.alerts):
            self.alerts[product] = {}
        if (not conversion in self.alerts[product]):
            self.alerts[product][conversion] = {}
        self.alerts[product][conversion][mode] = float(response.text)
        self.save_config()

    @rumps.clicked("About")
    def show_about_window(self, sender):
        rumps.alert("MoonTicker", "Source code: https://github.com/skxu/ \n\nBuy me a boba:\n\nETH:\n0x87e55aEaeF9D884673f50Dc673adD96Ca7e5BbF9\n\nBTC:\n377P7NPChAffZN6jMLanogesAsR3d7STxA")

    def get_progress(self):
        li = ["|", "/", "-", "\\"]
        return li[self.count%len(li)]


if __name__ == "__main__":
    MoonTickerApp("eth: loading...").run()