#!/usr/bin/python
#coding:utf-8

import mylog
import mythreadpool as tp
import logging

if __name__ == '__main__':
  logger = logging.getLogger(__name__)
  
  def process(args):
    logger.info('task %d is finished!', args['taskid'])
  
  threadpool = tp.MyThreadPool(2)
  for i in range(1,10):
    threadpool.DispatchTask(process, {'taskid':i})
  threadpool.Destroy()

