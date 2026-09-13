"""Job board API — application factory."""

import copy

from flask import Flask

from .config import DevelopmentConfig


def create_app(config_object: type = DevelopmentConfig) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    from seed import SEED_JOBS

    app.extensions["jobs_store"] = copy.deepcopy(SEED_JOBS)  # a fresh copy per app

    # Imported here to avoid circular imports and import-time side effects.
    from .errors import register_error_handlers
    from .routes.health import health_bp
    from .routes.jobs import jobs_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(jobs_bp)
    register_error_handlers(app)
    return app
