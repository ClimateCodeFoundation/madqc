#!/usr/bin/env python3

import mad

def test_1():
    assert 2 == mad.median([1,2,3])

def main():
    for name, fn in globals().items():
        if name.startswith('test'):
            fn()

if __name__ == '__main__':
    main()
