from fastapi import Body, Request

from common import application, call


app = application("master")


@app.get("/status")
def status():
    result = {}
    for service in ("storage", "collector", "ml"):
        try:
            result[service] = call(service, "GET", "/health").json()
        except Exception:
            result[service] = {"status": "unavailable"}
    return result


@app.post("/collect")
def collect():
    return call("collector", "POST", "/collect").json()


@app.get("/videos")
def videos():
    return call("storage", "GET", "/records/videos").json()


@app.get("/batch")
def batch(request: Request):
    return call("collector", "GET", "/batch", params=request.query_params).json()


@app.get("/models")
def models():
    return call("ml", "GET", "/models").json()


@app.post("/models", status_code=201)
def create_model(body: dict = Body(...)):
    return call("ml", "POST", "/models", json=body).json()


@app.get("/models/{model_id}")
def summary(model_id: str):
    return call("ml", "GET", "/models/" + model_id).json()


@app.post("/models/{model_id}/train", status_code=202)
def train(model_id: str, body: dict = Body(...)):
    return call("ml", "POST", f"/models/{model_id}/train", json=body).json()


@app.get("/runs")
def runs():
    return call("ml", "GET", "/runs").json()


@app.post("/experiments")
def experiment(body: dict = Body(...)):
    return call("ml", "POST", "/experiments", json=body).json()
