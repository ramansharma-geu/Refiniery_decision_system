"""
WSGI entry point for RDIS.
Use this for production deployments (Gunicorn, uWSGI, etc.)
"""
import os
from app import create_app

config_overrides = {}
if os.environ.get('FLASK_ENV') == 'production':
    config_overrides['DEBUG'] = False

app = create_app(config_overrides)

if __name__ == '__main__':
    app.run()
