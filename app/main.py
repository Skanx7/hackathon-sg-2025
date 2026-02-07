from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import database_router, metadata_router, prices_router, nlp_router, news_router, sentiment_router, correlation_router
import uvicorn
import logging
app = FastAPI(
    title="CAC40 Sentiment-Price Correlation API",
    description="API for analyzing correlations between sentiment and price variations for CAC40 stocks",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(database_router)
app.include_router(metadata_router)
app.include_router(prices_router)
app.include_router(nlp_router)
app.include_router(news_router)
app.include_router(sentiment_router)
app.include_router(correlation_router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
