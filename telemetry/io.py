"""Read the TLE earth satellite file format.

This is a minimally-edited copy of "sgp4io.cpp".

"""
import re
from datetime import datetime
from math import pi, pow
from sgp4.ext import days2mdhms, invjday, jday
from sgp4.propagation import sgp4init

INT_RE = re.compile(r'[+-]?\d*')
FLOAT_RE = re.compile(r'[+-]?\d*(\.\d*)?')

LINE1 = '1 NNNNNC NNNNNAAA NNNNN.NNNNNNNN +.NNNNNNNN +NNNNN-N +NNNNN-N N NNNNN'
LINE2 = '2 NNNNN NNN.NNNN NNN.NNNN NNNNNNN NNN.NNNN NNN.NNNN NN.NNNNNNNNNNNNNN'

error_message = """TLE format error

The Two-Line Element (TLE) format was designed for punch cards, and so
is very strict about the position of every period, space, and digit.
Your line does not quite match.  Here is the official format for line {0}
with an N where each digit should go, followed by the line you provided:

{1}
{2}"""
def twoline2rv(longstr1, longstr2, whichconst, opsmode='i', satrec=None):
    
    deg2rad  =   pi / 180.0;         #    0.0174532925199433
    xpdotp   =  1440.0 / (2.0 *pi);  #  229.1831180523293

    # For compatibility with our 1.x API, build an old Satellite object
    # if the caller fails to supply a satrec.  In that case we perform
    # the necessary import here to avoid an import loop.
    if satrec is None:
        from sgp4.model import Satellite
        satrec = Satellite()

    satrec.error = 0;

    line = longstr1.rstrip()

    if (len(line) >= 64 and
        line.startswith('1 ') and
        line[8] == ' ' and
        line[23] == '.' and
        line[32] == ' ' and
        line[34] == '.' and
        line[43] == ' ' and
        line[52] == ' ' and
        line[61] == ' ' and
        line[63] == ' '):

        _saved_satnum = satrec.satnum = _alpha5(line[2:7])
        satrec.classification = line[7] or 'U'
        satrec.intldesg = line[9:17].rstrip()
        two_digit_year = int(line[18:20])
        satrec.epochdays = float(line[20:32])
        satrec.ndot = float(line[33:43])
        satrec.nddot = float(line[44] + '.' + line[45:50])
        nexp = int(line[50:52])
        satrec.bstar = float(line[53] + '.' + line[54:59])
        ibexp = int(line[59:61])
        satrec.ephtype = line[62]
        satrec.elnum = int(line[64:68])
    else:
        raise ValueError(error_message.format(1, LINE1, line))

    line = longstr2.rstrip()

    if (len(line) >= 69 and
        line.startswith('2 ') and
        line[7] == ' ' and
        line[11] == '.' and
        line[16] == ' ' and
        line[20] == '.' and
        line[25] == ' ' and
        line[33] == ' ' and
        line[37] == '.' and
        line[42] == ' ' and
        line[46] == '.' and
        line[51] == ' '):

        satrec.satnum = _alpha5(line[2:7])
        if _saved_satnum != satrec.satnum:
            raise ValueError('Object numbers in lines 1 and 2 do not match')

        satrec.inclo = float(line[8:16])
        satrec.nodeo = float(line[17:25])
        satrec.ecco = float('0.' + line[26:33].replace(' ', '0'))
        satrec.argpo = float(line[34:42])
        satrec.mo = float(line[43:51])
        satrec.no_kozai = float(line[52:63])
        satrec.revnum = line[63:68]
    #except (AssertionError, IndexError, ValueError):
    else:
        raise ValueError(error_message.format(2, LINE2, line))

    #  ---- find no, ndot, nddot ----
    satrec.no_kozai = satrec.no_kozai / xpdotp; #   rad/min
    satrec.nddot= satrec.nddot * pow(10.0, nexp);
    satrec.bstar= satrec.bstar * pow(10.0, ibexp);

    #  ---- convert to sgp4 units ----
    satrec.ndot = satrec.ndot  / (xpdotp*1440.0);  #   ? * minperday
    satrec.nddot= satrec.nddot / (xpdotp*1440.0*1440);

    #  ---- find standard orbital elements ----
    satrec.inclo = satrec.inclo  * deg2rad;
    satrec.nodeo = satrec.nodeo  * deg2rad;
    satrec.argpo = satrec.argpo  * deg2rad;
    satrec.mo    = satrec.mo     * deg2rad;

    if two_digit_year < 57:
        year = two_digit_year + 2000;
    else:
        year = two_digit_year + 1900;

    mon,day,hr,minute,sec = days2mdhms(year, satrec.epochdays);
    sec_whole, sec_fraction = divmod(sec, 1.0)

    satrec.epochyr = year
    satrec.jdsatepoch = jday(year,mon,day,hr,minute,sec);
    try:
        satrec.epoch = datetime(year, mon, day, hr, minute, int(sec_whole),
                                int(sec_fraction * 1000000.0 // 1.0))
    except ValueError:
        # Sometimes a TLE says something like "2019 + 366.82137887 days"
        # which would be December 32nd which causes a ValueError.
        year, mon, day, hr, minute, sec = invjday(satrec.jdsatepoch)
        satrec.epoch = datetime(year, mon, day, hr, minute, int(sec_whole),
                                int(sec_fraction * 1000000.0 // 1.0))

    #  ---------------- initialize the orbit at sgp4epoch -------------------
    sgp4init(whichconst, opsmode, satrec.satnum, satrec.jdsatepoch-2433281.5, satrec.bstar,
             satrec.ndot, satrec.nddot, satrec.ecco, satrec.argpo, satrec.inclo, satrec.mo,
             satrec.no_kozai, satrec.nodeo, satrec)

    return satrec

def verify_checksum(*lines):

    for line in lines:
        checksum = line[68:69]
        if not checksum.isdigit():
            continue
        checksum = int(checksum)
        computed = compute_checksum(line)
        if checksum != computed:
            complaint = ('TLE line gives its checksum as {}'
                         ' but in fact tallies to {}:\n{}')
            raise ValueError(complaint.format(checksum, computed, line))

def fix_checksum(line):
    """Return a new copy of the TLE `line`, with the correct checksum appended.

    This discards any existing checksum at the end of the line, if a
    checksum is already present.

    """
    return line[:68].ljust(68) + str(compute_checksum(line))

def compute_checksum(line):
    """Compute the TLE checksum for the given line."""
    return sum((int(c) if c.isdigit() else c == '-') for c in line[0:68]) % 10

def _alpha5(s):
    if not s[0].isalpha():
        return int(s)
    c = s[0]
    n = ord(c) - ord('A') + 10
    n -= c > 'I'
    n -= c > 'O'
    return n * 10000 + int(s[1:])