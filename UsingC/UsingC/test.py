import queue

try:
    print("=======================")
    print("初始化 一个队列")
    q=queue.Queue()
    print("初始化 队列成功")
    print("=======================")
    i=5
    print("插入一个元素 %d" % (i))
    q.append(i)
    print("弹出一个元素 %d" % q.pop())
    print("=======================")
except Exception as e:
    print("发生异常： %s" % e)
finally:
    print("测试完成")
