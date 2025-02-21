from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = FastAPI()

# Load your local model and tokenizer
MODEL_PATH = "path/to/your/local/model"  # Update this path
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, trust_remote_code=True, device_map="auto")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = 1.0
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    choices: List[dict]

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    try:
        # Prepare the input text
        conversation = ""
        for msg in request.messages:
            if msg.role == "system":
                conversation += f"System: {msg.content}\n"
            elif msg.role == "user":
                conversation += f"User: {msg.content}\n"
            elif msg.role == "assistant":
                conversation += f"Assistant: {msg.content}\n"
        
        # Generate response
        inputs = tokenizer(conversation, return_tensors="pt").to(model.device)
        outputs = model.generate(
            inputs["input_ids"],
            max_new_tokens=512,
            temperature=request.temperature,
            do_sample=True,
        )
        
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract the model's response (everything after the last "Assistant: ")
        response = response_text.split("Assistant: ")[-1].strip()
        
        return ChatResponse(
            choices=[{
                "message": {"role": "assistant", "content": response},
                "finish_reason": "stop"
            }]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 