import asyncio

class PrintContext:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.buffer = ""  # This is a results buffer

    def read(self):
        if self.queue.empty():
            return
        response = ""
        while not self.queue.empty():
            # Get a "work item" out of the queue.
            response += self.queue.get_nowait()
            self.queue.task_done()
        self.buffer += response


# Slightly more involved but allows both single threaded use and option multithreaded
_ctx = PrintContext()

def aprint(msg="", ctx=None, end="\n"):
    if ctx is None:
        ctx = _ctx
    if end == "\n":
        ctx.queue.put_nowait(f"<p>{msg}</p>")
    else:
        ctx.queue.put_nowait(f"&nbsp;{msg}&nbsp;")
    # await asyncio.sleep(0)  # Allow breaks

def abuffer(ctx=None):
    if ctx is None:
        ctx = _ctx
    ctx.read()  # drain buffer
    return ctx.buffer

def areset(ctx=None):
    if ctx is None:
        ctx = _ctx
    ctx.buffer = ""

