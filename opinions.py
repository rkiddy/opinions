import sys

from dotenv import dotenv_values
from flask import Flask
from jinja2 import Environment, PackageLoader

sys.path.append("/home/ray/opinions/")
import data

opinions = Flask(__name__)
application = opinions
env = Environment(loader=PackageLoader('opinions', 'pages'))

cfg = dotenv_values(".env")

@opinions.route(f"/{cfg['WWW']}")
@opinions.route(f"/{cfg['WWW']}/")
def opinions_unpublished():
    main = env.get_template('unpublished.html')
    context = data.build('unpublished')
    return main.render(**context)


@opinions.route(f"/{cfg['WWW']}/pub_date/<param>")
def opinions_unpublished_for_date(param):
    main = env.get_template('listed.html')
    context = data.build('pub_date', param)
    return main.render(**context)
