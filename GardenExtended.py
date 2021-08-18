class A(object):
    def __init__(self, a):
        self.a = a
    def f(self):
        print("AAAA")
    def g(self):
        print("gggggggg")

class A(A):
    def __init__(self, a, b):
        super(B, self).__init__(a)
        self.b=b
    def f(self):
        print("BBBBB")

o = B(1,2)
o.g()