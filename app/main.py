from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, conint, confloat
from typing import List, Optional
from contextlib import contextmanager
from app.connection import get_db_connection

# Initialize FastAPI App
app = FastAPI()

# Pydantic models for request validation
class PatientCreate(BaseModel):
    age: conint(ge=0, le=120)  # Age must be between 0 and 120
    gender: conint(ge=0, le=1)  # 1 for male, 0 for female

class MedicalTestCreate(BaseModel):
    patient_id: int
    total_bilirubin: confloat(ge=0)  # Must be non-negative
    direct_bilirubin: confloat(ge=0)  # Must be non-negative
    alkaline_phosphatase: conint(ge=0)  # Must be non-negative
    alamine_aminotransferase: conint(ge=0)  # Must be non-negative
    aspartate_aminotransferase: conint(ge=0)  # Must be non-negative
    total_proteins: confloat(ge=0)  # Must be non-negative
    albumin: confloat(ge=0)  # Must be non-negative
    albumin_and_globulin_ratio: confloat(ge=0)  # Must be non-negative

class DiagnosisCreate(BaseModel):
    patient_id: int
    diagnosis: conint(ge=0, le=1)  # 1 for liver disease, 0 for no disease

# Response models
class PatientResponse(BaseModel):
    patient_id: int
    age: int
    gender: int

class MedicalTestResponse(BaseModel):
    test_id: int
    patient_id: int
    total_bilirubin: float
    direct_bilirubin: float
    alkaline_phosphatase: int
    alamine_aminotransferase: int
    aspartate_aminotransferase: int
    total_proteins: float
    albumin: float
    albumin_and_globulin_ratio: float

# Context manager for database connection
@contextmanager
def get_db_cursor():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        yield cursor
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()

# Create (POST) - Add a new patient
@app.post("/patients/", response_model=PatientResponse)
def create_patient(patient: PatientCreate):
    with get_db_cursor() as cursor:
        try:
            query = "INSERT INTO patients (age, gender) VALUES (%s, %s)"
            cursor.execute(query, (patient.age, patient.gender))
            patient_id = cursor.lastrowid
            return {"patient_id": patient_id, **patient.dict()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Read (GET) - Get all patients
@app.get("/patients/", response_model=List[PatientResponse])
def get_patients():
    with get_db_cursor() as cursor:
        try:
            query = "SELECT * FROM patients"
            cursor.execute(query)
            patients = cursor.fetchall()
            return patients
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Update (PUT) - Update a patient
@app.put("/patients/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient: PatientCreate):
    with get_db_cursor() as cursor:
        try:
            query = "UPDATE patients SET age = %s, gender = %s WHERE patient_id = %s"
            cursor.execute(query, (patient.age, patient.gender, patient_id))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Patient not found")
            return {"patient_id": patient_id, **patient.dict()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Delete (DELETE) - Delete a patient
@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int):
    with get_db_cursor() as cursor:
        try:
            query = "DELETE FROM patients WHERE patient_id = %s"
            cursor.execute(query, (patient_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Patient not found")
            return {"message": "Patient deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Create (POST) - Add a new medical test
@app.post("/medical_tests/", response_model=MedicalTestResponse)
def create_medical_test(test: MedicalTestCreate):
    with get_db_cursor() as cursor:
        try:
            query = """
            INSERT INTO medical_tests (
                patient_id, total_bilirubin, direct_bilirubin, alkaline_phosphatase,
                alamine_aminotransferase, aspartate_aminotransferase, total_proteins,
                albumin, albumin_and_globulin_ratio
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                test.patient_id, test.total_bilirubin, test.direct_bilirubin,
                test.alkaline_phosphatase, test.alamine_aminotransferase,
                test.aspartate_aminotransferase, test.total_proteins,
                test.albumin, test.albumin_and_globulin_ratio
            ))
            test_id = cursor.lastrowid
            return {"test_id": test_id, **test.dict()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
