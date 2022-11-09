
import re
from flask import request, url_for
from sqlalchemy import create_engine, inspect
import subprocess
import calendar

engine = create_engine('mysql+pymysql://ray:ZEKRET_WORD@localhost/ca_courts')
conn = engine.connect()
inspector = inspect(engine)


# rows is a result cursor, columns is a dictionary or key -> column number in rows.
def fill_in_table(rows, columns):
    result = list()
    for row in rows:
        found = dict()
        for key in columns.keys():
            found[key] = row[columns[key]]
        result.append(found)
    return result


def pad_num(num):
    if num == '  ':
        return '&nbsp;&nbsp;'
    if num[0] == ' ':
        return f"&nbsp;{num[1]}"
    return num


def calendar_as_strs(month):
    parts = month.split('-')
    lines = calendar.month(int(parts[0]), int(parts[1])).split('\n')

    next_lines = list()
    next_lines.append(lines[0])

    for line in lines[1:-1]:
        one = line[0:2]
        two = line[3:5]
        three = line[6:8]
        four = line[9:11]
        five = line[12:14]
        six = line[15:17]
        seven = line[18:20]
        if one != '  ' or seven != '  ':
            next_lines.append(
                [one, two, three, four, five, six, seven]
            )

    return next_lines


def cal_strs_to_months(cal_strs, counts):
    next_months = dict()
    for month in cal_strs:

        month_str = cal_strs[month][0] + '<br/>'

        # put each of the week's date numbers together.
        for week in cal_strs[month][1:]:

            next_week = list()
            for day in week:

                if day == '  ':
                    next_week.append('&nbsp;&nbsp;')

                if re.match(r' [0-9]', day):
                    day_num = '0' + day[1]
                    if day_num in counts[month]:
                        next_week.append(f"<a href=\"/pub_date/{month}-{day_num}\">" + day + "</a>")
                    else:
                        next_week.append(f"&nbsp;{day[1]}")

                if not re.match(r' [0-9 ]', day):
                    if day in counts[month]:
                        next_week.append(f"<a href=\"/pub_date/{month}-{day}\">" + day + "</a>")
                    else:
                        next_week.append(day)

            month_str = month_str + '&nbsp;'.join(next_week) + '<br/>'

        next_months[month] = month_str

    return next_months


def build(param, extra_param=None):

    context = dict()

    if param == 'pub_date':
        sql = """
        select filed_date, docket_num, short_name, pdf_link, details_link
        from opinions where filed_date = '__PUB_DATE__'
        """

        sql = sql.replace('__PUB_DATE__', extra_param)

        rows = conn.execute(sql).fetchall()

        cols = {
            'filed_date': 0,
            'docket_num': 1,
            'short_name': 2,
            'pdf_link': 3,
            'details_link': 4
        }
        context['opinions'] = fill_in_table(rows, cols)
        context['pub_date'] = extra_param

        return context

    if param == 'unpublished':

        # get the list of months I need for a calendar.
        sql = """
        select distinct(substring(filed_date,1,7)) from opinions;
        """
        rows = conn.execute(sql).fetchall()
        months = [r[0] for r in rows]
        # print(f"months: {months}")

        sql = """
        select filed_date, count(0) as count from opinions
            group by filed_date order by filed_date desc;
        """
        rows = conn.execute(sql).fetchall()

        # get the date, broken out by month, for each date.
        counts = dict()
        for row in rows:
            month = row['filed_date'][0:7]
            date = row['filed_date'][8:]
            if month not in counts:
                counts[month] = dict()
            counts[month][date] = row['count']
        # print(f"counts: {counts}")

        cals = dict()
        for month in months:
            cals[month] = calendar_as_strs(month)
        # print(f"cals: {cals}")

        next_cals = cal_strs_to_months(cals, counts)
        # print(f"next_cals: {next_cals}")

        month_keys = sorted(list(next_cals.keys()))
        month_keys.reverse()

        context['month_keys'] = month_keys
        context['cals'] = next_cals
        return context
