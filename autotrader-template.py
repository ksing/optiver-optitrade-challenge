import socket
import select

REMOTE_IP = "178.62.36.224"
UDP_ANY_IP = ""

USERNAME = "optiver-python-template"
PASSWORD = "password-goes-here"

# -------------------------------------
# EML code (EML is execution market link)
# -------------------------------------

EML_UDP_PORT_LOCAL = 8078
EML_UDP_PORT_REMOTE = 8001

eml_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
eml_sock.bind((UDP_ANY_IP, EML_UDP_PORT_LOCAL))

# -------------------------------------
# IML code (IML is information market link)
# -------------------------------------

IML_UDP_PORT_LOCAL = 7078
IML_UDP_PORT_REMOTE = 7001
IML_INIT_MESSAGE = "TYPE=SUBSCRIPTION_REQUEST"

iml_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
iml_sock.bind((UDP_ANY_IP, IML_UDP_PORT_LOCAL))


# -------------------------------------
# Auto trader
# -------------------------------------
def start_autotrader():
    subscribe()
    event_listener()

def subscribe():
    iml_sock.sendto(IML_INIT_MESSAGE.encode(), (REMOTE_IP, IML_UDP_PORT_REMOTE))

def event_listener():
    """
    Wait for messages from the exchange and
    call handle_message on each of them.
    """
    while True:
        ready_socks,_,_ = select.select([iml_sock, eml_sock], [], [])
        for socket in ready_socks:
            data, addr = socket.recvfrom(1024)
            message = data.decode('utf-8')
            handle_message(message)

def handle_message(message):
    comps = message.split("|")

    if len(comps) == 0:
        print("Invalid message received: {msg}".format(msg=message))
        return

    type = comps[0]

    if type == "TYPE=PRICE":

        feedcode = comps[1].split("=")[1]
        bid_price = float(comps[2].split("=")[1])
        bid_volume = int(comps[3].split("=")[1])
        ask_price = float(comps[4].split("=")[1])
        ask_volume = int(comps[5].split("=")[1])

        print("PRICE: product: {} bid: {}@{} ask: {}@{}".format(feedcode, bid_volume, bid_price, ask_volume, ask_price))

    if type == "TYPE=TRADE":

        feedcode = comps[1].split("=")[1]
        side = comps[2].split("=")[1]
        traded_price = float(comps[3].split("=")[1])
        traded_volume = int(comps[4].split("=")[1])

        print("TRADE: product: {} side: {} price: {} volume: {}".format(feedcode, side, traded_price, traded_volume))

    if type == "TYPE=ORDER_ACK":

        if comps[1].split("=")[0] == "ERROR":
            print("Order was rejected because of error {err}.".format(err=comps[1].split("=")[1]))
            return

        feedcode = comps[1].split("=")[1]
        traded_price = float(comps[2].split("=")[1])

        # This is only 0 if price is not there, and volume became 0 instead
        if traded_price == 0:
            print("Unable to get trade on: {fc}".format(fc=feedcode))
            return

        traded_volume = int(comps[3].split("=")[1])

        print("ORDER_ACK: feedcode: {fc}, price: {pr}, volume: {vol}".format(
            fc=feedcode, pr=traded_price, vol=traded_volume))

def send_order(target_feedcode, action, target_price, volume):
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
    order_message = "TYPE=ORDER|USERNAME={user}|PASSWORD={pw}|FEEDCODE={fc}|ACTION={ac}|PRICE={pr}|VOLUME={vol}".format(
        user=USERNAME, pw=PASSWORD, fc=target_feedcode, ac=action, pr=target_price, vol=volume)
    print('sending order: '.format(order_message))
    eml_sock.sendto(order_message.encode(), (REMOTE_IP, EML_UDP_PORT_REMOTE))

# -------------------------------------
# Main
# -------------------------------------

if __name__ == "__main__":
    start_autotrader()
