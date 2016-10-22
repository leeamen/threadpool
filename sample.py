#!/usr/bin/python
#coding:utf-8

import logging
logging.basicConfig(level=logging.INFO,
      format='[%(asctime)s %(levelname)s] %(message)s',
      datefmt = '%F %T')

import threadpool as tp

def process(args):
  logging.info('task %d is finished!', args['taskid'])

threadpool = tp.MyThreadPool(2)
for i in range(1,10):
  threadpool.DispatchTask(process, {'taskid':i})
threadpool.Destroy()

