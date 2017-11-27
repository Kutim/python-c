from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

setup(
    ext_modules=cythonize([
        Extension("queue", ["queue.pyx"],
                  libraries=["calg"],                                   # 加载的库
                  library_dirs=["/opt/calg/lib"],
                  include_dirs=["/opt/calg/include/libcalg-1.0/"],      # 头文件位置
                  runtime_library_dirs=["/opt/calg/lib"])               # 运行时加载库的位置
    ])
)