#!/usr/bin/env python3.6

from base_autotrader_client import BaseAutotrader

USERNAME = "TeamXX"  # Change this to team name from user credentials
PASSWORD = "TeamPassword"  # Change this to team password from user credentials


class Autotrader(BaseAutotrader):
    """
    This is the only class you need to change - in particular, on_* methods. You may initialize new instance variables
     in the __init__ method, if you like.
    * DO NOT DELETE ANY METHOD *
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

    def send_order(self, target_feedcode: str, action: str, target_price: float, target_volume: int):
        """
        Send an order to the exchange.
        Example:
        If you want to buy  100 SP-FUTURES at a price of 3000:
        - send_order("SP-FUTURE", "BUY", 3000, 100)

        Args:
            target_feedcode (str): The feedcode, either "SP-FUTURE" or "ESX-FUTURE"
            action (str): "BUY" or "SELL"
            target_price (float): Price you want to trade at
            target_volume (int): Volume you want to trade at. Please start with 10 and go from there. Don't go crazy!
        Returns:
            Nothing

        """
        self._send_order(target_feedcode, action, target_price, target_volume)

    def on_price_update(self, feedcode: str, bid_price: float, bid_volume: int, ask_price: float, ask_volume: int):
        """This is where you write code to react to price updates. Due to a trade tick or someone inserting a quote,
         there is a change in the order book. Here, you receive the current state of the most competitive bid and ask -
         also known as top of the book (TOB) update. You may to react to those TOB updates.
        """
        pass

    def on_trade_tick(self, feedcode: str, side: str, traded_price: float, traded_volume: int):
        """This is where you write code to react to exchange trade ticks. There is a trade on an instrument at the
         exchange - it does not necessarily belong to you. You may to react to that information.
        """
        pass

    def on_order_success(self, feedcode: str, traded_price: float, traded_volume: int):
        """This is where you write code to react to a successful order confirmation. Your order was successful,
         exchange confirms the traded price and volume - may not be same as your order volum- to you in a message.        
        """
        pass

    def on_order_failure(self, feedcode: str):
        """This is where you write code to react - if you want - to failure of your order. You did not get any trade.
         Perhaps you were too late/slow, or the target price you sent was not available. You can also react to this
         information.
        """
        pass


if __name__ == "__main__":
    autotrader = Autotrader()
    autotrader.start()
