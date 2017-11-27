
## 1. 使用 c 库

除了编写快速代码之外，Cython的一个主要用例是从Python代码调用外部C库。由于Cython代码本身编译为C代码，直接在代码中调用C函数实际上是微不足道的。以下给出了一个在Cython代码中使用（和包装）外部C库的完整示例，包括适当的错误处理和有关为Python和Cython代码设计合适的API的注意事项。

下面以将 [[CAlg]](https://github.com/fragglet/c-algorithms "CAlg") 的队列算法封装为存储整型值的 FIFO 队列为例。(安装时注意缺失的依赖libtool)

## 2. 定义外部声明

实现队列的 c 的 API ，可以在 `libcalg/queue.h` 中找到，格式如下：

```c
/* file: queue.h */

typedef struct _Queue Queue;
typedef void *QueueValue;

Queue *queue_new(void);
void queue_free(Queue *queue);

int queue_push_head(Queue *queue, QueueValue data);
QueueValue queue_pop_head(Queue *queue);
QueueValue queue_peek_head(Queue *queue);

int queue_push_tail(Queue *queue, QueueValue data);
QueueValue queue_pop_tail(Queue *queue);
QueueValue queue_peek_tail(Queue *queue);

int queue_is_empty(Queue *queue);
```

首先，在`.pxd` 文件重定义 c 的 API。
```Cython
# file: cqueue.pxd

cdef extern from "libcalg/queue.h":
    ctypedef struct Queue:
        pass
    ctypedef void* QueueValue

    Queue* queue_new()
    void queue_free(Queue* queue)

    int queue_push_head(Queue* queue, QueueValue data)
    QueueValue  queue_pop_head(Queue* queue)
    QueueValue queue_peek_head(Queue* queue)

    int queue_push_tail(Queue* queue, QueueValue data)
    QueueValue queue_pop_tail(Queue* queue)
    QueueValue queue_peek_tail(Queue* queue)

    bint queue_is_empty(Queue* queue)
```
请注意，这些声明与 `c` 头文件声明几乎完全相同，因此经常可以将其复制过来。但是，不需要像上面那样提供所有的声明，只需要在代码或其他声明中使用的那些声明，以便Cython可以看到足够、一致的子集。然后，考虑适配它们，使它们更适合在Cython中使用。

具体来说，应该注意为C函数选择好的参数名称，因为Cython允许将它们作为关键字参数传递。稍后更改它们是向后不兼容的API修改。马上选择好名字将使这些函数更适合于Cython代码工作。

我们应该注意上面`Queue` 结构体的声明。 `Queue` 在此处做非透明处理。Cython不需要了解结构体的内容，此处没有声明结构体的内容，提供了一个空定义。

    `cdef struct Queue: pass` 和 `ctypedef struct Queue: pass`存在着微小的差异。前者声明的类型在c 中引用为 `struct Queue`,后者在 c 中引用为 `Queue`.This is a C language quirk that Cython is not able to hide。现在的 c 库使用 `ctypedef`类型的结构体。

最后一行也很特殊。`queue_is_empty()`返回的整型值是 c 中的boolean值。例如，返回值非零或零，意味着队列空或非空。最好使用 Cython 的 `bint` 类型将c 中的整型映射为 python 的boolean 值对象（`True`和`False`）。`pxd`中的这种声明可以简化使用。

将使用的一个库定义为一个 `.pxd`,API 较大时，可以一个头文件对应一个 `.pxd`。这样可以简化项目的复用。Cython 封装了常用的 `.pxd` 集，例如， `cpython`、`libc`、`libcpp`。`numpy` 库也提供了 `numpy.pxd`,可以在 `Cython/Includes` 源码目录下找到完整的 `.pxd` 。

## 2. 写封装类
在声明 c 库的 API 后，开始设计封装 `c queue` 的 `Queue`类。如下：

    注意：`.pyx`文件与 c 库声明文件 `cqueue.pxd` 描述不同的代码，因此他们的名称应该不同。
    `.pxd` 文件为 库的导出代码（用于 `.pyx`调用）
```Cython
# file: queue.pyx

cimport cqueue

cdef class Queue:
    cdef cqueue.Queue* _c_queue
    def __cinit__(self):
        self._c_queue = cqueue.queue_new()
```
注意此处是`__cinit__`,而不是`__init__`。尽管`__init__`也可以使用，但不确保一定会执行，例如，创建子类而忘记调用父类的构造函数。没有初始化的c 指针会导致 python 解释器的崩溃。Cython 提供的`__cinit__`会在构造时立即调用。甚至在调用`__init__`之前，因此是最适合实例化 `cdef` 字段的地方。但是，由于是在构建对象时调用`__cinit__`, `self`还没有完全构建，除了对 `cdef`字段赋值外，避免使用`self`。

同时上面的方法没有参数，尽管子类型会接收一些参数。一个不带参数的`__cinit__`方法不会接受传递给构造器的参数，但并不阻止子类添加参数。如果在 `__cinit__`中使用参数，应该与 `__init__` 声明匹配。
## 3.内存管理
上面的方法并不安全，如果在调用`queue_new()`时出错，代码会对错误保持沉默，之后会运行在崩溃的环境。 根据`queue_new()`函数的文档，引起错误的唯一原因是没有足够的内存，在这种情况下，它会返回`NULL`,否则，会返回指向新队列的指针。
在python 下出现这种情况会抛出`MemoryError`,可以将初始化函数修改如下：
```Cython
# file: queue.pyx

cimport cqueue

cdef class Queue:
    cdef cqueue.Queue* _c_queue
    def __cinit__(self):
        self._c_queue = cqueue.queue_new()
        if self._c_queue is NULL:
            raise MemoryError()
```
    注意：创建 `MemoryError`抛出异常，也可能因为以为内存不足而失败。幸运的是，CPython 提供了 C-API函数 PyErr_NoMemory() 来安全正确的抛出异常。从 0.14.1后，在调用raise MemoryError or raise MemoryError()时，Cython自动替换为这个 C-API。如果使用老版本，需要从标准包 `cpython.exec` `cimort `这个 C-API 函数，然后直接调用。

    下面要做的事情是，不使用Queue实例时进行清理（例如，所有引用都已删除）。这里CPython提供了回调（Cython 使用的方法`__dealloc__()`）。这里，我们需要在init 方法成功后，在最后释放 c 的队列。
```CPython
def __dealloc__(self):
    if self._c_queue is not NULL:
        cqueue.queue_free(self._c_queue)
```
## 4.编译、连接
此时，我们有了可以测试的 Cython 模块。编译它，我们需要配置 `distutils` 的 `setup.py`脚本。下面是基础的编译 Cython 模块：
```Python
# file: setup.py

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

setup(
    ext_modules = cythonize([Extension("queue", ["queue.pyx"])])
)
```
为了使用外部的 c 库，我们需要扩展这个脚本，包含必要的设置。假设库安装在 `/usr/lib` 和 ‘/usr/include’， 我们可以将上面的扩展进行如下转换：

```Python
# from
ext_modules = cythonize([Extension("queue", ["queue.pyx"])])

# to
ext_modules = cythonize([
    Extension("queue", ["queue.pyx"],
              libraries=["calg"])
    ])
```
如果没在上面的位置，我们可以提供需要的 c 编译器标志，例如：
```shell
CFLAGS="-I/usr/local/otherdir/calg/include"  \
LDFLAGS="-L/usr/local/otherdir/calg/lib"     \
    python setup.py build_ext -i
```
一旦编译了，我们可以 `import`、实例化新 `Queue`:
```shell
$ export PYTHONPATH=.
$ python -c 'import queue.Queue as Q ; Q()'
```
## 5. 实用性映射
在实现类的公有接口之前，可以先看看python 提供的接口。此处我们需要 FIFO 队列，只需提供方法 `append()`、`peek()`、`pop()`、以及一次添加多个值的`extend()`。由于我们清楚所有的值来自c，现在最好只提供`cdef` 方法，提供直接的 C 接口。
在 c 中，不管数据类型是什么，常用 `void *`来存储数据。由于我们只想存储 `int`值，大小正好与指针相同，通过技巧可以避免额外的内存分配，我们可以将 `int`值与 `void*` 相互转换，可以直接将 `int` 值转为指针值。

例如，`append()`方法实现：(考虑了异常)
```Cython
cdef append(self, int value):
    if not cqueue.queue_push_tail(self._c_queue,
                                  <void*>value):
        raise MemoryError()
```
`extend()`方法;
```Cython
cdef extend(self, int* values, size_t count):
    """Append all ints to the queue.
    """
    cdef size_t i
    for i in range(count):
        if not cqueue.queue_push_tail(
                self._c_queue, <void*>values[i]):
            raise MemoryError()

```

`peek()` 和 `pop()`
```Cython
cdef int peek(self):
    return <int>cqueue.queue_peek_head(self._c_queue)

cdef int pop(self):
    return <int>cqueue.queue_pop_head(self._c_queue)
```
## 6. 错误处理
考虑队列为空。根据文档可知，函数返回 `NULL`指针，不是一个有效值。由于我们需要转到，或转自 int，我们不能分清楚队列为空返回 `NULL` 和 队列存储的值是 `0`。 我们可以在 Cython中，让第一种情况抛出异常，第二种情况返回简单的 0。
```Cython
cdef int peek(self) except? -1:   # ？ 的含义表示返回值是歧义的，或许异常，或许值
    value = <int>cqueue.queue_peek_head(self._c_queue)
    if value == 0:
        # this may mean that the queue is empty, or
        # that it happens to contain a 0 value
        if cqueue.queue_is_empty(self._c_queue):
            raise IndexError("Queue is empty")
    return value
```
CPython 允许声明隐含含义为异常的值。外层的代码只需在收到这个值的时候，通过`PyErr_Occurred()`检测异常。

`pop()`方法：
```CPython
cdef int pop(self) except? -1:
    if cqueue.queue_is_empty(self._c_queue):
        raise IndexError("Queue is empty")
    return <int>cqueue.queue_pop_head(self._c_queue)
```

` __bool__() ` 方法： (python 2 调用 `__nonzero__`,Cython 可以使用两者)
```Cython
def __bool__(self):
    return not cqueue.queue_is_empty(self._c_queue)
```
## 7. 测试

此处使用 `doctests`做测试，同时也可以提供文档。要使用 `doctests`,需要可以调用的 Python API。可以通过将方法从 `cdef` 改为 `cpdef` 来快速提供 Python API 接口。这样Cython 产生两个入口，一个从python 代码调用，使用 python 对象作为参数；另一个从C 调用，使用 c 的语义。请注意，`cpdef` 方法可以确保它们可以被Python方法正确覆盖。与`cdef`方法相比，这增加了很小的开销。

下面为尽可能使用 `cpdef` 方法的完整示例：
```Cython
cimport cqueue

cdef class Queue:
    """A queue class for C integer values.

    >>> q = Queue()
    >>> q.append(5)
    >>> q.peek()
    5
    >>> q.pop()
    5
    """
    cdef cqueue.Queue* _c_queue
    def __cinit__(self):
        self._c_queue = cqueue.queue_new()
        if self._c_queue is NULL:
            raise MemoryError()

    def __dealloc__(self):
        if self._c_queue is not NULL:
            cqueue.queue_free(self._c_queue)

    cpdef append(self, int value):
        if not cqueue.queue_push_tail(self._c_queue,
                                      <void*>value):
            raise MemoryError()

    cdef extend(self, int* values, size_t count):
        cdef size_t i
        for i in xrange(count):
            if not cqueue.queue_push_tail(
                    self._c_queue, <void*>values[i]):
                raise MemoryError()

    cpdef int peek(self) except? -1:
        cdef int value = \
            <int>cqueue.queue_peek_head(self._c_queue)
        if value == 0:
            # this may mean that the queue is empty,
            # or that it happens to contain a 0 value
            if cqueue.queue_is_empty(self._c_queue):
                raise IndexError("Queue is empty")
        return value

    cpdef int pop(self) except? -1:
        if cqueue.queue_is_empty(self._c_queue):
            raise IndexError("Queue is empty")
        return <int>cqueue.queue_pop_head(self._c_queue)

    def __bool__(self):
        return not cqueue.queue_is_empty(self._c_queue)
```

注意 `cpdef`特性不适用于 `extend()`方法，方法签名与 python 参数类型不兼容，当然也可以按下面方法提供：
```Cython
cdef c_extend(self, int* values, size_t count):
    cdef size_t i
    for i in range(count):
        if not cqueue.queue_push_tail(
                self._c_queue, <void*>values[i]):
            raise MemoryError()

cpdef extend(self, values):
    for value in values:
        self.append(value)
```
## 8. 回调
为了提供当用户定义的事件发生时，才从队列中弹出值。我们需要传入一个函数：
```Python
def pop_until(self, predicate):
    while not predicate(self.peek()):
        self.pop()
```
假定 C 队列提供了可以将函数作为参数的API：
```c
/* C type of a predicate function that takes a queue value and returns
 * -1 for errors
 *  0 for reject
 *  1 for accept
 */
typedef int (*predicate_func)(void* user_context, QueueValue data);

/* Pop values as long as the predicate evaluates to true for them,
 * returns -1 if the predicate failed with an error and 0 otherwise.
 */
int queue_pop_head_until(Queue *queue, predicate_func predicate,
                         void* user_context);
```
C回调函数经常有一个通用`void*` 参数，它允许通过C-API将任何类型的上下文或状态传递到回调函数中。我们将使用它来传递我们的Python谓词函数（predicate function）。

首先，我们必须定义一个具有我们可以传入C-API函数的预期签名的回调函数：
```Cython
cdef int evaluate_predicate(void* context, cqueue.QueueValue value):
    "Callback function that can be passed as predicate_func"
    try:
        # recover Python function object from void* argument
        func = <object>context
        # call function, convert result into 0/1 for True/False
        return bool(func(<int>value))
    except:
        # catch any Python errors and return error indicator
        return -1
```
主要是将指针作为用户上下文参数传递给函数对象。
```
def pop_until(self, python_predicate_function):
    result = cqueue.queue_pop_head_until(
        self._c_queue, evaluate_predicate,
        <void*>python_predicate_function)
    if result == -1:
        raise RuntimeError("an error occurred")
```
通常的模式是首先将Python对象引用转换为 `void*`，将其传递给C-API函数，然后将其转换回C谓词回调函数中的Python对象。转为`void*`创建借用引用。再转换为<object>，Cython递增对象的引用计数，从而将借用的引用转换回拥有的引用。在谓词函数结束时，拥有的引用再次超出范围，Cython放弃它。

上面代码中的错误处理有点简单。具体而言，谓词函数引发的任何异常基本上都会被丢弃，只会导致RuntimeError()之后被抛出。这可以通过将异常存储在通过上下文参数传递的对象中并在C-API函数返回-1以指示错误之后重新抛出它来改进。
