#!/usr/bin/env python3

import math
import random

import mad

def test_1():
    assert 2 == mad.median([1,2,3])

def test_2():
    m = random.choice(range(1,10))
    e = random.choice(range(4))
    n = m*10**e
    
    l = list(range(n))
    random.shuffle(l)

    assert mad.median(l) in l

def test_3():
    assert 1 == mad.mad([1,2,3])

def test_4():
    m = random.choice(range(1,10))
    e = random.choice(range(4))
    n = m*10**e
    
    n |= 1 # ensure odd
    l = list(range(n))
    random.shuffle(l)

    # median is in this case also the max deviation.
    median = (n-1)/2
    assert math.ceil(median/2.0) == mad.mad(l)

def main():
    for name, fn in globals().items():
        if name.startswith('test'):
            fn()

if __name__ == '__main__':
    main()
