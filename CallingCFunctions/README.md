
## 1.调用 C 的函数

在Cython 的 `Includes/` 下包含了一些c 语言的库 如 `libc`、`libcpp`、`cpython`、`numpy`、`posix`。在IDE 下使用 `Cython.Includes.库名.文件名.函数` 来查看相应函数是否存在。以调用 C 语言中 `math` 库的 `sin` 函数为例：

```Python
# demo.pyx

from libc.math cimport sin

cpdef double f(double x):     # 官方文档使用 cdef ，python 是无法调到的，因此，在这里使用了 cpdef
    return sin(x*x)
```

```Python
# setup.py

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

ext_modules=[
    Extension("demo",
              sources=["demo.pyx"],
              libraries=["m"] # Unix-like specific  mac不需要添加使用的系统库，在一些 linux 上需要添加 库
    )
]

setup(
  name = "demo",
  ext_modules = cythonize(ext_modules)
)
```

```Python
# main.py

if __name__=="__main__":
    from demo import f
    print(f(100))
```

```Python
# teststdlib.pyx

from libc.stdlib cimport atoi

cpdef parse_charptr_to_py_int(char* s):   # oops！ 此处在调用时类型报错 TypeError: expected bytes
    assert s is not NULL, "byte string value is NULL"
    return atoi(s)   # note: atoi() has no error detection!
```

```Python
# setup_teststdlib.py

from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("teststdlib.pyx"),
)

```

## 2. 外部声明（External declarations）

在使用 cython 默认没有封装的库时，我们必须自己声明，例如：
```Python
# 这个声明sin()函数的方式使得Cython代码可以使用该函数，并指示Cython生成包含math.h头文件的C代码。C编译器将math.h在编译时看到原始声明，但是Cython不会解析“math.h”并需要单独的定义。

cdef extern from "math.h":
    double sin(double x)
```

```Python
# 使用了 cpdef 可以直接在 python 代码中访问

"""
>>> sin(0)
0.0
"""

cdef extern from "math.h":
    cpdef double sin(double x)
```
当这个声明（cpdef）出现在.pxd 属于Cython模块的文件中时（即具有相同名称，请参阅在Cython模块之间共享声明），您将得到相同的结果。这允许在其他Cython模块中重用C声明，同时仍然在这个特定的模块中提供一个自动生成的Python包装器。


## 3. 命名参数

c 和 cython 都支持不带参数名的函数声明.如：

```Python
cdef extern from "string.h":
    char* strstr(const char*, const char*)
```

但这会妨碍 Cython 以 关键字参数的方式调用，因此，应使用如下格式：

```python
cdef extern from "string.h":
    char* strstr(const char *haystack, const char *needle)
```
调用时使用如下格式：
```Python
cdef char* data = "hfvcakdfagbcffvschvxcdfgccbcfhvgcsnfxjh"

pos = strstr(needle='akd', haystack=data)
print pos != NULL
```
请注意，稍后更改现有参数名称是一种向后不兼容的API修改，就像Python代码一样。因此，如果为外部C或C ++函数提供自己的声明，通常值得花费额外的努力来选择其参数的名称。
