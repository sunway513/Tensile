import Tensile.Tensile as Tensile
 
def test_double_complex_asm_nt(tmpdir):
 Tensile.Tensile([Tensile.TensileTestPath("pre_checkin/double_complex/double_complex_asm_nt.yaml"), tmpdir.strpath])

def test_double_complex_asm_tn(tmpdir):
 Tensile.Tensile([Tensile.TensileTestPath("pre_checkin/double_complex/double_complex_asm_tn.yaml"), tmpdir.strpath])

def test_double_complex_asm_nn(tmpdir):
 Tensile.Tensile([Tensile.TensileTestPath("pre_checkin/double_complex/double_complex_asm_nn.yaml"), tmpdir.strpath])

def test_double_complex_asm_tt(tmpdir):
 Tensile.Tensile([Tensile.TensileTestPath("pre_checkin/double_complex/double_complex_asm_tt.yaml"), tmpdir.strpath])
 
def test_double_complex_asm_nc(tmpdir):
 Tensile.Tensile([Tensile.TensileTestPath("pre_checkin/double_complex/double_complex_asm_nc.yaml"), tmpdir.strpath])
 
def test_double_complex_asm_cn(tmpdir):
 Tensile.Tensile([Tensile.TensileTestPath("pre_checkin/double_complex/double_complex_asm_cn.yaml"), tmpdir.strpath])
 
def test_double_complex_asm_ct(tmpdir):
 Tensile.Tensile([Tensile.TensileTestPath("pre_checkin/double_complex/double_complex_asm_ct.yaml"), tmpdir.strpath])
 
def test_double_complex_asm_tc(tmpdir):
 Tensile.Tensile([Tensile.TensileTestPath("pre_checkin/double_complex/double_complex_asm_tc.yaml"), tmpdir.strpath])
 
def test_double_complex_asm_cc(tmpdir):
 Tensile.Tensile([Tensile.TensileTestPath("pre_checkin/double_complex/double_complex_asm_cc.yaml"), tmpdir.strpath])

