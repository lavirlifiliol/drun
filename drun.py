#!/usr/bin/env python3
import argparse
import socket
import os
import select
import signal
import sys
if __name__ != '__main__':
    raise Warning('This file is not meant to be imported')

p = argparse.ArgumentParser()
p.add_argument("-s", "--socket", help="socket path for arun to join this process", required=True)
p.add_argument('command', nargs=argparse.REMAINDER)
args = p.parse_args()

def on_child_death(signum, frame):
    global c_pid
    _, status = os.waitpid(-1, 0)
    c_pid = None
    raise SystemExit(os.waitstatus_to_exitcode(status))

signal.signal(signal.SIGCHLD, on_child_death)


def run_in_forkpty(cmd):
    pid, fd = os.forkpty()
    if pid == 0:
        os.execlp(cmd[0], *cmd)
    else:
        os.set_blocking(fd, False)
        return pid, fd

def handle_client(s):
    s.setblocking(False)
    while True:
        r, _, _ = select.select([fd, s], [], [])
        if s in r:
            data = s.recv(1024)
            if data:
                os.write(fd, data)
            else:
                break
        if fd in r:
            data = os.read(fd, 1024)
            if data:
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
                s.sendall(data)

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s_top:
    s_top.bind(args.socket)
    s_top.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)
    s_top.listen(0)
    c_pid, fd = run_in_forkpty(args.command)
    try:
        while True:
            cl, _ = s_top.accept()
            print("\n\n arun attached \n\n")
            handle_client(cl)
    finally:
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        if c_pid:
            os.kill(c_pid, signal.SIGINT)
