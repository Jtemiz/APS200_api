from app.socket_handler import APP
import uvicorn

if __name__ == '__main__':
    uvicorn.run(APP, host='127.0.0.1', port=5000)
    #uvicorn.run(APP, host='192.168.4.1', port=5000, ssl_keyfile='./certs/aps200.key', ssl_certfile='./certs/aps200.crt')
