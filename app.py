from app.socket_handler import APP
from app.arduino_connection import init_connection
import uvicorn

if __name__ == '__main__':
    uvicorn.run(APP, host='127.0.0.1', port=5000)
