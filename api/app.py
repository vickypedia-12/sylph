from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.project import get_project_settings
from index.src.indexer import InvertedIndex
from index.src.search import SearchEngine
from crawler.spider import SylphSpider
from twisted.internet import reactor
import asyncio
import uvicorn
import subprocess
import json
import logging
from contextlib import asynccontextmanager
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        global crawled_data, index, search_engine
        outputFile = os.path.join(os.path.dirname(__file__), 'output.jsonl')
        if os.path.exists(outputFile):
            with open(outputFile, 'r') as f:
                crawled_data = [json.loads(line) for line in f if line.strip()]
            logger.info(f"Loaded {len(crawled_data)} documents")

        index_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index', 'data')
        index_file = os.path.join(index_dir, 'index.json')
        if os.path.exists(index_file):
            index.load_index(index_file)
            logger.info(f"Loaded index with {len(index.index)} tokens from {index_file}")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

    yield

    try:
        if len(index.index) > 0:
            index_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index', 'data')
            index_file = os.path.join(index_dir, 'index.json')
            os.makedirs(index_dir, exist_ok=True)
            index.save_index(index_file)
            logger.info(f"Saved index with {len(index.index)} tokens on shutdown")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


app = FastAPI(
    title = "Sylph Search Engine",
    description="A search Engine Focused on Swiftness and Fast results",
    version="0.0.1",
    lifespnan = lifespan
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

index = InvertedIndex()
search_engine = SearchEngine(index)


@app.post("/crawl/")
async def start_crawler(urls: List[str]):
    try:
        urls_str = ','. join(urls)
        
        outputFile  = os.path.join(os.path.dirname(__file__), 'output.jsonl')

        if os.path.exists(outputFile):
            os.remove(outputFile)
        
        outputFile  = os.path.join(os.path.dirname(__file__), 'output.jsonl')
        index_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index', 'data')
        os.makedirs(index_dir, exist_ok=True)

        subprocess.call([
            'scrapy', 'crawl', 'sylph_spider', 
            '-a', f'start_urls={urls_str}', 
            '-o', outputFile
        ], restore_signals= True)


        global crawled_data
        with open(outputFile, 'r') as f:
            crawled_data = [json.loads(line) for line in f if line.strip()]

        print(f"Crawled {len(crawled_data)} documents")

        for item in crawled_data:
            print(f"Indexing document: {item['url']}")
            print(f"Text length: {len(item['text'])}")
            

        for item in crawled_data:
            index.add_document(
                doc_id=item['url'],
                text=item['text'],
                title=item['title']
            )

        index_file = os.path.join(index_dir, 'index.json')
        print(f"Saving index with {len(index.index)} tokens")
        index.save_index(index_file)


        return {
            "Message": "Crawling Complete",
            "Documents_Crawled": len(crawled_data),
            "Tokens_Indexed": len(index.index),
            "Data": crawled_data
        }
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/")
async def search(query: str, limit: Optional[int] = 10):
    if not crawled_data:
        raise HTTPException(status_code=404, detail="No crawled data available")
    
    matching_urls = search_engine.search(query, limit)
    results = [
        item for item in crawled_data
        if item['url'] in matching_urls
    ]

    return {
        "query": query,
        "results_count": len(results),
        "results": results
    }


@app.get("/stats/")
async def get_stats():
    return {
        "total_pages_crawled": len(crawled_data),
        "unique_domains": len(set(item['url'] for item in crawled_data))
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
