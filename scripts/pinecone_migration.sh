#!/bin/bash

# Create a new index in Pinecone Local with the specified parameters
curl -s "http://localhost:5080/indexes" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Api-Key: pclocal" \
  -H "X-Pinecone-Api-Version: 2025-01" \
  -d '{
         "name": "dense-index",
         "dimension": 512,
         "metric": "cosine",
         "spec": {
            "serverless": {
               "cloud": "aws",
               "region": "us-east-1"
            }
         }
      }'

# Upsert vectors into the index
curl -s "http://localhost:8000/api/migration/import-pinecone-index" \
  -F "file=@./data/pinecone_vectors.jsonl.gz"
