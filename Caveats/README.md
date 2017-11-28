## 1. 警告
由于Cython将C和Python语义混合在一起，有些事情可能有点令人惊讶或不直观。工作总是继续使Cython对Python用户更自然，所以这个列表将来可能会改变。
- 10**-2 == 0，而不是0.01像在Python中那样。
- 给定两个类型的int变量a和b，`a%b` 与第二个参数的符号相同（python 的语法），而不是与第一个相同（c 的语法）。通过 cdivision 指令，可以获得 c 的行为（Cython 0.12 前，默认 c 的行为）
- 需要注意无符号类型。`cdef unsigned n = 10; print(range(-n, n))` 将会打印一个空的列表，因为在传递给 `range` 函数之前，会将 `-n` 转换为一个较大的正整数 。
- Python的float类型实际上包装了C double值，Python 2.x中的 int 类型包装了C long值。
