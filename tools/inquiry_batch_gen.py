#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch generate inquiry letters for venues lacking knowledge."""
import json
import os
import sys
import warnings

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.constants import VENUES_FILE
from tools.inquiry_generator import generate_inquiry


from scraper.knowledge_config import get_scenarios_list


def find_missing():
    with open(VENUES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    venues = data if isinstance(data, list) else data.get('venues', [])
    missing = []
    for v in venues:
        if not v.get('active', True):
            continue
        rules = v.get('rules', {})
        has_r = rules and isinstance(rules, dict) and any(rules.values())
        any_lim = any(r.get('limitations') for r in v.get('rooms', []))
        if not has_r and not any_lim:
            missing.append(v)
    return missing


def main():
    missing = find_missing()
    scenarios = get_scenarios_list()[:2]  # only top 2 scenarios
    out_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'inquiry_letters'
    )
    os.makedirs(out_dir, exist_ok=True)
    generated = 0
    for venue in missing:
        vid = venue['id']
        vname = venue.get('name', '?')
        for scenario in scenarios:
            result = generate_inquiry(vid, scenario)
            if 'error' in result:
                print('  [ERROR] %s %s: %s' % result['error'])
                continue
            fn = '%s_%s_inquiry.txt' % (vid, scenario)
            filename = os.path.join(out_dir, fn)
            with open(filename, 'w', encoding='utf-8') as fh:
                fh.write(result['emailDraft'])
            generated += 1
            pcount = result.get('pendingCount', 0)
            acount = result.get('answeredCount', 0)
            bname = os.path.basename(filename)
            print('  %5s %25s  pending=%2d answered=%2d -> %s' % (vid, vname[:25], pcount, acount, bname))
    print('\nGenerated %d inquiry letters to %s/' % (generated, out_dir))
if __name__ == '__main__':
    main()
