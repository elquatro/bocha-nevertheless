#! /usr/bin/env python3

from string import Template
from datetime import datetime
import csv
import re


def main():
    base_tpl = get_base_template()

    count = []
    with open('data.csv', newline='') as fd:
        reader = csv.reader(fd)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            count.append(row)

    count = sort_by_date(count)

    row_tpl = Template('| $pic | $title | $date | $count |')
    link_tpl = Template('[$title]($link)')
    pic_tpl = Template('![$title]($pic_link)')

    lines = []
    total = 0

    for r in count:
        if len(r) < 4:
            continue
        title = link_tpl.substitute(title=r[0], link=r[2])
        pic = pic_tpl.substitute(
            title=r[0], pic_link=get_img_link(get_id_from_link(r[2])))
        total += int(r[3])
        lines.append(row_tpl.substitute(
            title=title, date=r[1], count=r[3], pic=pic))

    lines.append(row_tpl.substitute(
        title='**ИТОГО**', date='', count='**%s**' % total, pic=''))

    with open('README.md', 'w') as fp:
        fp.write(base_tpl.substitute(data='\n'.join(lines)))


def get_base_template():
    return Template(
        '''Сколько раз Дмитрий Бачило произнес фразу `"тем не менее"`
----------------------------------------------------------

|   | Название видео | Дата | Тем не менее |
| - | -------------- | ---- | ------------:|
$data
''')


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
