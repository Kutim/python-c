# 在 pycharm 下，重命名为 setup.py。或者使用 命令行  python setup_fib.py build_ext --inplace
from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("fib.pyx"),
)
