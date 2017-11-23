
## 1. Cython 概述

Cython的基本性质可以概括如下：Cython是带有C数据类型的Python。

Cython是Python：几乎所有的Python代码都是有效的Cython代码。（有一些限制，但是这个近似值现在可以使用）.Cython编译器会将它转换成C代码，这个C代码可以等效地调用Python / C API。

但是Cython远不止于此，因为参数和变量可以声明为C数据类型。操纵Python值和C值的代码可以自由混合，只要有可能就自动进行转换。Python操作的引用计数维护和错误检查也是自动的，甚至在操作C数据的过程中，Python的异常处理工具（包括try-except和try-finally语句）的全部功能也可以使用。


## 2. Cython 入门

由于Cython几乎可以接受任何有效的Python源文件，因此开始使用最困难的事情之一就是弄清楚如何编译扩展。

```Python
# helloworld.pyx

print ("Hello World")
```

- 方法一： 使用 `setup.py`

```Python
# setup.py

from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("helloworld.pyx")
)
```
在 pycharm 中 `"Tools"`-> `"Run setup.py Task.."` -> `"build_ext"` -> `"--inplace"`

- 方法二：使用 `pyximport`

  适用于不使用 c 库或特殊构建。

```Python
# main.py 不产生 .c、.o、.so、.html

import pyximport; pyximport.install()
import helloworld

```

```Python
# main.py 产生 .c、.o、.so、.html

import pyximport; pyximport.install()
import subprocess
subprocess.call(["cython", "-a", "helloworld.pyx"])

import helloworld

```

方法一种的步骤等价于 `$ python setup.py build_ext --inplace`

从Cython 0.11开始，`pyximport`模块还支持普通Python模块的实验编译。这使您可以在Python导入的每个.pyx和.py模块上自动运行Cython，包括标准库和已安装的软件包。Cython仍然无法编译大量的Python模块，在这种情况下，导入机制将回退到加载Python源代码模块。.py导入机制是这样安装的：

```Python
 pyximport.install(pyimport = True)
 ```
满足终端用户最好的方式是：二进制包 `wheel`

## 3. Fibonacci

python 代码块

```Python
# fib.pyx

def fib(n):
    """Print the Fibonacci series up to n."""
    a, b = 0, 1
    while b < n:
        print b,
        a, b = b, a + b
```

```Python
# setup.py

from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("fib.pyx"),
)
```
## 4. Primes

python 与 c 混合：

```Python
# primes.pyx

def primes(int kmax):
    cdef int n, k, i
    cdef int p[1000]
    result = []
    if kmax > 1000:
        kmax = 1000
    k = 0
    n = 2
    while k < kmax:
        i = 0
        while i < k and n % p[i] != 0:
            i = i + 1
        if i == k:
            p[k] = n
            k = k + 1
            result.append(n)
        n = n + 1
    return result
```

```Python
# setup.py

from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("primes.pyx"),
)
```
