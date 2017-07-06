import unittest

class Test_cuda(unittest.TestCase):

    @unittest.skip("This test requires CUDA C compiler to be in the path.")
    def test_cuda(self):

        # https://documen.tician.de/pycuda/

        import pycuda.autoinit
        import pycuda.driver as drv
        import numpy

        from pycuda.compiler import SourceModule
        mod = SourceModule("""
        __global__ void multiply_them(float *dest, float *a, float *b)
        {
          const int i = threadIdx.x;
          dest[i] = a[i] * b[i];
        }
        """)

        multiply_them = mod.get_function("multiply_them")

        a = numpy.random.randn(400).astype(numpy.float32)
        b = numpy.random.randn(400).astype(numpy.float32)

        dest = numpy.zeros_like(a)
        multiply_them(
                drv.Out(dest), drv.In(a), drv.In(b),
                block=(400,1,1), grid=(1,1))

        print(dest-a*b)


if __name__ == '__main__':
    unittest.main()
