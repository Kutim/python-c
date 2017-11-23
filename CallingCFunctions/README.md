
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
              libraries=["m"] # Unix-like specific  需要添加使用的系统库
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
