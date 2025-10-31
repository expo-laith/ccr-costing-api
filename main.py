from fastapi import FastAPI
from pydantic import BaseModel
from math import ceil

app = FastAPI(title="CCR Costing Advanced API")

# ---------- Input ----------
class Dimensions(BaseModel):
    L: int
    W: int
    H: int

class Spec(BaseModel):
    quantity: int
    dimensions_mm: Dimensions
    shape: str = "box"               # box, cylinder, panel...
    material: str = "mdf"            # mdf, ply, acrylic...
    finish: str = "roller_paint"     # roller_paint, 2pac, laminate...
    complexity: float = 1.0          # 1.0 = simple, 1.3 = complex
    crates_required: str = "no"
    ownership: str = "new"

class CCR(BaseModel):
    spec: Spec

# ---------- Logic ----------
def calculate_total(spec: Spec):
    # base rates
    MATERIAL_RATES = {
        "mdf": 50,
        "ply": 70,
        "acrylic": 90
    }
    FINISH_LABOUR_MULT = {
        "roller_paint": 1.0,
        "2pac": 1.3,
        "laminate": 1.15,
        "vinyl_wrap": 1.2
    }

    LABOUR_HR_RATE = 56.11
    PAINT_COST_PER_L = 10
    PAINT_COVERAGE = 9  # m² per litre

    L, W, H = spec.dimensions_mm.L, spec.dimensions_mm.W, spec.dimensions_mm.H
    area_m2 = 2 * (L*W + L*H + W*H) / 1_000_000
    sheets = ceil(area_m2 / (2.4 * 1.2) * 1.1)
    paint_l = ceil(area_m2 / PAINT_COVERAGE)

    material_cost = sheets * MATERIAL_RATES.get(spec.material, 50)
    paint_cost = paint_l * PAINT_COST_PER_L
    labour_hours = 9 * spec.complexity * FINISH_LABOUR_MULT.get(spec.finish, 1.0)
    labour_cost = labour_hours * LABOUR_HR_RATE
    crate_cost = 430 if spec.crates_required == "yes" else 0

    total = material_cost + paint_cost + labour_cost + crate_cost
    return {
        "material_cost": round(material_cost, 2),
        "paint_cost": round(paint_cost, 2),
        "labour_cost": round(labour_cost, 2),
        "crate_cost": round(crate_cost, 2),
        "total": round(total, 2)
    }

# ---------- Endpoint ----------
@app.post("/cost/advanced-estimate")
def advanced_estimate(payload: CCR):
    result = calculate_total(payload.spec)
    return {"estimate": result, "currency": "AUD"}
