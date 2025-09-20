import uvicorn
from fastapi import FastAPI, Request
from models import ImageReviewRequest, ImageReviewResponse, ImageReviewStatus
#from config import observer, config_handler AppConfigHandler
from config import config_handler

from app_logger import logger
import os

app = FastAPI()


@app.get("/health")
async def health(request: Request):
    logger.info(f"Health endpoint pinged from {request.client.host if request.client else None}")
    return {"status": "healthy"}

@app.post("/policy")
async def verify_images(request: ImageReviewRequest) -> ImageReviewResponse:

    container_repos = set([c.image.split("/")[0] for c in request.spec.containers])
    logger.info(f"Repositories from ImageReview: {container_repos}")
    logger.info(f"Whitelisted repositories: {config_handler.valid_repos}")
    violating_repos = container_repos - config_handler.valid_repos
    logger.info(f"Repositories violating validation rules: {violating_repos}")

    if violating_repos:
        response = ImageReviewResponse(
            apiVersion = request.apiVersion,
            status=ImageReviewStatus(allowed = False, reason = f"Violating image repositories: {", ".join(list(violating_repos))}. Allowed repositories: {", ".join(list(config_handler.valid_repos))}")
        )
    else:
        response = ImageReviewResponse(
            apiVersion = request.apiVersion,
            status=ImageReviewStatus(allowed = True)
        )

    return response

if __name__ == "__main__":
    ssl_cert_file = os.environ.get("SSL_CERTFILE",None)
    ssl_key_file = os.environ.get("SSL_KEYFILE",None)
    if not ssl_cert_file or not ssl_key_file:
        logger.critical("Both SSL_CERTFILE and SSL_KEYFILE environment variables must be defined")
        exit(1)

    uvicorn.run(
         "main:app",
         host="0.0.0.0",
         port=443,
         ssl_certfile=ssl_cert_file,
         ssl_keyfile=ssl_key_file     
    )        