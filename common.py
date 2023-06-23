# Return a string describing the range between low_ym and high_ym, where each is a string
# in the format YYYYMM, with YYYY being the year and MM the month number
# If low_ym and high_ym are the same value, just return string describing low_ym
def comp_mon_range(low_ym, high_ym):
    low = low_ym[0:4] + " " + low_ym[4:6]
    if low_ym == high_ym:
        return low
    else:
        return low + " to " + high_ym[0:4] + " " + high_ym[4:6]

