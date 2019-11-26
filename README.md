# Optiver OptiTrade Challenge

Look at your positions here: http://18.185.112.43:5006/optitrade

During this challenge, you will be listening to an exchange, analyse its data and then
develop an automated trading system.

You will be trading on a virtual exchange that we setup. The exchange is broadcasting
prices and trades on two famous stock market indices: S&P500 (SP) and Eurostoxx (ESX).
That means you see how the price changes over time for those indices, and what trades
from the outside world are made (this is simulated). Your goal is to implement a clever
strategies to (hopefully) make money!


### The Exchange

The system is composed by:

  * ```PRICE``` messages:

    This tells you the current price and volume for an *instrument* (SP-FUTURE or ESX-FUTURE).
    They are always the new top of the order book. There is only one level in this order book, and this message describes it.
   
  * ```TRADE``` messages:

    This tells you simulated trades on the exchange (only), at which price and for how much volume.

### Manage Your Risk

Sending orders is one thing, but you also want to know how much risk you're taking **&mdash; every trade will impact your position**. We already provide you with basic functionality to look at your positions, so think about how you can use that to control your risk and avoid going bankrupt. This is important!


### Bankruptcy

You start with **20,000 EUR**. If you end up losing all of it, you go bankrupt!
When this happens, your team is out of the game for **5 minutes**. Use this time
wisely to rethink your strategy and feel free to ask the Optiverians for help!

After these 5 minutes, you'll start again with 20,000 euros.

**Last thing: All of you are trading on the same exchange, which means that you will compete for the same opportunities...**
