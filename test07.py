from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from pydatacolor import DataColorState, DataColorModel
from lofigui import print, buffer


VERSION = "0.2.15 2022-05-12"

app = FastAPI()


class Controller:
    """Async controller class for datacolour, but also combined with model"""

    def __init__(self):
        self.model = DataColorModel()
        self.poll = False
        self.poll_timer = 0

    def state_dict(self, d):
        def buttons_up(selection):
            def success(name):
                if name in selection:
                    d[f"{name}_class"] = "is-success"
                else:
                    d[f"{name}_class"] = "is-success is-light"

            def danger(name):
                if name in selection:
                    d[f"{name}_class"] = "is-success"
                else:
                    d[f"{name}_class"] = "is-danger is-light"

            success("connect")
            danger("cancel")
            danger("calibrate")
            danger("measure")

        self.state = f"{self.model.state}"
        if self.model.state in [DataColorState.Disconnected, DataColorState.Failed]:
            self.poll = False
            buttons_up(["connect"])
        elif self.model.state in [DataColorState.NotFound]:
            self.poll = False
            buttons_up(["connect"])
        elif self.model.state in [DataColorState.Connecting]:
            self.poll = True
            buttons_up(["cancel"])
        elif self.model.state in [DataColorState.Connected]:
            self.poll = False
            buttons_up(["calibrate"])
        elif self.model.state in [DataColorState.Calibrating]:
            self.poll = True
            buttons_up(["cancel"])
        elif self.model.state in [DataColorState.Calibrated]:
            self.poll = False
            buttons_up(["calibrate", "measure"])
        elif self.model.state in [DataColorState.Measureing]:
            self.poll = True
            buttons_up(["cancel"])
        elif self.model.state in [DataColorState.Measured]:
            self.poll = False
            buttons_up(["calibrate", "measure"])
        else:  # self.datacolor and self.datacolor.dev:
            buttons_up(["connect"])
        if self.poll and self.poll_count > 100:
            print(">100 run so going to timeout")
            self.poll = False
            self.model.state = DataColorState.Failed
        if self.poll:
            self.poll_count += 1
            d[
                "refresh"
            ] = '<meta http-equiv="refresh" content="1">'  # Poll while running
        else:
            self.poll_count = 0
            d["refresh"] = ""
        d["results"] = buffer()
        d["status"] = controller.state
        d["version"] = VERSION
        return d


controller = Controller()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "test07.html", controller.state_dict({"request": request})
    )


@app.post("/connect", response_class=HTMLResponse)
async def connect(background_tasks: BackgroundTasks):
    background_tasks.add_task(controller.model.connect)
    return '<head>  <meta http-equiv="Refresh" content="0; URL=/" /></head>'


@app.post("/stop", response_class=HTMLResponse)
async def stop(request: Request):
    controller.model.stop()
    return '<head>  <meta http-equiv="Refresh" content="0; URL=/" /></head>'


@app.post("/calibrate", response_class=HTMLResponse)
async def connect(background_tasks: BackgroundTasks):
    background_tasks.add_task(controller.model.calibrate)
    return '<head>  <meta http-equiv="Refresh" content="0; URL=/" /></head>'


@app.post("/measure", response_class=HTMLResponse)
async def connect(background_tasks: BackgroundTasks):
    background_tasks.add_task(controller.model.measure)
    return '<head>  <meta http-equiv="Refresh" content="0; URL=/" /></head>'


@app.get("/favicon.ico", response_class=HTMLResponse)
async def connect(background_tasks: BackgroundTasks):
    return FileResponse("images/favicon.ico")


if __name__ == "__main__":
    uvicorn.run("test07:app", host="127.0.0.1", port=1340, reload=True)
