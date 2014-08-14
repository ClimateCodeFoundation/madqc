#!/usr/bin/env python3

import itertools
import os

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
                        v /= 100.0
                        data["{:04d}{:02d}".format(year, m+1)] = v
            yield record

def median(values):
    """
    Return the value of the median element.
    When len(values) is even, two elements are nearest "the
    middle"; the one with even index is returned.
    """

    s = sorted(values)
    h = len(s)/2.0
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


def main(argv=None):
    import glob

    pattern = os.path.expanduser("~/.local/share/data/isti")
    globs = glob.glob(os.path.join(pattern, "merged*.dat"))
    dat_file = sorted(globs)[-1]

    with open(dat_file) as dat:
        for record in ghcnm_stations(dat):
            print(record.id, record.element,
              "{:6.2f}".format(median(record.data.values())),
              mad(record.data.values()))

if __name__ == '__main__':
    main()
        
