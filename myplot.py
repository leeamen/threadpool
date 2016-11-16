#!/usr/bin/python
#coding:utf-8
import numpy as np
from matplotlib.pyplot import *
from matplotlib.mlab import *
def Figure():
  figure()
def Plot2DLine(x,y, xla, yla):
  #画图
#  plot(x[pos], y[pos], '+r', markersize = 5)
#  plot(x[neg], y[neg], 'xg', markersize = 3)
  xlabel(xla)
  ylabel(yla)
  plot(x, y)
def Show():
  show()
def Legend(arr):
  legend(arr)
def Title(tit):
  title(tit)

