from bbs_tool.models.schemas import BBSItem, BBSCalculationConfig
from bbs_tool.calc.is2502 import calculate_cutting_length_for_item, unit_weight_kg_per_m, bend_allowance_mm


def test_unit_weight_formula_default():
    cfg = BBSCalculationConfig()
    assert round(unit_weight_kg_per_m(16, cfg), 3) == round((16*16)/162.0, 3)


def test_straight_bar():
    cfg = BBSCalculationConfig()
    item = BBSItem(bar_mark="S1", diameter_mm=12, shape="STRAIGHT", dims_mm={"A": 3000}, quantity=2)
    assert calculate_cutting_length_for_item(item, cfg) == 3000


def test_l_90():
    cfg = BBSCalculationConfig()
    item = BBSItem(bar_mark="L1", diameter_mm=12, shape="L_90", dims_mm={"A": 500, "B": 600}, quantity=1)
    cl = calculate_cutting_length_for_item(item, cfg)
    # expected: 500 + 600 + allowance(90)
    exp = 500 + 600 + bend_allowance_mm(90, 12, cfg)
    assert round(cl, 3) == round(exp, 3)


def test_rect_stirrup():
    cfg = BBSCalculationConfig()
    item = BBSItem(bar_mark="ST1", diameter_mm=8, shape="STIRRUP_RECT", dims_mm={"A": 200, "B": 300}, quantity=5)
    cl = calculate_cutting_length_for_item(item, cfg)
    exp = 2*(200+300) + 4*bend_allowance_mm(90, 8, cfg)
    assert round(cl, 3) == round(exp, 3)