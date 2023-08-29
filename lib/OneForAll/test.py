#!/usr/bin/env python3
# coding=utf-8

"""
Example
"""
import os
import sys
root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_path)
from oneforall import OneForAll


def oneforall(domain):
    test = OneForAll(target=domain)
    test.dns = True
    test.brute = True
    test.req = True
    test.takeover = True
    test.run()
    results = test.datas
    return results


if __name__ == '__main__':
    oneforall('freebuf.com')
