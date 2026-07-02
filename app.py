from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from src.pipeline.prediction import Prediction
from pydantic import BaseModel,Field
from contextlib import asynccontextmanager
import traceback

class MessagePayload(BaseModel):
    msg: str = Field(...,description="message sent by user to llm")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FASTAPI: Initializing FinGuard Pipeline...")
    try:
        app.state.pipeline = Prediction()
        print("FASTAPI: Pipeline Ready.")
    except Exception as e:
        print("CRITICAL ERROR during initialization:")
        traceback.print_exc()
    
    yield 
    
    print("FASTAPI: Shutting down.")

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/',response_class=HTMLResponse)
async def home(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.get('/benchmark_report',response_class=HTMLResponse)
async def benchmark_report(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="benchmark_dashboard.html"
    )

@app.post("/get_response")
def get_response(payload : MessagePayload, request:Request):
    pipeline = getattr(request.app.state, "pipeline", None)   
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized. Check server logs.")

    try:
        bot_reply_object, metrics = pipeline.predict(payload.msg)

        if hasattr(bot_reply_object, 'content'):
            bot_text = bot_reply_object.content
        else:
            bot_text = str(bot_reply_object)

        if metrics.get('cyborg', 0) > 0:
            mode_used = "search"
        else:
            mode_used = "chat"

        return JSONResponse(status_code=200,content={
            "response": bot_text, 
            "metrics": metrics,
            "mode_used": mode_used
        })

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500,detail="Internal server error during prediction.")