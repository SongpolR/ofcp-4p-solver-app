# backend/app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from solver import solve_best_arrangement

app = FastAPI(title="OFCP 4P Best Arrangement Solver")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SolveRequest(BaseModel):
    cards: list[str] = Field(..., description="Exactly 13 card codes like 'AS','TD','7H'")
    time_limit_sec: float = Field(55.0, ge=1.0, le=180.0)
    shortlist_k: int = Field(250, ge=50, le=2000)
    seed: int = Field(1, ge=0, le=999999)

class SolveResponse(BaseModel):
    best: dict
    estimated_winrate: float
    estimated_margin: float
    elapsed_sec: float
    shortlist_k: int

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/solve", response_model=SolveResponse)
def solve(req: SolveRequest):
    try:
        res = solve_best_arrangement(
            cards13_codes=req.cards,
            time_limit_sec=req.time_limit_sec,
            shortlist_k=req.shortlist_k,
            seed=req.seed,
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")