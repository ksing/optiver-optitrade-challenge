import os
import select
import socket
from collections import defaultdict
from datetime import datetime

REMOTE_IP = "172.31.18.231"
UDP_ANY_IP = ""

IML_UDP_PORT_LOCAL = 7078
IML_UDP_PORT_REMOTE = 7001
IML_INIT_MESSAGE = "TYPE=SUBSCRIPTION_REQUEST"

EML_UDP_PORT_LOCAL = 8078
EML_UDP_PORT_REMOTE = 8001


# -------------------------------------
# Auto trader
# -------------------------------------
class BaseAutotrader:
    
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._set_up_eml()
        self._set_up_iml()
        self._positions = defaultdict(int)
        replay_file = os.path.join(
            os.getenv('HOME', os.path.expanduser('~')),
            f"{datetime.now().strftime('%Y-%m-%d')}-{self._username}_replay_file.replay"
        )
        if not os.path.isfile(replay_file):
            with open(replay_file, 'w+'):
                f.write('TradeTime|Feedcode|TradedPrice|TradedVolume')
        self._replay_file_handler = open(replay_file, 'r+')

    def __repr__(self):
        return f'{self.__class__.__name__}({self._username})'

    def _set_up_eml(self):
        # EML code (EML is execution market link)
        self._eml_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._eml_sock.bind((UDP_ANY_IP, EML_UDP_PORT_LOCAL))

    def _set_up_iml(self):
        # IML code (IML is information market link)
        self._iml_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._iml_sock.bind((UDP_ANY_IP, IML_UDP_PORT_LOCAL))

    def start_autotrader(self):
        self._subscribe()
        self._read_replay_file()
        self._event_listener()

    def _subscribe(self):
        self._iml_sock.sendto(IML_INIT_MESSAGE.encode(), (REMOTE_IP, IML_UDP_PORT_REMOTE))

    def _event_listener():
        """
        Wait for messages from the exchange and call handle_message on each of them.
        """
        while True:
            ready_socks,_,_ = select.select([self._iml_sock, self._eml_sock], [], [])
            for socket in ready_socks:
                data, addr = socket.recvfrom(1024)
                message = data.decode('utf-8')
                try:
                    self._handle_message(message)
                except Exception:
                    print(f"Invalid message received: {message}")

    def _read_replay_file(self):
        header = self._replay_file_handler.readline()
        for line in self._replay_file_handler:
            if line:
                trade_time, feedcode, traded_price, traded_volume = line.split('|')
                self._positions['feedcode'] += traded_volume
        
    def _write_replay_file(self, feedcode, traded_price, traded_volume):
        self._replay_file_handler.write(
            f"{datetime.now().strftime('%H:%M:%S')}|{feedcode}|{traded_price}|{traded_volume}\n"
        )

    def _update_position(self, feedcode, traded_volume):
        self._positions[feedcode] += traded_volume

    def _handle_message(self, message):
        message_components = message.split("|")

        if not message_components:
            print(f"Invalid message received: {message}")
            return

        dict_message = dict([msg.split('=') for msg in message_components])

        if dict_message['TYPE'] == "PRICE":
            print(
                "[PRICE] product: {FEEDCODE} bid: {BID_VOLUME}@{BID_PRICE} ask: {ASK_VOLUME}@{ASK_PRICE}"
                .format(**dict_message)
            )
            self.on_price_update(
                feedcode=dict_message['FEEDCODE'],
                bid_price=float(dict_message['BID_PRICE']),
                bid_volume=int(dict_message['BID_VOLUME']),
                ask_price=float(dict_message['ASK_PRICE']),
                ask_volume=int(dict_message['ASK_VOLUME'])
            )
        elif dict_message['TYPE'] == "TRADE":
            print(
                "[TRADE] product: {FEEDCODE} side: {SIDE} price: {PRICE} volume: {VOLUME}"
                .format(**dict_message)
            )
            self.on_trade_tick(
                feedcode=dict_message['FEEDCODE'],
                side=dict_message['SIDE'],
                traded_price=float(dict_message['PRICE']),
                traded_volume=int(dict_message['VOLUME']),
            )
        elif dict_message['type'] == "ORDER_ACK":
            if "ERROR" in dict_message:
                print(f"Order was rejected because of error {dict_message['ERROR']}.")
                return
            # This is only 0 if price is not there, and volume became 0 instead.
            # Possible cause: someone else got the trade instead of you.
            traded_price = float(dict_message.get('PRICE', 0))
            traded_volume = int(dict_message.get('TRADED_VOLUME', 0))
            if traded_price == 0 or traded_volume == 0:
                print(f"Unable to get trade on: {dict_message['FEEDCODE']}")
                return
            print(f"[ORDER_ACK] feedcode: {dict_message['FEEDCODE']}, price: {traded_price}, volume: {traded_volume}")

            self._update_position(feedcode=dict_message['FEEDCODE'], traded_volume=traded_volume)
            self._write_replay_file(
                feedcode=dict_message['FEEDCODE'],
                traded_price=traded_price,
                traded_volume=traded_volume
            )
            self.on_trade_confirmation(
                position_sp=self._positions.get('SP-FUTURE', 0),
                position_esx=self._positions.get('ESX-FUTURE', 0),
                feedcode=dict_message['FEEDCODE'],
                traded_price=traded_price,
                traded_volume=traded_volume
            )
        else:
            print(f"Message type not recognized: {message}")

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
        order_message = (
            f"TYPE=ORDER|USERNAME={self._username}|PASSWORD={self._password}|FEEDCODE={target_feedcode}|ACTION={action}"
            f"|PRICE={target_price}|VOLUME={volume}"
        )
        print(f"[SENDING ORDER] {order_message}")
        self._eml_sock.sendto(order_message.encode(), (REMOTE_IP, EML_UDP_PORT_REMOTE))

    def on_price_update(self, feedcode, bid_price, bid_volume, ask_price, ask_volume):
        raise NotImplementedError

    def on_trade_tick(self, feedcode, side, traded_price, traded_volume):
        raise NotImplementedError

    def on_trade_confirmation(self, position_sp, position_esx, feedcode, traded_price, traded_volume):
        raise NotImplementedError

