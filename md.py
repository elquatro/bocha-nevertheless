from string import Template
import json

def main():
    with open('template.md') as fp:
        base_tpl = Template(fp.read())

    with open('count.json') as fp:
        count = json.load(fp)

    row_tpl = Template('| $title | $date | $count |')
    link_tpl = Template('[$title]($link)')

    lines = []

    for r in count:
        title = link_tpl.substitute(title=r[0], link=r[2])
        lines.append(row_tpl.substitute(title=title, date=r[1], count=r[3]))

    with open('README.md', 'w') as fp:
        fp.write(base_tpl.substitute(data='\n'.join(lines)))

if __name__ == '__main__':
    main()
