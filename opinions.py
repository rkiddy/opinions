
from flask import Flask
from jinja2 import Environment, PackageLoader

import data

opinions = Flask(__name__)
application = opinions

env = Environment(loader=PackageLoader('opinions', 'pages'))


# @opinions.route('/')
# def hello_world():
#     return 'Hello World'


@opinions.route('/')
def opinions_unpublished():
    main = env.get_template('unpublished.html')
    context = data.build('unpublished')
    return main.render(**context)


@opinions.route('/pub_date/<param>')
def opinions_unpublished_for_date(param):
    main = env.get_template('listed.html')
    context = data.build('pub_date', param)
    return main.render(**context)


if __name__ == '__main__':
    opinions.run()
