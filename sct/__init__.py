import os
from flask import Flask

def create_app(add_config=None):
    # Crear app y configuracion
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if not add_config is None:
        # cargar configuraciones adicionales a la instancia
        app.config.from_mapping(add_config)
    
    # asegurando la existencia de la carpeta instancia
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Registrando Apps

    from . import user
    app.register_blueprint(user.bp)


    return app
