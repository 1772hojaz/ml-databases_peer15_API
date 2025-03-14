from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, conint, confloat
from typing import List
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
    total_bilirubin: confloat(ge=0)
    direct_bilirubin: confloat(ge=0)
    alkaline_phosphatase: conint(ge=0)
    alamine_aminotransferase: conint(ge=0)
    aspartate_aminotransferase: conint(ge=0)
    total_proteins: confloat(ge=0)
    albumin: confloat(ge=0)
    albumin_and_globulin_ratio: confloat(ge=0)

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

class DiagnosisResponse(BaseModel):
    diagnosis_id: int
    patient_id: int
    diagnosis: int

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
        query = "INSERT INTO patients (age, gender) VALUES (%s, %s)"
        cursor.execute(query, (patient.age, patient.gender))
        patient_id = cursor.lastrowid
        return {"patient_id": patient_id, **patient.dict()}

# Read (GET) - Get all patients
@app.get("/patients/", response_model=List[PatientResponse])
def get_patients():
    with get_db_cursor() as cursor:
        query = "SELECT * FROM patients"
        cursor.execute(query)
        patients = cursor.fetchall()
        return patients

# Update (PUT) - Update a patient
@app.put("/patients/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient: PatientCreate):
    with get_db_cursor() as cursor:
        query = "UPDATE patients SET age = %s, gender = %s WHERE patient_id = %s"
        cursor.execute(query, (patient.age, patient.gender, patient_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Patient not found")
        return {"patient_id": patient_id, **patient.dict()}

# Delete (DELETE) - Delete a patient
@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int):
    with get_db_cursor() as cursor:
        query = "DELETE FROM patients WHERE patient_id = %s"
        cursor.execute(query, (patient_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Patient not found")
        return {"message": "Patient deleted successfully"}

# Create (POST) - Add a new medical test
@app.post("/medical_tests/", response_model=MedicalTestResponse)
def create_medical_test(test: MedicalTestCreate):
    with get_db_cursor() as cursor:
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

# Read (GET) - Get all medical tests
@app.get("/medical_tests/", response_model=List[MedicalTestResponse])
def get_medical_tests():
    with get_db_cursor() as cursor:
        query = "SELECT * FROM medical_tests"
        cursor.execute(query)
        tests = cursor.fetchall()
        return tests

# Create (POST) - Add a new diagnosis
@app.post("/diagnosis/", response_model=DiagnosisResponse)
def create_diagnosis(diagnosis: DiagnosisCreate):
    with get_db_cursor() as cursor:
        query = "INSERT INTO diagnosis (patient_id, diagnosis) VALUES (%s, %s)"
        cursor.execute(query, (diagnosis.patient_id, diagnosis.diagnosis))
        diagnosis_id = cursor.lastrowid
        return {"diagnosis_id": diagnosis_id, **diagnosis.dict()}

# Read (GET) - Get all diagnoses
@app.get("/diagnosis/", response_model=List[DiagnosisResponse])
def get_diagnoses():
    with get_db_cursor() as cursor:
        query = "SELECT * FROM diagnosis"
        cursor.execute(query)
        diagnoses = cursor.fetchall()
        return diagnoses

# Update (PUT) - Update a diagnosis
@app.put("/diagnosis/{diagnosis_id}", response_model=DiagnosisResponse)
def update_diagnosis(diagnosis_id: int, diagnosis: DiagnosisCreate):
    with get_db_cursor() as cursor:
        query = "UPDATE diagnosis SET patient_id = %s, diagnosis = %s WHERE diagnosis_id = %s"
        cursor.execute(query, (diagnosis.patient_id, diagnosis.diagnosis, diagnosis_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Diagnosis not found")
        return {"diagnosis_id": diagnosis_id, **diagnosis.dict()}

# Delete (DELETE) - Delete a diagnosis
@app.delete("/diagnosis/{diagnosis_id}")
def delete_diagnosis(diagnosis_id: int):
    with get_db_cursor() as cursor:
        query = "DELETE FROM diagnosis WHERE diagnosis_id = %s"
        cursor.execute(query, (diagnosis_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Diagnosis not found")
        return {"message": "Diagnosis deleted successfully"}

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Liver Disease Prediction API"}
