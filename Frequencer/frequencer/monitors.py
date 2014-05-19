import time
import logging
import contextlib
import functools

import redis

__all__ = ('agent', 'datadog', 'counter')


class Agent(object):
    def time(key, t):
        pass

    def span(key, d):
        pass


class LogAgent(object):
    def __init__(self):
        self.logger = logging.getLogger("LogAgent")

    def time(self, key, t):
        self.logger.info("%s: %s", key, t)

    def span(self, key, d):
        self.logger.info("%s: %s", key, d)


class RedisAgent(object):
    def __init__(self):
        self.redis = redis.Redis(db=5)

    def time(self, key, t):
        self.redis.set(key, t)

    def span(self, key, d):
        for k, v in d.items():
            self.redis.hset(key, k, v)

    def report(self, key):
        d = self.redis.hgetall(key)
        for k, v in d.items():
            d[k] = float(v)
        return d

agent = RedisAgent()


def noop(*args, **kwargs):
    pass


class Datadog(object):
    def __init__(self):
        self.logger = logging.getLogger("DataDog")

    def __getattr__(self, attr):
        return noop

    def _timed(self, func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            s = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                c = time.time() - s
                self.logger.info("Timing: %s, %s" % (func, c))
        return wrap

    def timed(self, *args, **kwargs):
        return self._timed

    def increment(self, key, value=1, tags=None):
        if tags:
            self.logger.info("Increment: %s, %s, %s" % (key, value, tags))
        else:
            self.logger.info("Increment: %s, %s" % (key, value))           

    def gauge(self, key, value, tags=None):
        if tags:
            self.logger.info("Gauge: %s, %s, %s" % (key, value, tags))
        else:
            self.logger.info("Gauge: %s, %s" % (key, value))

    def histogram(self, key, value, tags=None):
        if tags:
            self.logger.info("histogram: %s, %s, %s" % (key, value, tags))
        else:
            self.logger.info("histogram: %s, %s" % (key, value))

try:
    from statsd import statsd as datadog
except:
    datadog = Datadog()


def counter(key):
    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            datadog.increment(key)
            return func(*args, **kwargs)
        return wrapped
    return decorator


@contextlib.contextmanager
def counter_context(key):
    yield
    datadog.increment(key)