#!/usr/bin/env python3
import lxml.etree as et
import pandas
import numpy
import itertools
from io import StringIO
import matplotlib.pyplot as plt

# unnecessary, but implicitly used:
#   import cssselect


def calc_diffs(p):
    # very wrong. should use haversine?
    p['dist'] = numpy.sqrt(
         (p['lat'] - p['lat'].shift())**2 +
         (p['lon'] - p['lon'].shift())**2)

    p['elv_delta'] = numpy.append(0, numpy.diff(p['alt']))
    return(p)


def read_tracklog(f):
    e = et.parse(f)

    c = None
    for x in e.getroot().cssselect('coordinates'):
        name = x.getparent().getparent().find('name')
        if getattr(name, 'text', '') == 'Tracklog':
            c = x.text
            break

    if not c:
        return(None)

    p = pandas.read_csv(StringIO(c.replace(" ", "\n")))
    p.columns = ['lat', 'lon', 'alt']
    return(p)


def major_changes(p, cutoff=30):
    p = calc_diffs(p)
    deltas = [sum(list(k)) for i, k in
              itertools.groupby(p.elv_delta, key=lambda x: x > 0)]
    major = list(filter(lambda x: abs(x) > cutoff, deltas))
    return(major)


w = read_tracklog("Will 2017-11-11_20-36.kml")
e = read_tracklog("Emily 2017-11-11_18-57.kml")

print(major_changes(w))
print(major_changes(e,10))

# plot
fig = plt.figure(figsize=(7, 3.5))
w['alt'].plot()
e['alt'].plot()
plt.title(r'$\Delta$ elevation')
plt.legend(['will', 'Emily'])
fig.savefig('elv.png')
plt.show(block=False)
