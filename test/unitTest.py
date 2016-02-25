# -*- coding: utf-8 -*-
import unittest
import testTarget

class mytest(unittest.TestCase):
  def setUp(self):
    pass
  def tearDown(self):
    pass
  def testsum(self):
    self.assertEqual(testTarget.sum(1, 2), 2, 'test sum fail')
  def testsub(self):
    self.assertEqual(testTarget.sub(2, 1), 1, 'test sub fail')
if __name__ =='__main__':
    unittest.main()
