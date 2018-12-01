#!/usr/bin/python2

from xml import dom.minidom
import base64
import zlib
import sys

if len(sys.argv) != 3:
    print('Usage:', sys.argv[0], '<in> <out>')
    sys.exit(-1)

# parse XML document
dom = minidom.parse(sys.argv[1])

# pick it apart and do some basic validation
mapelt = dom.getElementsByTagName('map')[0]
if mapelt.getAttribute('orientation') != 'orthogonal':
    print('orientation must be orthogonal, not',
          mapelt.getAttribute('orientation'))
    sys.exit(-1)
height = int(mapelt.getAttribute('height'))
width = int(mapelt.getAttribute('width'))
if height < 1 or width < 1:
    print('map is too small:', width, 'x', height)
    sys.exit(-1)

# get tileset info
tileset = mapelt.getElementsByTagName('tileset')[0]
firstgid = int(tileset.getAttribute('firstgid'))

# get actual map data
layers = mapelt.getElementsByTagName('layer')
if len(layers) != 1:
    print('map must contain exactly one layer, not', len(layers))
    sys.exit(-1)
layer = layers[0]
if int(layer.getAttribute('height')) != height:
    print('layer height =', int(layer.getAttribute('height')),
          'does not match map height =', height)
    sys.exit(-1)
if int(layer.getAttribute('width')) != width:
    print('layer width =', int(layer.getAttribute('width')),
          'does not match map width =', width)
    sys.exit(-1)
data = layer.getElementsByTagName('data')[0]
if data.getAttribute('encoding') != 'base64':
    print('layer data must use base64 encoding, not',
          data.getAttribute('encoding'))
    sys.exit(-1)
zlibtype = data.getAttribute('compression')
if zlibtype not in ['gzip', 'zlib']:
    print('layer data must use gzip or zlib compression, not',
          data.getAttribute('compression'))
    sys.exit(-1)
data.normalize()
base64_gzip_elt = data.firstChild.data

# unencode the data
gzip_elt = base64.standard_b64decode(base64_gzip_elt)
if zlibtype == 'gzip':
    elt = zlib.decompress(gzip_elt[10:], -zlib.MAX_WBITS)
elif zlibtype == 'zlib':
    elt = zlib.decompress(gzip_elt)

if len(elt) != 4 * width * height:
    print('map data is the wrong size: found', len(elt), 'but expected',
          (4 * width * height))
    sys.exit(-1)

map = []
for y in range(height):
    line = []
    for x in range(width):
        i = 4 * (y * width + x)
        n =  ord(elt[i])
        n += ord(elt[i+1]) * 0x100
        n += ord(elt[i+2]) * 0x10000
        n += ord(elt[i+3]) * 0x1000000
        n -= firstgid
        line.append(n)
    map.append(line)

# dump output
fp = open(sys.argv[2], 'w')
fp.write('[\n')
for line in map:
    fp.write('    [')
    for n in line:
        fp.write('%3d,' % n)
    fp.write(' ],\n')
fp.write(']\n')
fp.close()
