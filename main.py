from fastapi import FastAPI
from pydantic import BaseModel
from math import ceil

app = FastAPI(title="CCR Costing Simple API")

# ---------- Input ----------
class Dimensions(BaseModel):
    L: int
    W: int
    H: int

class Spec(BaseModel):
    quantity: int
    dimensions_mm: Dimensions
    finish: str
    crates_required: str  # "yes" | "no"
    ownership: str        # "new" | "rental" | "client_owned"

class CCR(BaseModel):
    spec: Spec

# ---------- Logic ----------
def calculate_total(spec: Spec):
    MDF_COST = 50
    LABOUR_HR_RATE = 56.11
    PAINT_COST_PER_L = 10
    PAINT_COVERAGE = 9  # m² per litre

    L, W, H = spec.dimensions_mm.L, spec.dimensions_mm.W, spec.dimensions_mm.H
    area_m2 = 2 * (L*W + L*H + W*H) / 1_000_000
    sheets = ceil(area_m2 / (2.4 * 1.2) * 1.1)    # simple sheet estimate with 10% waste
    paint_l = ceil(area_m2 / PAINT_COVERAGE)      # litres needed (rounded up)

    materials = sheets * MDF_COST
    paint = paint_l * PAINT_COST_PER_L
    labour = 9 * LABOUR_HR_RATE                   # simple default hours for small items
    crate = 0
    if spec.crates_required == "yes":
        crate = 430  # flat crate allowance for MVP

    total = materials + paint + labour + crate
    return {
        "materials": round(materials, 2),
        "paint": round(paint, 2),
        "labour": round(labour, 2),
        "crate": round(crate, 2),
        "total": round(total, 2)
    }

# ---------- Endpoint ----------
@app.post("/cost/simple-estimate")
def simple_estimate(payload: CCR):
    result = calculate_total(payload.spec)
    return {"estimate": result, "currency": "AUD"}
