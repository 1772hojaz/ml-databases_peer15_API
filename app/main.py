from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conint, confloat
from typing import List
from contextlib import contextmanager
from app.connection import get_db_connection
import logging

# Initialize FastAPI App
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Pydantic models for request validation
class PatientCreate(BaseModel):
    age: conint(ge=0, le=120)  # Age must be between 0 and 120
    gender: str  # Accepts "male" or "female"

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
    gender: str

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

# Helper function to convert gender to binary
def convert_gender_to_binary(gender: str) -> int:
    if gender.lower() == "male":
        return 1
    elif gender.lower() == "female":
        return 0
    else:
        raise ValueError("Gender must be 'male' or 'female'")

# Helper function to convert binary gender to string
def convert_binary_to_gender(gender: int) -> str:
    if gender == 1:
        return "male"
    elif gender == 0:
        return "female"
    else:
        raise ValueError("Gender must be 0 or 1")

# Helper function to check if a patient exists
def patient_exists(cursor, patient_id: int) -> bool:
    cursor.execute("SELECT patient_id FROM patients WHERE patient_id = %s", (patient_id,))
    return cursor.fetchone() is not None

# Create (POST) - Add a new patient
@app.post("/patients/", response_model=PatientResponse)
def create_patient(patient: PatientCreate):
    with get_db_cursor() as cursor:
        try:
            # Convert gender to binary (1 for male, 0 for female)
            gender_binary = convert_gender_to_binary(patient.gender)
            query = "INSERT INTO patients (age, gender) VALUES (%s, %s)"
            cursor.execute(query, (patient.age, gender_binary))
            patient_id = cursor.lastrowid
            return {"patient_id": patient_id, "age": patient.age, "gender": patient.gender}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Read (GET) - Get all patients
@app.get("/patients/", response_model=List[PatientResponse])
def get_patients():
    with get_db_cursor() as cursor:
        try:
            query = "SELECT * FROM patients"
            cursor.execute(query)
            patients = cursor.fetchall()
            # Convert binary gender back to string
            for patient in patients:
                patient["gender"] = convert_binary_to_gender(patient["gender"])
            return patients
        except Exception as e:
            logger.error(f"Error fetching patients: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Update (PUT) - Update a patient
@app.put("/patients/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient: PatientCreate):
    with get_db_cursor() as cursor:
        try:
            # Convert gender to binary
            gender_binary = convert_gender_to_binary(patient.gender)
            query = "UPDATE patients SET age = %s, gender = %s WHERE patient_id = %s"
            cursor.execute(query, (patient.age, gender_binary, patient_id))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Patient not found")
            return {"patient_id": patient_id, "age": patient.age, "gender": patient.gender}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error updating patient: {str(e)}")
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
            logger.error(f"Error deleting patient: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Create (POST) - Add a new medical test
@app.post("/medical_tests/", response_model=MedicalTestResponse)
def create_medical_test(test: MedicalTestCreate):
    with get_db_cursor() as cursor:
        try:
            # Check if the patient exists
            if not patient_exists(cursor, test.patient_id):
                raise HTTPException(status_code=404, detail="Patient not found")

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
            logger.error(f"Error creating medical test: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Create (POST) - Add a new diagnosis
@app.post("/diagnosis/", response_model=DiagnosisResponse)
def create_diagnosis(diagnosis: DiagnosisCreate):
    with get_db_cursor() as cursor:
        try:
            # Check if the patient exists
            if not patient_exists(cursor, diagnosis.patient_id):
                raise HTTPException(status_code=404, detail="Patient not found")

            query = "INSERT INTO diagnosis (patient_id, diagnosis) VALUES (%s, %s)"
            cursor.execute(query, (diagnosis.patient_id, diagnosis.diagnosis))
            diagnosis_id = cursor.lastrowid
            return {"diagnosis_id": diagnosis_id, **diagnosis.dict()}
        except Exception as e:
            logger.error(f"Error creating diagnosis: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Liver Disease Prediction API"}
