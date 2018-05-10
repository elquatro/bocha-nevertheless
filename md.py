#! /usr/bin/env python3

from string import Template
from datetime import datetime
import json

def sort_by_date(count):
    return sorted(
        count,
        key=lambda x: datetime.strptime(x[1], '%d.%m.%Y'),
        reverse=True)

def main():
    with open('template.md') as fp:
        base_tpl = Template(fp.read())

    with open('count.json') as fp:
        count = json.load(fp)

    count = sort_by_date(count)

    row_tpl = Template('| $title | $date | $count |')
    link_tpl = Template('[$title]($link)')

    lines = []

    for r in count:
        if len(r) < 4:
            continue
        title = link_tpl.substitute(title=r[0], link=r[2])
        lines.append(row_tpl.substitute(title=title, date=r[1], count=r[3]))

    with open('README.md', 'w') as fp:
        fp.write(base_tpl.substitute(data='\n'.join(lines)))

if __name__ == '__main__':
    main()
