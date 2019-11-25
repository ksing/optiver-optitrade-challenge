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

    def on_price_update(self, feedcode, bid_price, bid_volume, ask_price, ask_volume):
        # This is where you write code to react to price updates
        pass

    def on_trade_tick(self, feedcode, side, traded_price, traded_volume):
        # This is where you write code to react to price updates
        pass

    def on_trade_confirmation(self, position_sp, position_esx, feedcode, traded_price, traded_volume):
        # This is where you write code to react to price updates
        pass


if __name__ == "__main__":
    Autotrader().start_autotrader()
