from fastapi import FastAPI

app = FastAPI()

@app.get("/devices")
def get_devices():
    return [{"id": 1, "name": "Device 1", "serial": "123-abc"}]

@app.get("/health")
def health():
    return {"status": "ok"}
