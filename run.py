
from iot.factory import create_app

import os
import configparser


config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join("sample.ini")))

if __name__ == "__main__":
    app = create_app()
    app.config['DEBUG'] = True
    app.config['MONGO_URI'] = config['PROD']['DB_URI']

    app.run(host='0.0.0.0', port=5000)
