import os
import select
import socket
from collections import defaultdict
from datetime import datetime

REMOTE_IP = "172.31.18.231"
UDP_ANY_IP = ""

IML_UDP_PORT_LOCAL = 7078
IML_UDP_PORT_REMOTE = 7001

EML_UDP_PORT_LOCAL = 8078
EML_UDP_PORT_REMOTE = 8001


class BaseAutotrader:
    """
    DO NOT CHANGE THIS CODE!!

    This code makes the auto-trader work. It connects to our virtual exchange and facilitates trading. You can look at
    the code to see how it works, and feel free to ask questions. But this code is not meant for you to change.
    """

    def __init__(self, username: str, password: str):
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
            with open(replay_file, 'w+') as f:
                f.write('TradeTime|Feedcode|TradedPrice|TradedVolume')

        self._replay_file_handler = open(replay_file, 'r+')

    def __repr__(self):
        return f'{self.__class__.__name__}({self._username})'

    @property
    def position_sp(self):
        """You can get your position in S&P with simply reading self.position_sp variable - not as a method"""
        return self._positions.get('SP-FUTURE', 0)

    @property
    def position_esx(self):
        """You can get your position in ESX with simply reading self.position_esx variable"""
        return self._positions.get('ESX-FUTURE', 0)

    def _set_up_eml(self):
        """EML code (EML is execution market link)"""
        self._eml_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._eml_sock.bind((UDP_ANY_IP, EML_UDP_PORT_LOCAL))

    def _set_up_iml(self):
        """IML code (IML is information market link)"""
        self._iml_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._iml_sock.bind((UDP_ANY_IP, IML_UDP_PORT_LOCAL))

    def _start(self):
        self._iml_subscribe()
        self._read_replay_file()
        self._event_listener()

    def _iml_subscribe(self):
        iml_init_message = "TYPE=SUBSCRIPTION_REQUEST"
        self._iml_sock.sendto(iml_init_message.encode(), (REMOTE_IP, IML_UDP_PORT_REMOTE))

    def _event_listener(self):
        """Wait for messages from the exchange and call handle_message on each of them."""
        while True:
            ready_socks, _, _ = select.select([self._iml_sock, self._eml_sock], [], [])
            for sock in ready_socks:
                data, addr = sock.recvfrom(1024)
                message = data.decode('utf-8')
                try:
                    self._handle_message(message)
                except (KeyError, ValueError):
                    print(f"Invalid message received: {message}")
                except Exception as e:
                    print(f"Error: {e}")

    def _read_replay_file(self):
        _ = self._replay_file_handler.readline()  # Skip the header line
        for line in self._replay_file_handler:
            if line:
                trade_time, feedcode, traded_price, traded_volume = line.split('|')
                self._positions['feedcode'] += traded_volume

    def _write_replay_file(self, feedcode: str, traded_price: float, traded_volume: int):
        self._replay_file_handler.write(
            f"{datetime.now().strftime('%H:%M:%S')}|{feedcode}|{traded_price}|{traded_volume}\n"
        )

    def _update_position(self, feedcode: str, traded_volume: int):
        self._positions[feedcode] += traded_volume

    def _handle_message(self, message: str):
        message_components = message.split("|")

        if not message_components:
            print(f"Invalid message received: {message}")
            return

        dict_message = dict([msg.split('=') for msg in message_components])

        if dict_message['TYPE'] == "PRICE":
            self._handle_price_message(dict_message)
        elif dict_message['TYPE'] == "TRADE":
            self._handle_trade_message(dict_message)
        elif dict_message['TYPE'] == "ORDER_ACK":
            self._handle_order_ack(dict_message)
        else:
            print(f"Message type not recognized: {message}")

    def _handle_price_message(self, dict_message: dict):
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

    def _handle_trade_message(self, dict_message: dict):
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

    def _handle_order_ack(self, dict_message: dict):
        if "ERROR" in dict_message:
            print(f"Order was rejected because of error {dict_message['ERROR']}.")
            return

        # This is only 0 if price is not there, and volume became 0 instead.
        # Possible cause: someone else got the trade instead of you.
        traded_price = float(dict_message.get('PRICE', 0))
        traded_volume = int(dict_message.get('TRADED_VOLUME', 0))
        if traded_price == 0 or traded_volume == 0:
            print(f"Unable to get trade on: {dict_message['FEEDCODE']}")
            self.on_order_failure(dict_message['FEEDCODE'])
        else:
            print(
                f"[ORDER_ACK] feedcode: {dict_message['FEEDCODE']}, price: {traded_price}, volume: {traded_volume}")

            self._update_position(feedcode=dict_message['FEEDCODE'], traded_volume=traded_volume)
            self._write_replay_file(
                feedcode=dict_message['FEEDCODE'],
                traded_price=traded_price,
                traded_volume=traded_volume
            )
            self.on_order_success(
                feedcode=dict_message['FEEDCODE'],
                traded_price=traded_price,
                traded_volume=traded_volume
            )

    def _send_order(self, target_feedcode, action, target_price, volume):
        order_message = (
            f"TYPE=ORDER|USERNAME={self._username}|PASSWORD={self._password}|FEEDCODE={target_feedcode}|ACTION={action}"
            f"|PRICE={target_price}|VOLUME={int(volume)}"
        )
        print(f"[SENDING ORDER] {order_message}")
        self._eml_sock.sendto(order_message.encode(), (REMOTE_IP, EML_UDP_PORT_REMOTE))

    def on_price_update(self, feedcode, bid_price, bid_volume, ask_price, ask_volume):
        raise NotImplementedError

    def on_trade_tick(self, feedcode, side, traded_price, traded_volume):
        raise NotImplementedError

    def on_order_failure(self, feedcode):
        raise NotImplementedError

    def on_order_success(self, feedcode, traded_price, traded_volume):
        raise NotImplementedError
