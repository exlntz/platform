from fastapi import FastAPI,HTTPException

app=FastAPI()

@app.get('/')
def home() -> str:
    return 'сама платформа'

