fld f0, 0(x1)
fld f1, 0(x2)
fld f2, 0(x3)
fmul f0, f0, f0 
fmul f1, f1, f1 
fmul f2, f2, f2 
fadd f3, f0, f1 
fadd f3, f3, f2 
fld f4, 0(x0) 
fdiv f3, f3, f4 
fsd f3, 0(x4)