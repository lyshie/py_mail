#!/usr/bin/env python
# -*- coding: utf-8 -*-

#=========================================================================
#
#         FILE: py_today.py
#
#        USAGE: ./py_today.py
#
#  DESCRIPTION: Create 'Today' class for date/time manipulation
#
#      OPTIONS: ---
# REQUIREMENTS: ---
#         BUGS: ---
#        NOTES: ---
#       AUTHOR: SHIE, Li-Yi (lyshie), lyshie@mx.nthu.edu.tw
# ORGANIZATION:
#      VERSION: 1.0
#      CREATED: 2014-10-14 15:11:30
#     REVISION: ---
#=========================================================================

import calendar
import datetime
import time
import pytz

"""
    October 2014    
Mo Tu We Th Fr Sa Su
       1  2  3  4  5
 6  7  8  9 10 11 12
13 14 15 16 17 18 19
20 21 22 23 24 25 26
27 28 29 30 31      
"""


class Today(object):

    """Today"""

    def __init__(self, epoch=time.time(), tz_name='Asia/Taipei'):
        """
            epoch = UNIX timestamp
            tz_name = name of timezone
        """
        super(Today, self).__init__()

        self.epoch = epoch or 0

        if (tz_name):
            self.tz = pytz.timezone(tz_name)

    def set_timezone(self, tz_name=None):
        """Set the current internal timezone"""
        if (tz_name):
            self.tz = pytz.timezone(tz_name)

    @staticmethod
    def strip_time(dt=None):
        """Strip the part of time"""
        if (dt):
            return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    def begin_of_today(self, epoch=None):
        """Get begin time of today (included)"""
        if (not epoch):
            epoch = self.epoch

        dt = datetime.datetime.fromtimestamp(epoch, tz=self.tz)

        return self.strip_time(dt)

    def end_of_today(self, epoch=None):
        """Get end time of today (excluded)"""
        if (not epoch):
            epoch = self.epoch

        dt = datetime.datetime.fromtimestamp(epoch, tz=self.tz)
        dt = dt + datetime.timedelta(days=1)

        return self.strip_time(dt)

    def first_of_this_week(self, epoch=None, strip_time=True):
        """Get first date of this week"""
        if (not epoch):
            epoch = self.epoch

        dt = datetime.datetime.fromtimestamp(epoch, tz=self.tz)
        dt = dt - datetime.timedelta(days=dt.weekday())

        if (strip_time):
            return self.strip_time(dt)
        else:
            return dt

    def last_of_this_week(self, epoch=None, strip_time=True):
        """Get last date of this week"""
        if (not epoch):
            epoch = self.epoch

        dt = datetime.datetime.fromtimestamp(epoch, tz=self.tz)
        dt = dt + datetime.timedelta(days=6 - dt.weekday())

        if (strip_time):
            return self.strip_time(dt)
        else:
            return dt

    def first_of_this_month(self, epoch=None, strip_time=True):
        """Get first date of this month"""
        if (not epoch):
            epoch = self.epoch

        dt = datetime.datetime.fromtimestamp(epoch, tz=self.tz)
        dt = dt.replace(day=1)

        if (strip_time):
            return self.strip_time(dt)
        else:
            return dt

    def last_of_this_month(self, epoch=None, strip_time=True):
        """Get last date of this month"""
        if (not epoch):
            epoch = self.epoch

        dt = datetime.datetime.fromtimestamp(epoch, tz=self.tz)
        weekday, number = calendar.monthrange(dt.year, dt.month)
        dt = dt.replace(day=number)

        if (strip_time):
            return self.strip_time(dt)
        else:
            return dt

    def get_epoch(self):
        """Get internal unix timestamp"""
        return self.epoch

    def set_epoch(self, epoch=time.time()):
        """Set/Reset internal unix timestamp"""
        self.epoch = epoch or 0

    def get_datetime(self):
        """Get datetime.datetime object"""
        dt = datetime.datetime.fromtimestamp(self.epoch, tz=self.tz)

        return dt

    def set_datetime(self, dt=None):
        """Set datetime.datetime object"""
        if (dt):
            #self.epoch = calendar.timegm(dt.utctimetuple())
            self.epoch = time.mktime(dt.timetuple())

    def __sub__(self, other):
        if (isinstance(other, datetime.timedelta)):
            self.set_datetime(self.get_datetime() - other)
            return self
        elif (isinstance(other, basestring)):
            self.set_datetime(
                self.get_datetime() - self.str_to_timedelta(other))
            return self
        else:
            raise TypeError

    def __isub__(self, other):
        return self.__sub__(other)

    def __add__(self, other):
        if (isinstance(other, datetime.timedelta)):
            self.set_datetime(self.get_datetime() + other)
            return self
        elif (isinstance(other, basestring)):
            self.set_datetime(
                self.get_datetime() + self.str_to_timedelta(other))
            return self
        else:
            raise TypeError

    def __iadd__(self, other):
        return self.__add__(other)

    def format_time(self, epoch=None, dt=None, format="%F %T (%z) (%Z)"):
        """Get well formatted datetime string"""
        if (dt):
            return dt.strftime(format)
        elif (epoch):
            dt = datetime.datetime.fromtimestamp(epoch, tz=self.tz)
            return dt.strftime(format)
        else:
            dt = datetime.datetime.fromtimestamp(self.epoch, tz=self.tz)
            return dt.strftime(format)

    @staticmethod
    def str_to_timedelta(delta=""):
        """Convert string into datetime.timedelta object"""
        d = {}
        for token in delta.split(","):
            k, v = token.strip().split("=", 2)
            d[k.strip()] = int(v.strip())

        # unpack argument lists (dict)
        return datetime.timedelta(**d)


def main():
    """main"""
    print("              TODAY: {}".format(time.strftime("%F %T (%z) (%Z)")))

    #today = Today(epoch=time.time() - 86400 * 23)
    today = Today()

    print("              TODAY: {}".format(
        today.format_time(epoch=today.get_epoch())))
    print("FIRST OF THIS MONTH: {}".format(
        today.format_time(dt=today.first_of_this_month())))
    print(" LAST OF THIS MONTH: {}".format(
        today.format_time(dt=today.last_of_this_month())))
    print(" FIRST OF THIS WEEK: {}".format(
        today.format_time(dt=today.first_of_this_week())))
    print("  LAST OF THIS WEEK: {}".format(
        today.format_time(dt=today.last_of_this_week())))
    print("     BEGIN OF TODAY: {}".format(
        today.format_time(dt=today.begin_of_today())))
    print("       END OF TODAY: {}".format(
        today.format_time(dt=today.end_of_today())))

    print(today.get_epoch())
    today -= "minutes=1"
    print(today.get_epoch())

if __name__ == '__main__':
    main()
