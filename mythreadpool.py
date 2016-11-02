#!/usr/bin/python
#!coding:utf-8
#by lmy 2016/10/22

import threading
import sys
#import time
import logging
#logging.basicConfig(level=logging.DEBUG,
#      format='[%(asctime)s %(msecs)d %(module)15s %(name)10s %(funcName)15s %(levelname)s] %(message)s',
#      datefmt = '%F %T')
#
#logging.debug('start')

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class MyThreadPool:
  def __init__(self, max_thread_num):
    #thread array
    self._max_thread_num = max_thread_num
    self._total_thread_num = 0

    #the flag for all threads to destroy
    self._stop = False

    #mutex
    self._lock = threading.Lock()

    #import contitions
    self._cond_idle = threading.Condition(self._lock)
    self._cond_full = threading.Condition(self._lock)
    self._cond_empty = threading.Condition(self._lock)

    #
    self._thread_list = []

  def __del__(self):
    logger.debug('MyThreadPool __del__')
  def PushBack(self, athread):
    self.Lock()

    logger.debug('PushBack inner')
    if not athread == None:
      logger.debug('athread is not None')
      self._thread_list.append(athread)
      self.Notify('idle')
      logger.debug('Notify idle')

      #全部空闲,可以结束线程池
      if len(self._thread_list) >= self._total_thread_num:
        logger.debug('Notify full')
        self.Notify('full')

    self.UnLock()

  def PopThread(self):
    if not len(self._thread_list) == 0:
      return self._thread_list.pop()

  def join(self):
    for athread in self._thread_list:
      athread.join()

  def Destroy(self):
    logger.debug('call Destroy')
    self.Lock()
    #self._stop = True

    #等待线程全部工作完毕
    if len(self._thread_list) < self._total_thread_num:
      self.Wait('full')
      logger.debug('Wait full')

    self._stop = True
    logger.debug('self._stop = True')

    #通知所有线程启动
    logger.debug('len of _thread_list is: %d',len(self._thread_list))
    for athread in self._thread_list:
      athread.Lock()
      athread.Notify()
      athread.UnLock()

    logger.debug('通知每一个线程结束完毕')

    #

    if self._total_thread_num > 0:
      logger.debug('waiting to receive empty notify')
      self.Wait('empty')
      logger.debug('have received empty notify')

    self.UnLock()

  #  for athread in self._thread_list:
  #    athread.join()

  def DispatchTask(self, function = None, args_dict = None):
    self.Lock()

    #线程池线程个数达到最大值并且都在使用，此时等待
    while(len(self._thread_list) <= 0 and self._total_thread_num >= self._max_thread_num):
      logger.debug('waiting idle notify')
      self.Wait('idle')

    #有idle线程
    if len(self._thread_list) > 0:
      athread = self.PopThread()

      athread.SetTask(function, args_dict)

      #notify thread to run
      athread.Lock()
      athread.Notify()
      athread.UnLock()

    #create new thread
    else:
      athread = MyThread(self)
      athread.SetTask(function, args_dict)
      self._total_thread_num +=1
      athread.start()

    self.UnLock()
    logger.debug('DispatchTask is over')


  def Stop(self):
    return self._stop

  def Lock(self):
    self._lock.acquire()
  def UnLock(self):
    self._lock.release()

  def OneThreadFinish(self):
    self.Lock()
    self._total_thread_num -=1
    if self._total_thread_num <= 0:
      self.Notify('empty')
      logger.debug('send emtpy Notify')
    self.UnLock()

  def Wait(self, who):
    if who == 'full':
      self._cond_full.wait()
    elif who == 'idle':
      self._cond_idle.wait()
    elif who == 'empty':
      self._cond_empty.wait()
    else:
      logging.critical('Faltal error!')

  def Notify(self, who):
    if who == 'full':
      self._cond_full.notify()
    elif who == 'idle':
      self._cond_idle.notify()
    elif who == 'empty':
      self._cond_empty.notify()
    else:
      logging.critical('Fatal error!')

class MyThread(threading.Thread):
  def __init__(self, thread_pool = None):
    threading.Thread.__init__(self)
    self.setDaemon(True)
    
    #pool
    self._thread_pool = thread_pool

    #process function
    self._task = None
    self._lock = threading.Lock()
    self._cond = threading.Condition(self._lock)

  def run(self):

    #没有使用线程池
    if self._thread_pool == None:
      self._task(self._args)
      logger.debug('thread pool is None')
      return
    #
    while self._thread_pool.Stop() == False:
      if not self._task == None:
        self._task(self._args)


      #线程池停止工作
      if self._thread_pool.Stop() == True:
        break

      self.Lock()
      #加入到线程池
      self._thread_pool.PushBack(self)
      #等待被唤醒
      self.Wait()
      self.UnLock()

    #线程池停止，线程结束
    self._thread_pool.OneThreadFinish()

    logger.debug('thread %d is finishing', self.ident)

  def Lock(self):
    self._lock.acquire()

  def UnLock(self):
    self._lock.release()

  def Wait(self):
    self._cond.wait()

  def Notify(self):
    self._cond.notify()
      

  def SetTask(self, task_func, args_dict):
    self._task = task_func
    self._args = args_dict


def process(args):
  logger.debug('the value of key 0 is :%s', args[0])
  import time
#  time.sleep(1)

if __name__ == '__main__':
#  athread = MyThread()
#  athread.SetTask(process, {0:'lmy'})
#  athread.start()

  threadpool = MyThreadPool(2)
  i = 0
  while i < 10:
    threadpool.DispatchTask(process, {0: 'lmy'})
    i+=1

  threadpool.Destroy()

  logger.debug('over')


