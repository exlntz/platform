from fastapi import FastAPI

app=FastAPI()

@app.get('/')
def home() -> str:
    return '1236'




posts=[
    {'id': 1, 'tittle': 'News 1', 'body': 'Text 1'},
    {'id': 2, 'tittle': 'News 2', 'body': 'Text 2'},
    {'id': 3, 'tittle': 'News 3', 'body': 'Text 3'}
]


@app.get('/items')
async def items() -> list:
    return posts

@app.get('/items/{id}')
async def items(id: int):
    for post in posts:
        if post['id'] == id:
            return post
    return 'Not found'
