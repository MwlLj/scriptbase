# encoding=utf8
from threading import Lock


class IObservable(object):
    def __init__(self):
        self.m_observers = []
        self.m_mutex = Lock()

    def add_observer(self, observer):
        self.m_mutex.acquire()
        self.m_observers.append(observer)
        self.m_mutex.release()

    def notify(self, *tuples, **dicts):
        for observer in self.m_observers:
            observer.update(self, *tuples, **dicts)


class IObserver(object):
    def update(self, observable, *tuples, **dicts):
        pass
