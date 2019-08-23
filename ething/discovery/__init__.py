# coding: utf-8
import gevent


SCANNER_CLS = list()


def scan(timeout=10):

    scanners = [cls() for cls in SCANNER_CLS]
    gevent.joinall([gevent.spawn(scanner.scan, timeout) for scanner in scanners])



