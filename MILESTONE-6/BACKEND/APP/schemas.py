from pydantic import BaseModel

class InputData(BaseModel):
    price: float
    cost: float
    discount_pct: float
    inventory_units: int
    competitor_price: float
    category: int
    region: int
    seasonality: int
    weather_condition: int
    month: int
    day_of_week: int