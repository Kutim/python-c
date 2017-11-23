from libc.math cimport sin

cpdef double f(double x):
    return sin(x*x)