#!/usr/bin/env python
# -*- coding: utf-8 -*-

#=========================================================================
#
#         FILE: py_today_test.py
#
#        USAGE: ./py_today_test.py
#
#  DESCRIPTION: Unit test for Today class
#
#      OPTIONS: ---
# REQUIREMENTS: ---
#         BUGS: ---
#        NOTES: ---
#       AUTHOR: SHIE, Li-Yi (lyshie), lyshie@mx.nthu.edu.tw
# ORGANIZATION:
#      VERSION: 1.0
#      CREATED: 2014-10-23 16:43:30
#     REVISION: ---
#=========================================================================

import unittest
import py_today
import random


class TodayTestCase(unittest.TestCase):

    def setUp(self):
        self.today = py_today.Today(epoch=1414050717)

    def test_today(self):
        expected = '2014-10-23 15:51:57 (+0800) (CST)'
        result = self.today.format_time(epoch=self.today.get_epoch())

        self.assertEqual(expected, result)

    def test_first_of_this_month(self):
        expected = '2014-10-01 00:00:00 (+0800) (CST)'
        result = self.today.format_time(dt=self.today.first_of_this_month())

        self.assertEqual(expected, result)

    def test_last_of_this_month(self):
        expected = '2014-10-31 00:00:00 (+0800) (CST)'
        result = self.today.format_time(dt=self.today.last_of_this_month())

        self.assertEqual(expected, result)

    def test_first_of_this_week(self):
        expected = '2014-10-20 00:00:00 (+0800) (CST)'
        result = self.today.format_time(dt=self.today.first_of_this_week())

        self.assertEqual(expected, result)

    def test_last_of_this_week(self):
        expected = '2014-10-26 00:00:00 (+0800) (CST)'
        result = self.today.format_time(dt=self.today.last_of_this_week())

        self.assertEqual(expected, result)

    def test_begin_of_today(self):
        expected = '2014-10-23 00:00:00 (+0800) (CST)'
        result = self.today.format_time(dt=self.today.begin_of_today())

        self.assertEqual(expected, result)

    def test_end_of_today(self):
        expected = '2014-10-24 00:00:00 (+0800) (CST)'
        result = self.today.format_time(dt=self.today.end_of_today())

        self.assertEqual(expected, result)

    def test_end_of_today2(self):
        expected = '2014-10-23 23:59:59 (+0800) (CST)'

        eot = py_today.Today()
        eot.set_datetime(dt=self.today.end_of_today())
        eot -= "seconds=1"
        result = eot.format_time(epoch=eot.get_epoch())

        self.assertEqual(expected, result)

    def test_calc_add(self):
        expected = '2014-10-23 01:01:01 (+0800) (CST)'

        bot = py_today.Today()
        bot.set_datetime(dt=self.today.begin_of_today())
        bot += "seconds=1, minutes=1, hours=1"
        result = bot.format_time(epoch=bot.get_epoch())

        self.assertEqual(expected, result)

    def test_calc_add2(self):
        expected = '2014-10-23 01:01:01 (+0800) (CST)'

        bot = py_today.Today()
        bot.set_datetime(dt=self.today.begin_of_today())
        bot += "seconds=61, minutes=60"
        result = bot.format_time(epoch=bot.get_epoch())

        self.assertEqual(expected, result)

    def test_calc_sub(self):
        expected = '2014-10-22 22:58:59 (+0800) (CST)'

        bot = py_today.Today()
        bot.set_datetime(dt=self.today.begin_of_today())
        bot -= "seconds=1, minutes=1, hours=1"
        result = bot.format_time(epoch=bot.get_epoch())

        self.assertEqual(expected, result)

    def test_calc_sub2(self):
        expected = '2014-10-22 22:58:59 (+0800) (CST)'

        bot = py_today.Today()
        bot.set_datetime(dt=self.today.begin_of_today())
        bot -= "seconds=61, minutes=60"
        result = bot.format_time(epoch=bot.get_epoch())

        self.assertEqual(expected, result)

    def test_invariant(self):
        expected = '2014-10-23 00:00:00 (+0800) (CST)'

        nums = map(lambda x: random.randint(0, 300), range(100))

        bot = py_today.Today()
        bot.set_datetime(dt=self.today.begin_of_today())

        random.shuffle(nums)
        for n in nums:
            bot -= "seconds={}".format(n)

        random.shuffle(nums)
        for n in nums:
            bot += "seconds={}".format(n)

        result = bot.format_time(epoch=bot.get_epoch())

        self.assertEqual(expected, result)


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TodayTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main()
