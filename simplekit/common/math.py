from __future__ import division


def percent(value, total, precision=2):
    """
    Scale percent
    :param value: class:`int`, class:`float`
    :param total: class:`int`, class:`float`
    :param precision: class:`int`, the precision of result
    :return: class:`float`
    """
    value = value or 0
    total = total or 0
    if not total:
        return 0.0
    if not isinstance(precision, int) or precision < 0:
        precision = 2
    quotient = value / total
    quotient = round(quotient * 100, precision)
    return quotient
