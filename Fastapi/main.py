from fastapi import FastAPI, Path, HTTPException, Query, status
import json
from pydantic import BaseModel, computed_field, Field
from typing import Annotated, Literal, Optional
app = FastAPI()


def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)

    return data   



def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f, indent=4)


@app.get("/")
def hello():
    return {"message": "Patient Management"}

@app.get("/about")
def ideA():
    return{"message":"We keep the details about patient, so you can focus on improving your health"}

@app.get('/view')
def view():
    data = load_data()

    return data    

@app.get('/patient/{patient_id}')
def view_patient(
    patient_id: str = Path(
        ...,
        description="ID of the patient in the DB",
        example="P001",
    ),
):
    # load all patients
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    # return {'error': 'patient not found'}    
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get('/sort')
def sort_patients(
    sort_by: str = Query(
        ...,
        description="Field to sort by",
        example="BMI,Height,Weight",
    ),
    sort_order: str = Query(
        'asc',
        description="Sort order",
        example="asc",
    ),
):
    valid_fields = ['bmi', 'height', 'weight']

    if sort_by not in valid_fields:
        raise HTTPException(status_code = 400, detail = f'Invalid field{valid_fields}')

    if sort_order not in ['asc','desc']:
        raise HTTPException(status_code=400, detail= 'Invalid order select one from [ASC] or [DESC]')

    data = load_data()

    sorted_order = True if sort_order == 'desc' else False

    sorted_data = sorted(data.values(), key = lambda x: x.get(sort_by,0),reverse = sorted_order)  

    return sorted_data



@computed_field
@property
def bmi(self) -> float:
    return round(self.weight / (self.height ** 2), 2)
    

@computed_field
@property
def verdict(self) -> str:
    if self.bmi < 18.5:
        return 'Underweight'
    elif self.bmi >= 18.5 and self.bmi < 24.9:
        return 'Normal'
    elif self.bmi >= 25 and self.bmi < 29.9:
        return 'Overweight'
    else:
        return 'Obese'


class Patient(BaseModel):
    id: Annotated[str, Field(...,description="ID of the patient",example="P001")]
    name: Annotated[str, Field(..., description="Name of the patient",example="John Doe")]
    city: Annotated[str, Field(..., description="City of the patient",example="New York")]
    age: Annotated[int, Field(..., description="Age of the patient",example=30)]
    gender: Annotated[Literal['male','female'], Field(..., description="Gender of the patient",example="Male")]
    height: Annotated[float, Field(..., description="Height of the patient in Ft",example=1.75)]
    weight: Annotated[float, Field(description="Weight of the patient",example=70.0)]




class UpdatePatient(BaseModel):
    name: Annotated[Optional[str], Field(default=None, description="Updated Name of the patient")]
    city: Annotated[Optional[ str], Field(default=None, description="Updated City of the patient")]
    age: Annotated[Optional[int], Field(default=None, description="Updated Age of the patient")]
    gender: Annotated[Optional[Literal['male','female']], Field(default=None, description="Updated Gender of the patient")]
    height: Annotated[Optional[float], Field(default=None, description="Updated Height of the patient in Ft")]
    weight: Annotated[Optional[float], Field(default=None, description="Updated Weight of the patient")]




@app.post('/add', status_code=status.HTTP_201_CREATED)
def add_patient(patient: Patient):
    #load existing data
    data = load_data()

    #check if patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail= 'Patient already exists')

    #add new patient
    data[patient.id] = patient.model_dump(exclude=['id'])

    # with open('patients.json', 'w') as f:
    #     json.dump(data, f, indent=4)
    save_data(data)

    return {'message': 'Patient added successfully'}




@app.put('/update/{patient_id}')
def update_patient(patient_id: str, patient_update: UpdatePatient):


        data = load_data()

        if patient_id not in data:
            raise HTTPException(status_code=404, detail= 'Patient not found')
        
        existing_patient = data[patient_id]

        updated_patient_info = patient_update.model_dump(exclude_none=True)

        for key, value in updated_patient_info.items():
            existing_patient[key] = value

#        existing_patient_info = -> pydantic object -> updated bmi + verdict -> pydanctic object -> dict 
        existing_patient['id'] = patient_id
        patient_pydantic_object = Patient(**existing_patient)

        #pydantic object -> dict
        existing_patient = patient_pydantic_object.model_dump(exclude='id')

        data[patient_id] = existing_patient
        save_data(data)

        return {'message': 'Patient updated successfully'}

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail= 'Patient not found')
    del data[patient_id]
    save_data(data)
    return {'message': 'Patient deleted successfully'}









