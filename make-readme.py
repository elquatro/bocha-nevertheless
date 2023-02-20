#! /usr/bin/env python3

from collections import defaultdict
from string import Template
from datetime import datetime
import csv
import re
import json
import base64

ENCODING = 'utf8'
DATE_FORMAT = '%d.%m.%Y'


def main():
    base_tpl = get_base_template()

    rows = []
    with open('data.csv', newline='', encoding=ENCODING) as fd:
        reader = csv.reader(fd)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            rows.append(row)

    rows = sort_by_date(rows)

    row_tpl = Template('| $pic | $title | $date | $count |')
    link_tpl = Template('[$title]($link)')
    pic_tpl = Template('![$title]($pic_link)')
    year_data_tpl = Template('| $year | $video_count | $count | $average |')

    lines = []
    total = 0
    data = defaultdict(list)

    for row in rows:
        if len(row) < 4:
            continue
        title = link_tpl.substitute(title=md_escape(row[0]), link=row[2])
        pic = pic_tpl.substitute(
            title=md_escape(row[0]), pic_link=get_img_link(get_id_from_link(row[2])))
        total += int(row[3])
        year = datetime.strptime(row[1], DATE_FORMAT).year
        data[year].append(int(row[3]))
        lines.append(row_tpl.substitute(
            title=title, date=row[1], count=row[3], pic=pic))

    lines.append(row_tpl.substitute(
        title='', date='', count=f'**{total}**', pic='**ИТОГО**'))

    labels = list(map(lambda x: str(x), reversed(list(data.keys()))))
    values = list(map(lambda x: sum(data[int(x)]), labels))
    averages = list(map(lambda x: average(data[int(x)]), labels))

    years_data_lines = []
    for year in reversed(data.keys()):
        video_count = len(data[year])
        count = sum(data[year])
        year_average = round(count / video_count, 2)
        years_data_lines.append(year_data_tpl.substitute(
            year=year, video_count=video_count, count=count, average=year_average))

    years_data = '\n'.join(years_data_lines)
    with open('README.md', 'w', encoding=ENCODING) as fp:
        fp.write(base_tpl.substitute(data='\n'.join(
            lines), chart=get_chart(values, averages, labels), badge=get_badge(total), years_data=years_data))


def get_base_template():
    return Template(
        '''Сколько раз Дмитрий Бачило произнес фразу `"тем не менее"` (Есть определенное утверждение, однако, не смотря на него, бла-бла-бла)
----------------------------------------------------------
$badge

|   | Название видео | Дата | Тем не менее |
| - | -------------- | ---- | ------------:|
$data

$chart

| Год | Видео | Тем не менее | Среднее |
| ---:| -----:| ------------:| -------:|
$years_data

''')


def get_badge(total):
    return f'![Всего](https://img.shields.io/badge/%D0%A2%D0%95%D0%9C%20%D0%9D%D0%95%20%D0%9C%D0%95%D0%9D%D0%95%D0%95-{total}-green)'


def get_chart(values, averages, labels):
    chart = {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Сумма',
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
        key=lambda x: datetime.strptime(x[1], DATE_FORMAT),
        reverse=True)


def get_img_link(id):
    return f'https://img.youtube.com/vi/{id}/default.jpg'


def get_id_from_link(link):
    return re.search('/?v=(.+)$', link).groups()[0]


def average(values):
    return int(round(sum(values)/float(len(values))))


def md_escape(text):
    return text.replace("|", r"\|")


if __name__ == '__main__':
    main()
