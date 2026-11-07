def create_app():
    from flask import Flask, request

    from app.config import Config
    from app.database import Base, engine
    from app.routes.api import api_bp
    from app.routes.web import web_bp

    app = Flask(__name__)
    app.config.from_object(Config)
    Base.metadata.create_all(engine)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.before_request
    def log_request():
        app.logger.info("%s %s", request.method, request.path)

    return app
