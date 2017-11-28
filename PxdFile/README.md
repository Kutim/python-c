## 1. pxd 文件

除了`.pyx` 源文件之外，Cython还使用 `.pxd` （像C头文件一样的文件） ,它们包含Cython声明（有时是代码段），这些声明只能用于Cython模块。使用关键字 `cimport` 将 `pxd` 文件导入到 `pyx` 模块中。

`pxd` 文件有很多用例：
- 它们可以用于共享外部C声明。
- 它们可以包含非常适合C编译器内联的函数。这样的函数应该标记为 `inline` ，例如：
  ``` Cython
  cdef inline int int_min(int a, int b):
    return b if b < a else a
  ```
- 当伴随同名的 `pyx`文件时(不能完全同名)，他们为Cython模块提供一个Cython接口，以便其他Cython模块可以使用比Python更高效的协议与其进行通信。


在我们的集成示例中，我们可能会将其分解成pxd如下所示的文件：
- 在 `cmath.pxd` 中添加函数，其 c 的定义包含在 `math.h` 头文件中，例如 `sin`。然后，在 `integrate.pyx ` 文件中使用 `from cmath cimport sin`导入。
- 在 `integrate.pxd` 添加一个,以便Cython编写的其他模块可以定义快速自定义函数进行集成
  ```Cython
  cdef class Function:
    cpdef evaluate(self, double x)
  cpdef integrate(Function f, double a,
                double b, int N)
  ```

请注意，如果您有一个带有属性的cdef类，则必须在类声明 `pxd` 文件（如果使用）中声明属性，而不是 `pyx` 文件。编译器会告诉你这个。
