#! /usr/bin/env python3

from collections import defaultdict
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
    total = 0
    data = defaultdict(list)

    for row in rows:
        if len(row) < 4:
            continue
        title = link_tpl.substitute(title=row[0], link=row[2])
        pic = pic_tpl.substitute(
            title=row[0], pic_link=get_img_link(get_id_from_link(row[2])))
        total += int(row[3])
        year = datetime.strptime(row[1], '%d.%m.%Y').year
        data[year].append(int(row[3]))
        lines.append(row_tpl.substitute(
            title=title, date=row[1], count=row[3], pic=pic))

    lines.append(row_tpl.substitute(
        title='', date='', count=f'**{total}**', pic='**ИТОГО**'))

    labels = list(map(lambda x: str(x), reversed(list(data.keys()))))
    values = list(map(lambda x: sum(data[int(x)]), labels))
    averages = list(map(lambda x: average(data[int(x)]), labels))

    with open('README.md', 'w') as fp:
        fp.write(base_tpl.substitute(data='\n'.join(
            lines), chart=get_chart(values, averages, labels)))


def get_base_template():
    return Template(
        '''Сколько раз Дмитрий Бачило произнес фразу `"тем не менее"`
----------------------------------------------------------

|   | Название видео | Дата | Тем не менее |
| - | -------------- | ---- | ------------:|
$data

$chart
''')


def get_chart(values, averages, labels):
    chart = {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Всего',
                    'backgroundColor': 'red',
                    'borderColor': 'red',
                    'data': values,
                    'fill': False,
                    'pointRadius': 1
                },
                {
                    'label': 'Среднее',
                    'backgroundColor': 'blue',
                    'borderColor': 'blue',
                    'data': averages,
                    'fill': False,
                    'pointRadius': 1
                }
            ]
        }
    }

    base64_chart = str(
        base64.b64encode(bytes(json.dumps(chart), 'utf-8')), 'utf-8')

    ch = f'https://quickchart.io/chart?c={base64_chart}&devicePixelRatio=1&encoding=base64'

    return f'![Nevertheless Chart]({ch})'


def sort_by_date(count):
    return sorted(
        count,
        key=lambda x: datetime.strptime(x[1], '%d.%m.%Y'),
        reverse=True)


def get_img_link(id):
    return f'https://img.youtube.com/vi/{id}/default.jpg'


def get_id_from_link(link):
    return re.search('/?v=(.+)$', link).groups()[0]


def average(values):
    return int(round(sum(values)/float(len(values))))


if __name__ == '__main__':
    main()
