import io

from fastapi import FastAPI
from loguru import logger
from starlette.responses import StreamingResponse

import config

logger.info('start logging...')

app = FastAPI()


@app.get("/svg")
@logger.catch
def get_svg(*, id: str):
    with open(config.SVG_PATH / id, 'rb') as f:
        return StreamingResponse(io.BytesIO(f.read()), media_type="image/png")
