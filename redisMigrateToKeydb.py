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


def migrate_redis(source, destination):
    src = connect_redis(source)
    dst = connect_redis(destination)
    for key in tqdm(src.keys('*')):
        type_of_value = src.type(key)
        desPipe = dst.pipeline()
        # migrate without using ttl
        # migrate according to type
        if type_of_value == b'string':
            value = src.get(key)
            desPipe.set(key, value)
        elif type_of_value == b'hash':
            value = src.hgetall(key)
            for k, v in value.items():
                desPipe.hset(key, k, v)
        elif type_of_value == b'list':
            value = src.lrange(key, 0, -1)
            for v in value:
                desPipe.rpush(key, v)
        elif type_of_value == b'set':
            value = src.smembers(key)
            for v in value:
                desPipe.rpush(key, v)
        elif type_of_value == b'zset':
            desPipe.zadd(key, {v[0]: v[1] for v in value})
        else:
            print("Unknown type for key: {key}")
            continue
        desPipe.execute()
    return


if __name__ == '__main__':
    source = conn_string_type("docker.vm:6379/10")
    destination = conn_string_type("10.10.2.18:6379/10")
    migrate_redis(source, destination)
