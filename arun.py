#!/usr/bin/env python3

import argparse
import os
import socket
import sys
import select
import termios
from contextlib import contextmanager

p = argparse.ArgumentParser()
p.add_argument("-s", "--socket", help="socket path where drun is listening", required=True)
args = p.parse_args()


@contextmanager
def without_echo():
    old = termios.tcgetattr(sys.stdin)
    new = termios.tcgetattr(sys.stdin)
    try:
        new[3] &= ~(termios.ICANON | termios.ECHO)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new)
        yield
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)



with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s, without_echo():
    s.connect(args.socket)
    os.set_blocking(0, False)
    while True:
        r, _, _ = select.select([sys.stdin, s], [], [])
        if s in r:
            data = s.recv(1)
            if data:
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
        if sys.stdin in r:
            data = sys.stdin.read(1).encode('utf-8')
            if data:
                s.sendall(data)
