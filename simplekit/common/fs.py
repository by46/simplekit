def sizeof_fmt(num):

    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if num < 1024.0:
            if not unit:
                return str(num)
            return "%3.1f%s" % (num, unit)
        num /= 1024.0
    return "%.1f%s" % (num, 'Y')
