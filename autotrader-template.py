#!/usr/bin/env python3.6

from base_autotrader_client import BaseAutotrader

USERNAME = "TeamXX"  # Change this to team name from user credentials
PASSWORD = "TeamPassword"  # Change this to team password from user credentials


class Autotrader(BaseAutotrader):
    """
    This is the only class you need to change - in particular, on_* methods. You may initialize new instance variables
     in the __init__ method, if you like.
    """

    def __init__(self):
        super().__init__(username=USERNAME, password=PASSWORD)

    def get_position_sp(self):
        """You can get your current position in S&P"""
        return self.position_sp

    def get_position_esx(self):
        """You can get your current position in ESX"""
        return self.position_esx

    def start(self):
        self._start()

    def send_order(self, target_feedcode, action, target_price, volume):
        """
        Send an order to the exchange.

        :param target_feedcode: The feedcode, either "SP-FUTURE" or "ESX-FUTURE"
        :param action: "BUY" or "SELL"
        :param target_price: Price you want to trade at
        :param volume: Volume you want to trade at. Please start with 10 and go from there. Don't go crazy!
        :return:

        Example:
        If you want to buy  100 SP-FUTURES at a price of 3000:
        - send_order("SP-FUTURE", "BUY", 3000, 100)
        """
        self._send_order(target_feedcode, action, target_price, volume)

    def on_price_update(self, feedcode: str, bid_price: float, bid_volume: int, ask_price: float, ask_volume: int):
        """This is where you write code to react to price updates"""
        pass

    def on_trade_tick(self, feedcode: str, side: str, traded_price: float, traded_volume: int):
        """This is where you write code to react to exchange trade ticks"""
        pass

    def on_order_success(self, feedcode: str, traded_price: float, traded_volume: int):
        """This is where you write code to react to a successful order"""
        pass

    def on_order_failure(self, feedcode: str):
        """This is where you write code to react - if you want - to failure of your order"""
        pass


if __name__ == "__main__":
    autotrader = Autotrader()
    autotrader.start()
