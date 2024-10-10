from fastapi import FastAPI

app = FastAPI()

# API function that takes path parameters
@app.get("/add/{b}/{a}")
async def add_numbers(b: int, a: int):
    result = a + b
    return {"b": b, "a": a, "result": result}
