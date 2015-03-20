#!/usr/bin/env python3

"""mad.py [--help] [--progress] [tavg.dat]"""

import itertools
import json
import math
import os
import sys

def station_id(line):
    return line[:11]

def get_element(line):
    return line[15:19]

def get_year(line):
    return int(line[11:15])

class Record(object):
    def __init__(self, **k):
        self.__dict__.update(**k)

    def __repr__(self):
        return "Record({})".format(", ".join(
          "{}={!r}".format(k,v) for k,v in self.__dict__.items()))

def ghcnm_stations(inp):
    for id, lines in itertools.groupby(inp, station_id):
        # Guaranteed stable, is it?
        by_elem = sorted(lines, key=get_element)
        for element, lines in itertools.groupby(by_elem, get_element):
            data = {}
            record = Record(element=element, id=id, data=data)
            for line in lines:
                year = get_year(line)
                for m in range(12):
                    v = int(line[19+m*8:24+m*8])
                    if v != -9999:
                        data["{:04d}{:02d}".format(year, m+1)] = v
            yield record

def ghcnm_write_station(record, out):
    if not record.data:
        return
    MISSING_YEAR = [-9999]*12
    min_year = int(min(record.data)[:4])
    max_year = int(max(record.data)[:4])
    for year in range(min_year, max_year+1):
        vs = [record.data.get("{}{:02d}".format(year, m+1), -9999)
          for m in range(12)]
        if vs == MISSING_YEAR:
            continue

        FMT = "{:5d}   "*12
        fmt_vs = FMT.format(*vs)
        out.write("{}{}{}{}\n".format(record.id, year,
          record.element, fmt_vs))


def median(values):
    """
    Return the value of the median element.
    When len(values) is even, two elements are nearest "the
    middle"; the one with even index is returned.
    """

    s = sorted(values)
    h = (len(s)-1)/2.0
    n = int(h)
    if n != h:
        n = int(h+0.5)&~1
    return s[n]

def deviation(values):
    """
    Each value is converted to its _deviation_, which is the
    value with the median value subtracted.
    """
    
    m = median(values)
    return [v - m for v in values]

def mad(values):
    """
    The median of the absolute deviations.
    """

    return median(abs(d) for d in deviation(values))


def mad_r(record, months_required=20):
    """
    Convert the .data of `record` into a "r-scores", where
    the r-score is the datum's (signed) deviation (from the median)
    divided by the MAD (see mad()).
    
    Each of the 12 calendar months are treated
    separately, and at least `months_required` values for any
    particular month are required; if there are fewer then all
    the data for that calendar month is invalidated.

    A fresh dict is returned.
    """

    new = {}
    for s in ["{:02d}".format(m+1) for m in range(12)]:
        values = [v for k,v in record.data.items() if k.endswith(s)]
        if len(values) < months_required:
            continue
        mad_v = mad(values)
        median_v = median(values)
        for k, v in record.data.items():
            if k.endswith(s):
                if mad_v:
                    new[k] = (v-median_v)/mad_v
                else:
                    if v == median_v:
                        new[k] = 0.0
                    else:
                        new[k] = math.copysign(float("inf"), (v-median_v))
    return new

def treat(dat, progress=None, log=None, qc=None):
    r_threshold = 5.0

    for record in ghcnm_stations(dat):
        if progress:
            print(record.id, record.element,
              "{}".format(median(record.data.values())),
              mad(record.data.values()), file=progress)
        r_data = mad_r(record)
        json.dump(dict(id=record.id, element=record.element,
          r=r_data), log)
        log.write("\n")

        good_months = [k for k,v in r_data.items()
          if abs(v) < r_threshold]
        good_data = dict((k,record.data[k]) for k in good_months)
        record.data = good_data
        ghcnm_write_station(record, qc)

def main(argv=None):
    import getopt
    import glob

    if argv is None:
        argv = sys.argv

    progress = None

    opts, arg = getopt.getopt(argv[1:], '', ['help', 'progress'])
    for k,v in opts:
        if k == '--help':
            print(__doc__)
            return 0
        if k == '--progress':
            progress = sys.stdout
            continue

    if not arg:
        pattern = os.path.expanduser("~/.local/share/data/isti")
        globs = glob.glob(os.path.join(pattern, "merged*.dat"))
        dat_file = sorted(globs)[-1]
        sys.stderr.write("using {}...\n".format(dat_file))
    else:
        (dat_file,) = arg

    qc_file = os.path.basename(dat_file)
    if qc_file.endswith(".dat"):
        qc_file = qc_file[:-4]
    qc_file = qc_file + ".qc.dat"

    with open(dat_file) as dat, open(qc_file, 'w') as qc:
        treat(dat, progress=progress, log=sys.stdout, qc=qc)

if __name__ == '__main__':
    sys.exit(main())
