

def timeticks_to_str(ticks):
    """Return "days, hours, minutes, seconds and ms" string from ticks"""
    days, rem1 = divmod(ticks, 24 * 60 * 60 * 100)
    hours, rem2 = divmod(rem1, 60 * 60 * 100)
    minutes, rem3 = divmod(rem2, 60 * 100)
    seconds, milliseconds = divmod(rem3, 100)
    ending = 's' if days > 1 else ''
    days_fmt = "{} day{}, ".format(days, ending) if days > 0 else ""
    return '{}{:-02}:{:-02}:{:-02}.{:-02}'.format(days_fmt, hours, minutes, seconds, milliseconds)


print(timeticks_to_str(1199388))
