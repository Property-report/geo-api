from src import app
from src.views import general

def register_blueprints(app):
    """
    Adds all blueprint objects into the app.
    """
    app.register_blueprint(general.general)

    # All done!
    app.logger.info("Blueprints registered")
