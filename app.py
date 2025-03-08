import os
import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from controllers.apis import router as APISRouter

from middlewares.request_context import RequestContextMiddleware


app = FastAPI()

load_dotenv()
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):

    response_payload: dict = {
        "transactionUrn": request.state.urn,
        "responseMessage": "Bad or missing input.",
        "responseKey": "error_bad_input",
        "errors": exc.errors()
    }
    return JSONResponse(
        status_code=400,
        content=response_payload,
    )

@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.add_middleware(
    middleware_class=TrustedHostMiddleware, 
    allowed_hosts=["*"]
)
origins = [
    "http://localhost:5173",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

logger.info("Initialising middleware stack")
app.add_middleware(RequestContextMiddleware)
logger.info("Initialised middleware stack")

logger.info("Initialising routers")
# APIS ROUTER
app.include_router(APISRouter)
logger.info("Initialised routers")

if __name__ == '__main__':
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)