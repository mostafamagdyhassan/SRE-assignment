from flask import Flask
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

@app.route("/health")
def health():
    return {"status": "ok"}, 200

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    "/metrics": make_wsgi_app()
})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
