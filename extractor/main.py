from fastapi import FastAPI, Request

from nltk.corpus import stopwords
import nltk
import re

import asyncpg

app = FastAPI()

nltk.download('stopwords')
stopwordlist = stopwords.words('english') + stopwords.words('russian')

@app.post('/api/extractor')
async def extract(request: Request):
    """Current json format:
    {
        'message': str
        'pages': [
            {
                'id':  int,
                'url': str,
                'content': {
                    'title':   str,
                    'meta':    list[str],
                    'headers': list[str]
                }
            },
            ...
        ]
    }
    """
    pg_conn = await asyncpg.connect(
        user='user',
        password='12345',
        database='urls_db',
        host='database'
    )
    try:
        data = await request.json()
        for page in data['pages']:
            raw_content = ""
            for title, meta, headers in page['content']:
                raw_content += re.sub(r'[,.;:/\'\"\`~!?%$#№&*_\[\]\(\)\{\}\\]', '', str(title + ' ' + ' '.join(meta) + ' '.join(headers)).lower()) + ' '
            
            raw_content = re.sub(r'\n\r\t', ' ', raw_content).split(' ')
            keywords = [word for word in raw_content if word not in stopwordlist]

            await pg_conn.execute(
                "INSERT INTO urls (url, keywords) VALUES ($1, $2)",
                page['url'], keywords
            )
    finally:
        await pg_conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)