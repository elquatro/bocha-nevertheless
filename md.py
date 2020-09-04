#! /usr/bin/env python3

from string import Template
from datetime import datetime
import csv
import re
import json
import base64


def main():
    base_tpl = get_base_template()

    rows = []
    with open('data.csv', newline='') as fd:
        reader = csv.reader(fd)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            rows.append(row)

    rows = sort_by_date(rows)

    row_tpl = Template('| $pic | $title | $date | $count |')
    link_tpl = Template('[$title]($link)')
    pic_tpl = Template('![$title]($pic_link)')

    lines = []
    labels = []
    values = []
    total = 0

    for row in rows:
        if len(row) < 4:
            continue
        title = link_tpl.substitute(title=row[0], link=row[2])
        pic = pic_tpl.substitute(
            title=row[0], pic_link=get_img_link(get_id_from_link(row[2])))
        total += int(row[3])
        year = datetime.strptime(row[1], '%d.%m.%Y').year
        lines.append(row_tpl.substitute(
            title=title, date=row[1], count=row[3], pic=pic))
        values.append(int(row[3]))
        labels.append(str(year))

    lines.append(row_tpl.substitute(
        title='', date='', count='**%s**' % total, pic='**ИТОГО**'))

    values.reverse()
    labels.reverse()

    with open('README.md', 'w') as fp:
        fp.write(base_tpl.substitute(data='\n'.join(
            lines), chart=get_chart(values, labels)))


def get_base_template():
    return Template(
        '''Сколько раз Дмитрий Бачило произнес фразу `"тем не менее"`
----------------------------------------------------------

|   | Название видео | Дата | Тем не менее |
| - | -------------- | ---- | ------------:|
$data

$chart
''')


def get_chart(values, labels):
    chart = {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': [
                {
                    'data': values,
                    'fill': False,
                    'pointRadius': 1
                }
            ]
        },
        'options': {
            'legend': {
                'display': False
            }
        }
    }

    ch = "https://quickchart.io/chart?c=%s&devicePixelRatio=1&encoding=base64" % str(
        base64.b64encode(bytes(json.dumps(chart), "utf-8")), "utf-8")

    return '![Nevertheless Chart](%s)' % ch


def sort_by_date(count):
    return sorted(
        count,
        key=lambda x: datetime.strptime(x[1], '%d.%m.%Y'),
        reverse=True)


def get_img_link(id):
    return 'https://img.youtube.com/vi/%s/hqdefault.jpg' % id


def get_id_from_link(link):
    return re.search('/?v=(.+)$', link).groups()[0]


if __name__ == '__main__':
    main()
