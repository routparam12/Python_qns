from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, computed_field, Field
from typing import Annotated, Literal
import pickle
import pandas as pd




# import the ML model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

app = FastAPI()

tier_1_cities = {"Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Pune"}
tier_2_cities = {"Lucknow", "Jaipur", "Indore", "Bhopal", "Coimbatore", "Patna", "Nagpur"}

# pydantic model to validate incoming data
class UserInput(BaseModel):
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the user")]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the user")]
    height: Annotated[float, Field(..., gt=0, description="Height of the user in meters")]
    income_lpa: Annotated[float, Field(..., description="User annual income in LPA")]
    smoker: Annotated[bool, Field(..., description="Is user a smoker")]
    city: Annotated[str, Field(..., description="The city user belongs to")]
    occupation: Annotated[
        Literal[
            'retired',
            'freelancer',
            'student',
            'government_job',
            'business_owner',
            'unemployed',
            'private_job',
        ],
        Field(..., description="Occupation of user"),
    ]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        if self.smoker and self.bmi > 30:
            return "high"
        if self.smoker or self.bmi > 27:
            return "medium"
        return "low"

    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 25:
            return "Young"
        if self.age < 45:
            return "Adult"
        if self.age < 60:
            return "Middle_Age"
        return "Senior"

    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        if self.city in tier_2_cities:
            return 2
        return 3






# -- now we will create the predict endpoint
@app.post("/predict")
def predict_premium(data: UserInput):
    input_df = pd.DataFrame(
        [
            {
                "bmi": data.bmi,
                "age_group": data.age_group,
                "lifestyle_risk": data.lifestyle_risk,
                "city_tier": data.city_tier,
                "income_lpa": data.income_lpa,
                "occupation": data.occupation,
            }
        ]
    )
    prediction = model.predict(input_df)[0]

    return JSONResponse(status_code=200, content={"predicted_category": str(prediction)})