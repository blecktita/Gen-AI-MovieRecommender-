from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes

from app.agents import router

load_dotenv()

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="Spin up a simple api server using LangChain's Runnable interfaces",
)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


# Adds routes to the app for using the chain under:
# /invoke
# /batch
# /stream
# /stream_events
add_routes(
    app,
    router.agent_executor,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
