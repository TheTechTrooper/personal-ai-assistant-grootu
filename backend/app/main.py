from fastapi import FastAPI

app = FastAPI(title="Personal AI Assistant")

@app.get("/")
def root():
    return {"status": "Personal AI Assistant is running 🚀"}
