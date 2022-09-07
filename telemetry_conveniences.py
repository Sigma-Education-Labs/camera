import datetime as dt
import sgp4
from telemetry_functions import days2mdhms, jday

class _UTC(dt.tzinfo):
    'UTC'
    zero = dt.timedelta(0)
    def __repr__(self):
        return 'UTC'
    def dst(self, datetime):
        return self.zero
    def tzname(self, datetime):
        return 'UTC'
    def utcoffset(self, datetime):
        return self.zero

UTC = _UTC()

def jday_datetime(datetime):
    u = datetime.astimezone(UTC)
    year = u.year
    mon = u.month
    day = u.day
    hr = u.hour
    minute = u.minute
    sec = u.second + u.microsecond * 1e-6

    return jday(year, mon, day, hr, minute, sec)

def sat_epoch_datetime(sat):
    """Return the epoch of the given satellite as a Python datetime."""
    year = sat.epochyr
    year += 1900 + (year < 57) * 100
    days = sat.epochdays
    month, day, hour, minute, second = days2mdhms(year, days)
    if month == 12 and day > 31:  # for that time the ISS epoch was "Dec 32"
        year += 1
        month = 1
        day -= 31
    second, fraction = divmod(second, 1.0)
    second = int(second)
    micro = int(fraction * 1e6)
    return dt.datetime(year, month, day, hour, minute, second, micro, UTC)

_ATTRIBUTES = None

def dump_satrec(sat, sat2=None):
    """Yield lines that list the attributes of one or two satellites."""

    global _ATTRIBUTES
    if _ATTRIBUTES is None:
        _ATTRIBUTES = []
        for line in sgp4.__doc__.splitlines():
            if line.endswith('*'):
                title = line.strip('*')
                _ATTRIBUTES.append(title)
            elif line.startswith('| ``'):
                pieces = line.split('``')
                _ATTRIBUTES.append(pieces[1])
                i = 2
                while pieces[i] == ', ':
                    _ATTRIBUTES.append(pieces[i+1])
                    i += 2

    for item in _ATTRIBUTES:
        if item[0].isupper():
            title = item
            yield '\n'
            yield '# -------- {0} --------\n'.format(title)
        else:
            name = item
            value = getattr(sat, item, '(not set)')
            line = '{0} = {1!r}\n'.format(item, value)
            if sat2 is not None:
                value2 = getattr(sat2, name, '(not set)')
                verdict = '==' if (value == value2) else '!='
                line = '{0:39} {1} {2!r}\n'.format(line[:-1], verdict, value2)
            yield line
