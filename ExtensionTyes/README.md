## 1. 扩展类型（aka. cdef classes）
为了支持面向对象编程，Cython支持像Python一样编写正常的Python类：
```Python
class MathFunction(object):
    def __init__(self, name, operator):
        self.name = name
        self.operator = operator

    def __call__(self, *operands):
        return self.operator(*operands)
```
然而，基于Python所谓的“内置类型”，Cython支持第二种类：扩展类型，由于用于声明的关键字，有时被称为“cdef类”。与Python类相比，它们有些受限制，但通常比通用的Python类更具有内存效率和更快的速度。主要区别在于它们使用C结构来存储它们的字段和方法，而不是Python字典。这允许他们在他们的字段中存储任意的C类型，而不需要Python包装器，并且直接在C级访问字段和方法，而不需要通过Python字典查找。

正常的Python类可以从cdef类继承，但不能以其他方式继承。Cython需要知道完整的继承层次结构，以便布置其C结构，并将其限制为单一继承。另一方面，普通的Python类可以继承任何数量的Python类和扩展类型，无论是Cython代码还是纯Python代码。

到目前为止，我们的集成示例并不是很有用，因为它只集成了一个硬编码函数。为了弥补这一点，几乎不用牺牲速度，我们将使用一个cdef类来表示浮点数的函数：
```Cython
cdef class Function:
    cpdef double evaluate(self, double x) except *:
        return 0
```
指令cpdef使两个版本的方法可用; 一个从Cython快速使用，一个从Python使用较慢。然后：
```Cython
cdef class SinOfSquareFunction(Function):
    cpdef double evaluate(self, double x) except *:
        return sin(x**2)
```
这比为cdef方法提供python包装略微多一点：与cdef方法不同，cpdef方法可以被Python子类中的方法和实例属性完全覆盖。与cdef方法相比，它增加了一些调用开销。

使用这个，我们现在可以改变我们的整合例子：
```Cython
def integrate(Function f, double a, double b, int N):      # 函数的积分
    cdef int i
    cdef double s, dx
    if f is None:
        raise ValueError("f cannot be None")
    s = 0
    dx = (b-a)/N
    for i in range(N):
        s += f.evaluate(a+i*dx)
    return s * dx

print(integrate(SinOfSquareFunction(), 0, 1, 10000))
```
这几乎和前面的代码一样快，但是它更灵活，因为集成的功能可以改变。我们甚至可以传入一个在Python空间中定义的新函数：
```shell
>>> import integrate
>>> class MyPolynomial(integrate.Function):
...     def evaluate(self, x):
...         return 2*x*x + 3*x - 10
...
>>> integrate(MyPolynomial(), 0, 1, 10000)
-7.8335833300000077
```

这大约慢了20倍，但仍然比原来只有整合Python的代码快了10倍左右。这显示了当整个循环从Python代码移动到Cython模块时，加速可能会很容易。

关于我们新的实现的一些注意事项evaluate：
- 这里的快速方法调度只能在`Function`中声明`evaluate`。 如果已经在SinOfSquareFunction中引入了`evaluate`，代码仍然可以工作，但是Cython会使用较慢的Python方法调度机制。
- 以相同的方式，如果参数f没有被输入，而只是作为Python对象传递，那么使用较慢的Python调度。
- 由于参数是键入的，我们需要检查它是否是 None。在Python中，查找evaluate方法时会导致AttributeError，但是Cython会尝试访问None的（不兼容的）内部结构，就像它是一个Function一样，导致崩溃或数据损坏。

有一个编译器指令`nonecheck`打开检查这个，代价是速度降低。 下面是如何使用编译器指令来动态打开或关闭nonecheck：
```Cython
#cython: nonecheck=True
#        ^^^ Turns on nonecheck globally

import cython

# Turn off nonecheck locally for the function
@cython.nonecheck(False)
def func():
    cdef MyClass obj = None
    try:
        # Turn nonecheck on again for a block
        with cython.nonecheck(True):
            print obj.myfunc() # Raises exception
    except AttributeError:
        pass
    print obj.myfunc() # Hope for a crash!
```

cdef类中的属性与常规类中的属性行为不同：
- 所有属性必须在编译时预先声明
- 属性默认只能从Cython访问（类型访问）
- 可以声明属性以将动态属性暴露给Python空间

```Cython
cdef class WaveFunction(Function):
    # Not available in Python-space:
    cdef double offset
    # Available in Python-space:      public 关键字
    cdef public double freq
    # Available in Python-space:      注解
    @property
    def period(self):
        return 1.0 / self.freq
    @period.setter                    setter 方法
    def period(self, value):
        self.freq = 1.0 / value
    <...>
```
