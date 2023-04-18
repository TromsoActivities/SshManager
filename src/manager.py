# -*- coding: utf-8 -*-
# @Author: Ultraxime
# @Date:   2023-03-15 16:35:04
# @Last Modified by:   Ultraxime
# @Last Modified time: 2023-03-17 15:49:21
from __future__ import annotations


from threading import Thread
from zmq import Context, Socket
import zmq

from .config import Config
from .ssh_keys import SshKeyDict


class Listener(Thread):
    _manager: Manager

    def __init__(self, manager: Manager, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._manager = manager

    def run(self):
        config = Config()
        context = Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:" + str(config.get("sockets.discord.port")))
        while True: # not self.is_closed():
            print("Waiting for message.")
            msg = socket.recv_pyobj()
            print("Recv: ")
            print(msg)
            if isinstance(msg, dict):
                for key, value in msg.items():
                    if not isinstance(key, str):
                        socket.send_pyobj("FAIL")
                    else:
                        match key:
                            case "ADD":
                                if isinstance(value, SshKeyDict):
                                    if self._manager.add_key(value):
                                        socket.send_pyobj("ACK")
                                    else:
                                        socket.send_pyobj("FAIL")
                                else:
                                    socket.send_pyobj("FAIL")
                                    assert isinstance(value, SshKeyDict)
                            case "DEL":
                                if isinstance(value, str):
                                    if self._manager.del_key(value):
                                        socket.send_pyobj("ACK")
                                    else:
                                        socket.send_pyobj("FAIL")
                                else:
                                    socket.send_pyobj("FAIL")
                                    assert isinstance(value, str)
                            case _:
                                socket.send_pyobj("FAIL")
                                raise ValueError(key + " is not a expect value for header of a message.")
            elif isinstance(msg, str):
                if msg == "LIST":
                    socket.send_pyobj({"LIST": self._manager.list_key()})
                else:
                    socket.send_pyobj("FAIL")


class Manager:
    _listener: Listener
    _socket: Socket

    def __init__(self):
        self._listener = Listener(self)
        config = Config()
        context = Context()
        self._socket = context.socket(zmq.PUB)
        self._socket.bind("tcp://*:" + str(config.get("sockets.worker.port")))

    def start(self):
        self._listener.start()

    def add_key(self, dic: SshKeyDict) -> bool:
        old_dict = self.list_key()
        if old_dict.add(dic):
            old_dict.write()
            self.update()
            return True
        return False

    def del_key(self, key_name: str) -> bool:
        old_dict = self.list_key()
        if old_dict.remove(key_name):
            old_dict.write()
            self.update()
            return True
        return False

    def list_key(self) -> SshKeyDict:
        return SshKeyDict.open()

    def full_update(self, new_dict: SshKeyDict):
        new_dict.write("/authorized_key.save")
        self._socket.send_pyobj({"UPDATE": new_dict})

    def update(self):
        new_dict = SshKeyDict.open()
        try:
            old_dict = SshKeyDict.open("/authorized_key.save")
        except FileNotFoundError:
            self.full_update(new_dict)
            return
        new_dict.write("/authorized_key.save")
        self._socket.send_pyobj(new_dict.diff(old_dict))
