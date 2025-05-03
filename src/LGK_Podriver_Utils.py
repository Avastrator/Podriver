"""
LGK_Podriver_Utils:
Longecko Podriver Utils
By Avastrator
2025-04-19 10:27:40
"""
def shindo_to_cn(i: float):
    intensity_cases = {
        0.0: "零",
        1.0: "一",
        2.0: "二",
        3.0: "三",
        4.0: "四",
        4.75: "五弱",
        5.25: "五强",
        5.75: "六弱",
        6.25: "六强",
        7: "七"
    }
    return intensity_cases.get(float(i), str(i))

def shindo_to_en(i: float):
    intensity_cases = {
        0.0: "zero",
        1.0: "one",
        2.0: "two",
        3.0: "three",
        4.0: "four",
        4.75: "five lower",
        5.25: "five upper",
        5.75: "six lower",
        6.25: "six upper",
        7: "seven"
    }
    return intensity_cases.get(float(i), str(i))