import arrow
import asyncio
from jinja2 import Environment, FileSystemLoader

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()


class Controller:
    """Async controller class for datacolour"""

    def __init__(self):
        self.state = 0
        self.run = False
        self.queue = asyncio.Queue()
        self.results = ""  # Buffer print
        self.datacolor = None
        self.connect_state = "waiting"
        self.connect_timer = 0

    def connect(self):
        if self.connect_state == "waiting":
            self.run = True
            self.results = ""
            asyncio.create_task(model(self.queue))

    def stop(self):
        self.run = False

    def read(self):
        if self.queue.empty():
            return
        response = ""
        while not self.queue.empty():
            # Get a "work item" out of the queue.
            response += self.queue.get_nowait()
            self.queue.task_done()
        self.results += response

    async def connect_task(self):
        "Model code interacting with colorimeter"
        aprint(f"Test colorimeter")
        self.datacolor = DataColor(verbose=False)
        if self.datacolor.dev:
            aprint(f"Reset colorimeter")
            datacolor.reset()
            aprint(f"Drain colorimeter")
            datacolor.drain(verbose=False)
            aprint(f"Serial number = {datacolor.get_serial_number()}")
        aprint(f"Drain colorimeter")
        connect_state = "end"

    def state_dict(self, d):
        if self.datacolor is None:
            self.connect_state = "Waiting"
            d["connect_class"] = "is-success"
        elif self.datacolor and not self.datacolor.dev:
            status = "No Colorimeter found"
            d["connect_class"] = "is-success"
        else:  # self.datacolor and self.datacolor.dev:
            self.connect_state = "Connected"
            d["connect_class"] = "is-success is-light"
        if self.run:
            d[
                "refresh"
            ] = '<meta http-equiv="refresh" content="1">'  # Poll while running
        else:
            d["refresh"] = ""
        d["results"] = controller.results
        d["state"] = controller.connect_state
        return d


controller = Controller()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    controller.read()
    return templates.TemplateResponse(
        "test07.html", controller.state_dict({"request": request})
    )


@app.post("/connect", response_class=HTMLResponse)
async def read_item(request: Request):
    controller.connect()
    return '<head>  <meta http-equiv="Refresh" content="0; URL=/" /></head>'


async def aprint(msg):
    controller.queue.put(f"<p>{msg}</p>")
    await asyncio.sleep(0)  # Allow breaks


@app.post("/stop", response_class=HTMLResponse)
async def read_item(request: Request):
    controller.stop()
    return '<head>  <meta http-equiv="Refresh" content="0; URL=/" /></head>'


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=1340, reload=True)
