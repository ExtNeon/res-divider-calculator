#!/bin/python
import math
import locale
locale = locale.getdefaultlocale()[0]
exec(open("./languages/" + locale).read())

TARGET_RES_DIV_POWER = 0.01
MAX_COEFFICIENTS_DIVERGENCE = 0.0015

file_list_of_resistances = open('./res_list.txt')
lines = [line.strip().capitalize() for line in file_list_of_resistances]
res_list = []
for line in lines:
    if line.find('ω') > 0:
        line = line.removesuffix('ω')
    if line.find('r') > 0:
        line = line.removesuffix('r');
    if line.find('k') > 0:
        line = line.removesuffix('k')
        res_list.append(float(line.strip()) * 1000.)
    elif line.find('m') > 0:
        line = line.removesuffix('m')
        res_list.append(float(line.strip()) * 1000000.)
    elif line.find('g') > 0:
        line = line.removesuffix('g')
        res_list.append(float(line.strip()) * 1000000000.)
    else:
        res_list.append(float(line.strip()))

#res_list = [float(line.strip()) for line in file_list_of_resistances]
res_list.sort()
def calculate_additive_resistors(match_resistance):
    global res_list
    additive_resistors_val = [-1, -1]
    additive_resistors_max_correlation = math.inf
    for first_index in range(0, len(res_list)):
        if  abs(match_resistance - res_list[first_index]) < additive_resistors_max_correlation:
            additive_resistors_max_correlation = abs(match_resistance - res_list[first_index])
            additive_resistors_val = [first_index, -1]
        for second_index in range(0, len(res_list)):
            if abs(match_resistance - (res_list[first_index] + res_list[second_index])) < \
                    additive_resistors_max_correlation:
                additive_resistors_max_correlation = abs(match_resistance -
                                                         (res_list[first_index] + res_list[second_index]))
                additive_resistors_val = [first_index, second_index]
    return additive_resistors_val


def format_resistance(res):
    if 1000 <= res < 1000000:
        return str(round(res / 1000., 3)) + 'KΩ'
    elif res < 1000:
        return str(res) + 'Ω'
    else:
        return str(round(res / 1000000, 4)) + 'MΩ'


def format_additive_resistors(match_resistance):
    global res_list
    additive_resistors_combination = calculate_additive_resistors(match_resistance)
    if additive_resistors_combination[1] == -1:
        return format_resistance(res_list[additive_resistors_combination[0]])
    elif additive_resistors_combination[1] >= 0:
        return format_resistance(res_list[additive_resistors_combination[0]]) + ' и ' \
               + format_resistance(res_list[additive_resistors_combination[1]])
    elif additive_resistors_combination[0] == -1:
        return str_cannot_pick


print(str_list_loaded.format(len(res_list))+'\n')
# Резервируем переменные, чтобы они работали в этой зоне видимости
top_v = 0
bottom_v = 0

try:
    top_v = float(input(str_enter_input_voltage))
    bottom_v = float(input(str_enter_output_voltage))
    max_divergence = input(str_enter_max_coef_divergence)
    max_power = input(str_enter_max_heat_dissipation)
    try:
        MAX_COEFFICIENTS_DIVERGENCE = float(max_divergence)
    except ValueError:
        print(str_coef_divergence_set_default.format(MAX_COEFFICIENTS_DIVERGENCE))
    try:
        TARGET_RES_DIV_POWER = float(max_power)/1000.
    except ValueError:
        print(str_max_heat_dissipation_set_default.format(TARGET_RES_DIV_POWER*1000.))
    if top_v < bottom_v:
        print(str_error_output_gr_input)
        exit(1)
    elif top_v == bottom_v:
        print(str_error_output_eq_input)
        exit(2)
    elif top_v <= 0 or bottom_v <= 0:
        print(str_error_zero)
        exit(403)
except ValueError:
    print(str_error_nan)
    exit(1)

min_input_impedance = pow(top_v, 2) / TARGET_RES_DIV_POWER
if min_input_impedance > res_list[len(res_list) - 1] * 2:
    print(str_trouble_impedance_too_high.format(format_resistance(min_input_impedance)))
    exit(1)

coef_diff = math.inf
coef_target = top_v / bottom_v
i_top_res = 0
i_bottom_res = 0
for i in range(0, len(res_list)):
    for j in range(0, len(res_list)):
        if res_list[i] != 0 and res_list[j] != 0 and res_list[i] + res_list[j] > min_input_impedance and \
                abs(coef_target - (res_list[i] / res_list[j] + 1)) < coef_diff:
            coef_diff = abs(coef_target - (res_list[i] / res_list[j] + 1))
            i_top_res = i
            i_bottom_res = j
resistance_top = res_list[i_top_res]
resistance_bottom = res_list[i_bottom_res]
result_coef = resistance_top / resistance_bottom + 1
ideal_bottom_res = (resistance_top * bottom_v) / (top_v - bottom_v)
ideal_top_res = resistance_bottom * (top_v - bottom_v) / bottom_v
str_top_resistor = format_resistance(resistance_top)
str_bottom_resistor = format_resistance(resistance_bottom)

if coef_diff > MAX_COEFFICIENTS_DIVERGENCE:
    print(str_coef_diff_exceeded_threshold.format(round(coef_diff, 4), MAX_COEFFICIENTS_DIVERGENCE))
    if result_coef < coef_target:
        # Коэффициент надо повысить, добавив ещё сопротивления к верхнему резистору
        res_combination = calculate_additive_resistors(ideal_top_res - res_list[i_top_res])
        if res_combination[0] > -1:
            resistance_top += res_list[res_combination[0]]
            if res_combination[1] > -1:
                resistance_top += res_list[res_combination[1]]
			       
            str_top_resistor = str_combination.format(str_top_resistor, format_additive_resistors(ideal_top_res - res_list[i_top_res]), format_resistance(resistance_top))
    else:
        res_combination = calculate_additive_resistors(ideal_bottom_res - res_list[i_bottom_res])
        if res_combination[0] > -1:
            resistance_bottom += res_list[res_combination[0]]
            if res_combination[1] > -1:
                resistance_bottom += res_list[res_combination[1]]
            str_bottom_resistor = str_combination.format(str_bottom_resistor, format_additive_resistors(ideal_bottom_res - res_list[i_bottom_res]), format_resistance(resistance_bottom))

    result_coef = resistance_top / resistance_bottom + 1
    coef_diff = abs(coef_target - result_coef)

result_coef_divergence = ""
if coef_diff > 0.001:
    result_coef_divergence = str_result_coef_divergence.format(round(100 * coef_diff / coef_target, 3))

print(str_result.format(round(coef_target, 3), round(result_coef, 3),
                                                   result_coef_divergence,
                                                   str_top_resistor, str_bottom_resistor,
                                                   round(top_v / (resistance_top + resistance_bottom) * 1000., 2),
                                                   round(pow(top_v, 2) / (resistance_top + resistance_bottom) * 1000., 2),
                                                   round(top_v / result_coef, 4)))
