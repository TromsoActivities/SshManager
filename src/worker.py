# -*- coding: utf-8 -*-
# @Author: Ultraxime
# @Date:   2023-03-15 16:34:57
# @Last Modified by:   Ultraxime
# @Last Modified time: 2023-03-17 16:00:07

from __future__ import annotations


from threading import Thread
from zmq import Context
import zmq

from .config import Config
from .ssh_keys import SshKeyDict


class Listener(Thread):
    _worker: Worker

    def __init__(self, worker: Worker, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._worker = worker

    def run(self):
        config = Config()
        context = Context()
        socket = context.socket(zmq.SUB)
        socket.connect("tcp://" + str(config.get("sockets.manager.ip"))
                       + ":" + str(config.get("sockets.manager.port")))
        socket.setsockopt_string(zmq.SUBSCRIBE, "")
        while True: # not self.is_closed():
            print("Waiting for message.")
            msg = socket.recv_pyobj()
            print("Recv: ")
            print(msg)
            assert isinstance(msg, dict)
            for key, value in msg.items():
                assert isinstance(key, str)
                match key:
                    case "ADD":
                        if isinstance(value, SshKeyDict):
                            self._worker.add_key(value)
                        else:
                            assert isinstance(value, SshKeyDict)
                    case "DEL":
                        if isinstance(value, list):
                            for key_name in value:
                                assert isinstance(key_name, str)
                                self._worker.del_key(key_name)
                        else:
                            assert isinstance(value, str)
                    case "UPDATE":
                        if isinstance(value, SshKeyDict):
                            self._worker.update_key(value)
                        else:
                            assert isinstance(value, SshKeyDict)
                    case _:
                        raise ValueError(key + " is not a expect value for header of a message.")


class Worker:
    _listener: Listener

    def __init__(self):
        self._listener = Listener(self)

    def start(self):
        self._listener.start()

    def add_key(self, dic: SshKeyDict) -> bool:
        old_dict = self.list_key()
        if old_dict.add(dic):
            old_dict.write()
            return True
        return False

    def del_key(self, key_name: str) -> bool:
        old_dict = self.list_key()
        if old_dict.remove(key_name):
            old_dict.write()
            return True
        return False

    def update_key(self, new_dict: SshKeyDict) -> bool:
        new_dict.write()
        return True

    def list_key(self) -> SshKeyDict:
        return SshKeyDict.open()
