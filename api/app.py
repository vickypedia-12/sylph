from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.project import get_project_settings
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crawler.spider import SylphSpider
from twisted.internet import reactor
import asyncio
import uvicorn
import subprocess
import json


app = FastAPI(
    title = "Sylph Search Engine",
    description="A search Engine Focused on Swiftness and Fast results",
    version="0.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

crawled_data = []

@app.get("/")
async def read_root():
    return {"Message" : "Welcome to Sylph, Your Fastest Search Engine"}


@app.post("/crawl/")
async def start_crawler(urls: List[str]):
    try:
        urls_str = ','. join(urls)
        
        outputFile  = os.path.join(os.path.dirname(__file__), 'output.jsonl')

        if os.path.exists(outputFile):
            os.remove(outputFile)
        
        outputFile  = os.path.join(os.path.dirname(__file__), 'output.jsonl')

        subprocess.call([
            'scrapy', 'crawl', 'sylph_spider', 
            '-a', f'start_urls={urls_str}', 
            '-o', outputFile
        ], restore_signals= True)
        global crawled_data
        with open(outputFile, 'r') as f:
            crawled_data = [json.loads(line) for line in f if line.strip()]

        return {
            "Message" : "Crawling Complete", 
            "Data" : crawled_data
        }
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/")
async def search(query: str, limit: Optional[int] = 10):
    if not crawled_data:
        raise HTTPException(status_code=404, detail="No crawled data available")
    
    results = []
    for item in crawled_data:
        if (query.lower() in item['title'].lower() or 
            query.lower() in item['text'].lower()):
            results.append(item)
    
    return {
        "query": query,
        "results_count": len(results),
        "results": results[:limit]
    }


@app.get("/stats/")
async def get_stats():
    return {
        "total_pages_crawled": len(crawled_data),
        "unique_domains": len(set(item['url'] for item in crawled_data))
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, ssL_keyfile = None, ssl_certfile=None)
