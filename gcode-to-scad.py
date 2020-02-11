#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import math, sys
import argparse

DEBUG = False

if not DEBUG:
    parser = argparse.ArgumentParser(prog='gcode-to-scad.py')
    parser.add_argument('-d', '--tooldiam', type=float, metavar='mm', help='tool diameter in millimeters', default=4.0)
    parser.add_argument('-f', '--facets', type=int, metavar='N', help='number of facets to render tool with', default=8)
    parser.add_argument('-s', '--seglen', type=float, metavar='mm', help='max length of interpolated arc segments (G2/G3) in mm', default=2)
    parser.add_argument('--sx', type=float, metavar='mm', help='width of stock  (in X dimension, mm)', default=1000)
    parser.add_argument('--sy', type=float, metavar='mm', help='depth of stock  (in Y dimension, mm)', default=1000)
    parser.add_argument('--sz', type=float, metavar='mm', help='height of stock (in Z dimension, mm)', default=10)
    parser.add_argument('input', help='input .gcode file')
    parser.add_argument('output', help='output .scad file')
    args = parser.parse_args()
    
    inputFilename = args.input
    outputFilename = args.output
    toolDiam = args.tooldiam
    toolFacets = args.facets
    arcSegmentLength = args.seglen
    
    stockX = args.sx
    stockY = args.sy
    stockZ = args.sz
else:
    inputFilename = 'in.gcode'
    outputFilename = 'out.scad'
    
    toolDiam = 4.0 # mm
    toolFacets = 8
    
    arcSegmentLength = 2.0 # mm
    
    stockX = 1000 # mm
    stockY = 1000 # mm
    stockZ =   10 # mm

###############################################################################

cx = 0.0
cy = 0.0
cz = 0.0

mx = 0.0
my = 0.0
mz = 0.0

ox = 0.0
oy = 0.0
oz = 0.0

toolLength = stockZ + 10
movements = []

def isclose(a, b, atol=1e-6):
    return abs(a - b) <= atol

def parseParams(params):
    result = {}
    for param in params:
        try:
            name = param[0]
            value = float(param[1:])
            result[name] = value
        except:
            print('Could not parse parameter:', param)
    return result
        
        
with open(inputFilename, 'r') as f:
    for rawLine in f:
        assert(isclose(mx, ox + cx))
        assert(isclose(my, oy + cy))
        assert(isclose(mz, oz + cz))

        line = rawLine.split(';', 1)[0].strip().upper()
        if len(line) > 0:
            parts = line.split(' ')
            command = parts[0]
            params = parts[1:]
            code = int(command[1:])
            if command == 'G90':
                pass
            elif command == 'G91':
                print('Error: relative positioning (G91) is not supported')
                sys.exit(1)
            elif command == 'G92':
                p = parseParams(params)
                if 'X' in p:
                    cx = p['X']
                    ox = mx - cx
                if 'Y' in p:
                    cy = p['Y']
                    oy = my - cy
                if 'Z' in p:
                    cz = p['Z']
                    oz = mz - cz
            elif command.startswith('G') and 0 <= code and code <= 3:
                p = parseParams(params)
                nx = p.get('X', cx)
                ny = p.get('Y', cy)
                nz = p.get('Z', cz)
                
                if code == 2 or code == 3:
                    centerX = cx + p['I']
                    centerY = cy + p['J']
                    startRadius = math.sqrt((cx - centerX) ** 2 + (cy - centerY) ** 2)
                    endRadius   = math.sqrt((nx - centerX) ** 2 + (ny - centerY) ** 2)
                    assert(isclose(startRadius, endRadius, atol=0.001))
                    
                    radius = startRadius
                    circumference = math.pi * radius * 2
                    numFacets = circumference / float(arcSegmentLength)
                    deltaAngle = math.pi * 2 / numFacets
                    
                    angle = math.atan2(cy - centerY, cx - centerX)
                    while angle < 0: angle += math.pi * 2
                    while angle >= math.pi * 2: angle -= math.pi * 2
                    
                    endAngle = math.atan2(ny - centerY, nx - centerX)
                    while endAngle < 0: endAngle += math.pi * 2
                    while endAngle >= math.pi * 2: endAngle -= math.pi * 2

                    if code == 2:
                        if endAngle > angle: angle += math.pi * 2
                        deltaAngle *= -1
                    else:
                        if endAngle < angle: endAngle += math.pi * 2
                        
                    angle += deltaAngle
                    while (code == 2 and angle > endAngle) or (code == 3 and angle < endAngle):
                        ax = math.cos(angle) * radius
                        ay = math.sin(angle) * radius
                        movements += [(mx + (centerX - cx) + ax, my + (centerY - cy) + ay, mz)]
                        angle += deltaAngle
                    
                mx += nx - cx
                my += ny - cy
                mz += nz - cz
                cx = nx
                cy = ny
                cz = nz
                movements += [(mx, my, mz)]
                
            else:
                print('Skipping unknown line:', rawLine.strip())

with open(outputFilename, 'w') as f:
    print('module tool() { cylinder(h=%.3f,r1=%.3f,r2=%.3f,center=false,$fn=%d); }' % (toolLength, toolDiam / 2.0, toolDiam / 2.0, toolFacets), file=f)
    print('module stock() { translate(v=[%.3f,%.3f,%.3f]) cube(size=[%.3f,%.3f,%.3f],center=false); }' % (-stockX / 2.0, -stockY / 2.0, -stockZ, stockX, stockY, stockZ), file=f)
    print('difference() {', file=f)
    print('  stock();', file=f)
    print('  union() {', file=f)
    for (sx, sy, sz), (ex, ey, ez) in zip(movements, movements[1:]):
        print('    hull() { translate(v=[%.3f,%.3f,%.3f]) tool(); translate(v=[%.3f,%.3f,%.3f]) tool();  }' % (sx, sy, sz, ex, ey, ez), file=f)
    print('  }', file=f)
    print('}', file=f)
