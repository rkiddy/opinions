
import re
from flask import request, url_for
from sqlalchemy import create_engine, inspect

engine = create_engine('mysql+pymysql://ray:alexna11@localhost/ca_courts')
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


def build(param, extra_param=None):

    context = dict()

    if param == 'unpublished':
        sql = """
        select filed_date, count(0) from opinions
            group by filed_date order by filed_date desc;
        """

        rows = conn.execute(sql).fetchall()

        cols = {'pub_date': 0, 'pub_date_count': 1}
        context['unpublished'] = fill_in_table(rows, cols)

        return context

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

        return context

