import logging
import sys
from threading import Thread,Lock
import time


__all__ = ['Field', 'All', 'Every', 'Int', 'List', 'Job', 'Scheduler']


__version__ = '0.1.0'


class Field(object):
    def __init__(self, param):
        self.param = param

    def __repr__(self):
        return 'cron.Field(' + repr(self.param) + ')'


class All(Field):
    def __init__(self):
        pass

    def __eq__(self, value):
        return True

    def __repr__(self):
        return 'cron.All()'


class Every(Field):
    def __eq__(self, value):
        return value % self.param == 0

    def __repr__(self):
        return 'cron.Every(' + repr(self.param) + ')'


class Int(Field):
    def __eq__(self, value):
        return value == self.param

    def __repr__(self):
        return repr(self.param)


class List(Field):
    def __eq__(self, value):
        return value in self.param

    def __repr__(self):
        return repr(self.param)


def create_field(value):
    if isinstance(value, Field):
        return value
    elif isinstance(value, int):
        return Int(value)
    elif isinstance(value, list):
        return List(value)
    else:
        raise TypeError()


class Job(object):
    def __init__(self, function, args=(), kwargs={}, name=None, minute=All(), hour=All(), day=All(), month=All(), weekday=All()):
        self.function = function
        self.args = args
        self.kwargs = kwargs
        if name:
            self.name = name
        else:
            self.name = self.function.__name__
        self.minute = create_field(minute)
        self.hour = create_field(hour)
        self.day = create_field(day)
        self.month = create_field(month)
        self.weekday = create_field(weekday)

    def __str__(self):
        return '<cron.Job \'' + self.name + '\'>'

    def __repr__(self):
        return 'cron.Job(' + repr(self.function) + ', args=' + repr(self.args) + ', kwargs=' + repr(self.kwargs) + ', name=' + repr(self.name) + ', minute=' + repr(self.minute) + ', hour=' + repr(self.hour) + ', day=' + repr(self.day) + ', month=' + repr(self.month) + ', weekday=' + repr(self.weekday) + ')'

    def should_run(self, time):
        return time.tm_min == self.minute and time.tm_hour == self.hour and time.tm_mday == self.day and time.tm_mon == self.month and time.tm_wday == self.weekday

    def run(self):
        self.function(*self.args, **self.kwargs)


class Scheduler(object):
    def __init__(self, log=None, time=time.localtime, poll_interval=0.2):
        if log:
            self.log = log
        else:
            self.log = logging.getLogger('cron')
        self.time           = time
        self.jobs           = []
        self.poll_interval  = poll_interval
        self._lock          = Lock()
        self.running        = False
        self.thread         = None

    def __repr__(self):
        return 'cron.Scheduler(log=' + repr(self.log) + ', time=' + repr(self.time) + ')'

    def add(self, job):
        self._lock.acquire()
        self.jobs.append(job)
        self._lock.release()

    def remove(self, job):
        self._lock.acquire()
        self.jobs.remove(job)
        self._lock.release()

    def start(self):
        if self.is_running():
            return
        self.thread = Thread(target=self.run, name='bliptrip_cron', daemon=True)
        self.running = True
        self.thread.start()
        self.log.info('Scheduler running')

    def stop(self):
        if not self.is_running():
            return
        self.running = False
        self.thread.join() #Wait for scheduler to stop
        self.log.info('Scheduler stopped')

    def is_running(self):
        return bool(self.thread) and self.running

    def join(self):
        if bool(self.thread):
            self.thread.join()

    def run(self):
        while self.running:
            # get times
            ctime = time.time()
            ltime = self.time(ctime)
            # get sleep target to run on the minute
            sleep_target = ctime + 60 - ltime.tm_sec
            # copy jobs to prevent iterating over a mutating list
            self._lock.acquire()
            jobs = self.jobs[:]
            self._lock.release()
            # go through each job and run it if necessary
            for job in jobs:
                try:
                    if job.should_run(ltime):
                        job.run()
                except Exception:
                    self.log.exception('Caught exception on job "' + job.name + '"')
            while time.time() < sleep_target:
                if not self.running:
                    break
                time.sleep(self.poll_interval)
