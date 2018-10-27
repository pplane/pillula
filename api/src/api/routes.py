from . import app

from .import v1_0

app.register_blueprint(v1_0.api, url_prefix='/v1.0')
