from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware to allow requests from your frontend domain
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api")
def read_root(request: Request):
    """
    This endpoint is protected by APISIX and receives user information via headers.
    """
    # Get user information from headers set by APISIX
    username = request.headers.get("X-APISIX-Auth-Username", "Anonymous")
    
    # You can get more headers depending on your APISIX configuration
    # For example: user ID, roles, etc.
    
    return JSONResponse(content={
        "message": f"Hello, {username}! You have successfully authenticated.",
        "api_gateway_info": "This request was routed and authorized by APISIX.",
        "backend_info": "This response is from the FastAPI backend."
    })
