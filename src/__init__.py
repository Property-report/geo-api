from flask import Flask


app = Flask(__name__)

app.config.from_pyfile("config.py")

from src.blueprints import register_blueprints
from src.exceptions import register_exception_handlers

# Register the exception handlers
register_exception_handlers(app)

register_blueprints(app)