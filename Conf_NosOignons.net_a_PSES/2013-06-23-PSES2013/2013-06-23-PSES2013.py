#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-
#
# Diversity graph generator for the THSF2013 presentation
# Copyright 2013 © Lunar <lunar@torproject.org>
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

import itertools
import json
import math
import operator
import os
import os.path
import re
import subprocess
import sys

import matplotlib
# Avoid X11 based backend
matplotlib.use('Agg')
from matplotlib import pyplot, transforms, patches
from matplotlib.ticker import FuncFormatter
import numpy

COMPASS_DIR = os.environ['COMPASS_DIR']
COMPASS = os.path.join(COMPASS_DIR, 'compass.py')
sys.path = [COMPASS_DIR] + sys.path
import compass

PUBLISHED_AT = json.load(file(os.path.join(COMPASS_DIR, 'details.json')))['relays_published']

def draw_percent(data, item_getter, y_format, name_getter, name, desc, *args, **kwargs):
    points = map(lambda relay: (item_getter(relay), name_getter(relay)), data)
    points.sort(key=operator.itemgetter(0), reverse=True)

    top_count = min(100, len(points))
    max_nick_len = 20
    min_pies = 3
    max_pie_frac = 2.5

    max_y = sum(map(operator.itemgetter(0), points))

    ax_dist = pyplot.subplot(1,1,1)
    ax_dist.yaxis.set_major_formatter(FuncFormatter(lambda x, _: y_format % x))
    ax_dist.set_xticks(range(0, top_count, 10))
    ax_dist.set_yticks(range(0, int(math.ceil(max_y)), min(200, int(math.ceil(max_y) / 10))))

    plot_total = 0
    pie_others = 0
    plot_xs, plot_ys = [], []
    pie_xs, pie_labels = [], []
    for value, nick in points:
        if len(plot_ys) < top_count:
            plot_total += value
            plot_ys.append(plot_total)
            plot_xs.append(len(plot_ys))
        if len(pie_xs) < min_pies or value > max_pie_frac * (max_y / 100.0):
            pie_xs.append(value)
            if len(nick) > max_nick_len:
                nick = nick[:max_nick_len - 3] + u'…'
            pie_labels.append(nick)
        else:
            pie_others += value
    pie_labels.append('%d others' % (len(points) - len(pie_xs),))
    pie_xs.append(pie_others)

    colors = []
    explode = []
    for i in range(len(pie_xs) - 1):
        color = (0, 1 - pie_xs[i] / max_y, 0)
        colors.append(color)
        pyplot.plot(plot_xs[i], plot_ys[i], 'ko', color=color)

    remaining_color = (0.7, 1, 0.7)
    pyplot.plot(plot_xs[len(colors):], plot_ys[len(colors):], 'ko', color=remaining_color)
    colors.append(remaining_color)
    pyplot.xlabel('Top-x %s by %s' % (name, desc))
    pyplot.ylabel('Total %s' % (desc,))

    if len(points) > top_count:
        pyplot.annotate(('%d %s remaining (' + y_format + ')') % (len(points) - top_count, name, max_y - plot_total),
                        (top_count, plot_ys[-1] + (max_y - plot_ys[-1]) / 2), xycoords='data',
                        horizontalalignment='right', verticalalignment='center',
                        xytext=(-50, 0),
                        textcoords='offset points', size='small',
                        arrowprops=dict(arrowstyle='fancy', facecolor='white'))

    pyplot.xlim(0, plot_xs[-1])
    pyplot.ylim(0, max_y)

    def pie_label_formater(x, _):
        if x > 5.0:
            return y_format % (x * max_y / 100.0)
        else:
            return ''

    pie_left, pie_bottom, pie_width, pie_height = 0.45, 0.1, 0.3, 0.3 * (16.0/10.0) # keep aspect ratio
    ax_pie = pyplot.axes((pie_left, pie_bottom, pie_width, pie_height))
    explode = [0.05 for _ in pie_xs]
    ax_pie.pie(pie_xs, labels=pie_labels,
               autopct=FuncFormatter(pie_label_formater),
               colors=colors, explode=explode,
               labeldistance=1.1)

def draw_number(data, *args, **kwargs):
    item_getter = lambda relay: int(re.match(r'\(([0-9]*) .*', relay['fp']).group(1))
    y_format = '%d relays'
    draw_percent(data, item_getter, y_format, *args, **kwargs)

def draw_cw(data, *args, **kwargs):
    item_getter = operator.itemgetter('cw')
    y_format = '%1.1f%%'
    draw_percent(data, item_getter, y_format, *args, **kwargs)

def draw_p_exit(data, *args, **kwargs):
    item_getter = operator.itemgetter('p_exit')
    y_format = '%1.1f%%'
    data = [relay for relay in data if relay.get('p_exit', -1) > 0.0]
    draw_percent(data, item_getter, y_format, *args, **kwargs)

def run_compass(args=[]):
    return json.loads(subprocess.check_output([COMPASS, '--json', '--top=-1'] + args))['results']

def compute_network_families():
    return run_compass(['--by-network-family'])

def compute_as():
    return run_compass(['--by-as'])

def compute_countries():
    return run_compass(['--by-country'])

