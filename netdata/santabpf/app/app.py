from fastapi import FastAPI
from loguru import logger
from starlette.responses import HTMLResponse

import config

logger.info('start logging...')

app = FastAPI()


@app.get("/svg")
@logger.catch
def get_svg(*, id: str):
    with open(config.SVG_PATH / id, 'r') as f:
        return HTMLResponse(content=f.read(), status_code=200)
