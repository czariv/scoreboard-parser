fld f1, 0(x1)
fld f2, 0(x2)
fdiv f3, f2, f1
fadd f2, f3, f1
fadd f1, f1, f1
fsd f3, 0(x3)
fmul f4, f3, f2
fsd f4, 0(x4)
fadd f4, f1, f1
fsd f4, 0(x5)