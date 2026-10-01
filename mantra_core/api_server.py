from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mantra_core.command_processor import CommandProcessor
import uvicorn

app = FastAPI(title="MANTRA OS API")
processor = CommandProcessor()

class CommandRequest(BaseModel):
    command: str

@app.post("/command")
async def execute_command(request: CommandRequest):
    if not request.command:
        raise HTTPException(status_code=400, detail="Command cannot be empty")
    
    result = await processor.process(request.command)
    
    if result.get("status") == "failed":
        raise HTTPException(status_code=500, detail=result.get("error"))
    
    return result

if __name__ == "__main__":
    import uvicorn
    # Use 0.0.0.0 to allow access from local network (mobile device)
    uvicorn.run(app, host="0.0.0.0", port=8000)
