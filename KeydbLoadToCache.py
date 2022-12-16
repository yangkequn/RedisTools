#!/usr/bin/env python
import argparse
import redis
from tqdm import tqdm


def connect_redis(conn_dict):
    conn = redis.StrictRedis(host=conn_dict['host'],
                             port=conn_dict['port'],
                             db=conn_dict['db'])
    return conn


def conn_string_type(string):
    try:
        host, portdb = string.split(':')
        port, db = portdb.split('/')
        db = int(db)
    except ValueError:
        format = '<host>:<port>/<db>'
        raise argparse.ArgumentTypeError(
            'incorrect format, should be: %s' % format)
    return {'host': host, 'port': port, 'db': db}


def loadToMem(source):
    src = connect_redis(source)
    [src.type(key) for key in  tqdm(src.keys('*'))]


if __name__ == '__main__':
    source = conn_string_type("keydb2.vm:6379/9")
    loadToMem(source)
