from app import app, csrf
from app.controller.rotas import status_404,status_500,status_403
#from config import config


if __name__ == "__main__":
    csrf.init_app(app)
    app.register_error_handler(404,status_404)
    app.register_error_handler(404,status_500)
    app.register_error_handler(403,status_403)
    app.run()