"""
FastAPI main application.
Endpoints for scraping jobs and message dispatching.
"""
from fastapi import FastAPI

app = FastAPI(
    title="RPA Scraping System",
    description="System for collecting data from multiple web sources",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "RPA Scraping System API"}


# TODO: Implement endpoints:
# POST /crawl/hockey
# POST /crawl/oscar
# POST /crawl/all
# GET  /jobs
# GET  /jobs/{job_id}
# GET  /jobs/{job_id}/results
# GET  /results/hockey
# GET  /results/oscar
