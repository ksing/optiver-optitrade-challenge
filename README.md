# Optiver OptiTrade Challenge

Look at your positions here: http://18.197.147.155:5006/optitrade

During this challenge, you will be listening to an exchange, analyse its data and then
develop an automated trading system.

You will be trading on a virtual exchange that we setup. The exchange is broadcasting
prices and trades on two famous stock market indices: S&P500 (SP) and Eurostoxx (ESX).
That means you see how the price changes over time for those indices, and what trades
from the outside world are made (this is simulated). Your goal is to implement a clever
strategies to (hopefully) make money!


## The Exchange

The system is composed by:

  * ```PRICE``` messages:

    This tells you the current price and volume for an *instrument* (SP-FUTURE or ESX-FUTURE).
    They are always the new top of the order book. There is only one level in this order book, and this message describes it.
   
  * ```TRADE``` messages:

    This tells you simulated trades on the exchange (only), at which price and for how much volume.

### Measure Your Performance

Trading is one thing, but of course you also want to know how much money you have made or lost, and how much risk you're taking.
For that, it might be smart to track your own profit and loss (PnL), alongside your positions (which is your risk).

You can also look at your official PnL [here](http://18.197.147.155:5006/optitrade)


### Bankruptcy

You start with **20,000 EUR**. If you end up losing all of it, you go bankrupt!
When this happens, your team is out of the game for **5 minutes**. Use this time
wisely to rethink your strategy and feel free to ask the Optiverians for help!

After these 5 minutes, you'll start again with 20,000 euros.

**All of you are trading on the same exchange, which means that you will compete for the same opportunities...**

**Last thing: every trade will impact your position &mdash; keep an eye on it to manage your risk exposure!**

## Protocol specification
The communication from and towards the exchange is done via a text-based, ASCII, protocol.

Every message is specific to an *instrument*, identified by a *feedcode* (i.e. `SP-FUTURE` or `ESX-FUTURE`).
Every message is composed by several fields separated by `|`.

**Important**: Send ```TYPE=SUBSCRIPTION_REQUEST``` to ```ip: 188.166.115.7, port: 7001``` as the very first message in order to subscribe to the data feed.

### Info protocol specifications

The exchange broadcasts two messages (via UDP):

  * Price message: this tells you the current price and volume for an *instrument*
  * Trade message: this tells you trades on the exchange, at which price and for how much volume


#### Price message fields

| Field | Description | Value
|------|-------------|-----------------
| TYPE | The type of message | Fixed value: `PRICE` |
| FEEDCODE | The instrument's feedcode | String |
| BID_PRICE | The price at which you can sell | Float |
| BID_VOLUME | The volume available on the bid | Int |
| ASK_PRICE | The price at which you can buy |Float  |
| ASK_VOLUME | The volume available on the offer | Int |

Example: ```TYPE=PRICE|FEEDCODE=FOOBAR|BID_PRICE=10.0|BID_VOLUME=100|ASK_PRICE=11.0|ASK_VOLUME=20```


#### Trade message fields

| Field | Description | Value
--------|------------|----------------
| TYPE | The type of message | Fixed value: `TRADE` |
| FEEDCODE | The instrument's feedcode | String |
| SIDE | The side of the trade | String, `BID` or `ASK` |
| PRICE | The traded price | Float |
| VOLUME | The traded volume| Int |

Example: ```TYPE=TRADE|FEEDCODE=FOOBAR|SIDE=BID|PRICE=22.0|VOLUME=100```


### Execution protocol specification
In order to trade, you need to send an order to the exchange. Every order is acknowledged by the exchange.

#### Order message fields

| Field | Description | Value
-------|--------------|---------------
| TYPE | The type of message | Fixed value: `ORDER` |
| USERNAME | The unique username identifying your team. Can be found on the credential section  of the handout. | String |
| PASSWORD| The password associated with your username. Can be found on the credential section  of the handout. | String |
| FEEDCODE | The instrument's feedcode | String |
| ACTION | The order action | String, `BUY` or `SELL` |
| PRICE | The order price | Float |
| VOLUME | The order volume | Int |

Example: ```TYPE=ORDER|USERNAME=Optiver|PASSWORD=My_Password|FEEDCODE=FOOBAR|ACTION=BUY|PRICE=22.0|VOLUME=100```


#### Order ack message fields

| Field | Description | Value
-------|-------------|----------------
| TYPE | The type of message | Fixed value: `ORDER_ACK` |
| FEEDCODE | The instrument's feedcode | String |
| PRICE | The traded price | Float, optional, only set if the order traded |
| TRADED_VOLUME | The traded volume, positive if you bought, negative if you sold | Int, optional, only set if the order has been successfully processed |
| ERROR | The errord description | If something went wrong, this field is set, otherwise it is empty | String, optional, only set on error |

Examples:
- ```TYPE=ORDER_ACK|FEEDCODE=FOOBAR|PRICE=22.0|TRADED_VOLUME=100```
- ```TYPE=ORDER_ACK|FEEDCODE=FOOBAR|TRADED_VOLUME=0```
- ```TYPE=ORDER_ACK|ERROR=Invalid login credentials supplied```