FAMILY_MAP = {
        u'∀ Torservers.net': (
            'assk',
            'assk2',
            'bolobolo1',
            'bouazizi',
            'chomsky',
            'dorrisdeebrown',
            'gorz',
            'herngaard',
            'manning1',
            'manning2',
            'morales',
            'rainbowwarrior',
            'raskin',
            'sofia',
            'torserversNet1',
            'wannabe',
            'zeller',
      ), u'∀ DFRI': (
            'DFRI0',
            'DFRI1',
            'DFRI3',
            'Kiruna',
            'maatuska',
            'ndnr1',
      ), u'∀ TorLand': (
            'TorLand1',
            'TorLand2',
      ), u'∀ Random Person': (
            'Revisited',
            'Windmill2',
            'Riviera2',
            'Anthracite',
            'Paint',
            'Hymen2',
            'Frontier2',
            'Samo',
            'Lithium2',
            'AndBeans',
            'Barbecue',
            'Firebird',
            'Frontier',
            'WallyWorld',
            'Falcon',
            'Bohemian',
            'CzechMate',
            'Monk',
            'NoWay',
            'MrSnow',
            'BearNecessities',
            'BearlyLegal',
            'Stefan3',
            'BikiniTeam',
            '2ndCity',
            'Dragon',
      ), u'∀ Team Cymru': (
            'GoldDragon',
            'Ramsgate',
            'BigBoy',
            'RedDragon',
            'GreenDragon',
            'WhiteDragon',
      ),
    }

def compute_operators():
    # Compass does not support grouping by family, see #6662.
    # Let's just hack something right here for our needs.
    data = json.load(open(os.path.join(COMPASS_DIR, 'details.json')))

    print ''
    relays = {}
    for relay in data['relays']:
        if not relay.get('running', False):
            continue
        relay['nick'] = relay['nickname']
        relay['cw'] = relay.get('consensus_weight_fraction', 0) * 100.0
        relay['adv_bw'] = relay.get('advertised_bandwidth_fraction', 0) * 100.0
        relay['p_guard'] = relay.get('guard_probability', 0) * 100.0
        relay['p_middle'] = relay.get('middle_probability', 0) * 100.0
        relay['p_exit'] = relay.get('exit_probability', 0) * 100.0
        if 'Named' in relay['flags']:
            nick = relay['nick']
            for family_name, family_nicks in FAMILY_MAP.iteritems():
                if nick in family_nicks:
                    nick = family_name
                    break
        else:
            nick = '$' + relay['fingerprint']
        relays[relay['fingerprint']] = (relay, nick, compass.FamilyFilter(relay['fingerprint'], data['relays']))
        print '\r%d loaded relays' % len(relays),

    fields = ('cw', 'adv_bw', 'p_guard', 'p_middle', 'p_exit')

    print ''
    ops = []
    while len(relays) > 0:
        _, d = relays.popitem()
        r1, nick, f = d 

        op = { 'count': 1 }
        op['nick'] = nick
        for field in fields:
            op[field] = r1[field]
        for fingerprint in list(relays.iterkeys()):
            if not f.accept(relays[fingerprint][0]):
                continue
            r2, _, _ = relays.pop(fingerprint)
            for field in fields:
                op[field] += r2[field]
            op['count'] += 1
        op['fp'] = '(%d relays)' % op['count']
        ops.append(op)

        print '\r%d relays remaining' % len(relays),
    print ''
    return ops

DATA_TYPES = {
        'network_families': {
            'data_func': compute_network_families,
            'draw_args': {
                'name': 'network families',
                'name_getter': operator.itemgetter('nick'),
                'bounds': (10, 50, -1),
            },
     }, 'as': {
            'data_func': compute_as,
            'draw_args': {
                'name': 'AS',
                'name_getter': operator.itemgetter('as_info'),
                'bounds': (5, 20, -1),
            },
     }, 'countries': {
            'data_func': compute_countries,
            'draw_args': {
                'name': 'countries',
                'name_getter': operator.itemgetter('cc'),
                'bounds': (2, 7, -1),
            },
     }, 'operators': {
            'data_func': compute_operators,
            'draw_args': {
                'name': 'operators',
                'name_getter': operator.itemgetter('nick'),
                'bounds': (10, 50, -1),
            },
     },
  }

DRAWINGS = {
        'number': {
            'draw_func': draw_number,
            'desc': 'number of relays',
     }, 'cw': {
            'draw_func': draw_cw,
            'desc': 'consensus weight',
     }, 'p_exit': {
            'draw_func': draw_p_exit,
            'desc': 'exit probability',
     },
  }

def main():
    for type_name, type_data in DATA_TYPES.iteritems():
        for drawing_name, drawing_data in DRAWINGS.iteritems():
            image_name = '%s_by_%s' % (type_name, drawing_name)
            image_path = sys.argv[1]
            if image_name in image_path:

                data = type_data['data_func']()

                pyplot.figure(figsize=(16,10))
                pyplot.grid(True)
                pyplot.title('Diversity by %s (%s) @ %s' % (type_data['draw_args']['name'], drawing_data['desc'], PUBLISHED_AT))

                kwargs = {}
                kwargs.update(type_data['draw_args'])
                kwargs.update(desc=drawing_data['desc'])
                drawing_data['draw_func'](data, **kwargs)

                pyplot.savefig(image_path, bbox_inches='tight', pad_inches=0.1)
                sys.exit(0)

    sys.stderr.write('Not found!\n')
    sys.exit(1)

if __name__ == '__main__':
    main()
