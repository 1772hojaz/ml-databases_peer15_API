from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conint, confloat
from typing import List, Optional
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

class MedicalTestUpdate(BaseModel):
    patient_id: Optional[int] = None
    total_bilirubin: Optional[confloat(ge=0)] = None
    direct_bilirubin: Optional[confloat(ge=0)] = None
    alkaline_phosphatase: Optional[conint(ge=0)] = None
    alamine_aminotransferase: Optional[conint(ge=0)] = None
    aspartate_aminotransferase: Optional[conint(ge=0)] = None
    total_proteins: Optional[confloat(ge=0)] = None
    albumin: Optional[confloat(ge=0)] = None
    albumin_and_globulin_ratio: Optional[confloat(ge=0)] = None

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

# Helper function to check if a patient exists
def patient_exists(cursor, patient_id: int) -> bool:
    cursor.execute("SELECT patient_id FROM patients WHERE patient_id = %s", (patient_id,))
    return cursor.fetchone() is not None

# Helper function to check if a medical test exists
def medical_test_exists(cursor, test_id: int) -> bool:
    cursor.execute("SELECT test_id FROM medical_tests WHERE test_id = %s", (test_id,))
    return cursor.fetchone() is not None

# -------------------- Patient Endpoints --------------------

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
            return patients
        except Exception as e:
            logger.error(f"Error fetching patients: {str(e)}")
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

# -------------------- Medical Test Endpoints --------------------

# GET - Retrieve all medical tests
@app.get("/medical_tests/", response_model=List[MedicalTestResponse])
def get_medical_tests():
    with get_db_cursor() as cursor:
        try:
            query = "SELECT * FROM medical_tests"
            cursor.execute(query)
            tests = cursor.fetchall()
            return tests
        except Exception as e:
            logger.error(f"Error fetching medical tests: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# GET - Retrieve a specific medical test by test_id
@app.get("/medical_tests/{test_id}", response_model=MedicalTestResponse)
def get_medical_test(test_id: int):
    with get_db_cursor() as cursor:
        try:
            query = "SELECT * FROM medical_tests WHERE test_id = %s"
            cursor.execute(query, (test_id,))
            test = cursor.fetchone()
            if not test:
                raise HTTPException(status_code=404, detail="Medical test not found")
            return test
        except Exception as e:
            logger.error(f"Error fetching medical test: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# POST - Create a new medical test
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

# PUT - Update a medical test
@app.put("/medical_tests/{test_id}", response_model=MedicalTestResponse)
def update_medical_test(test_id: int, test: MedicalTestUpdate):
    with get_db_cursor() as cursor:
        try:
            # Check if the medical test exists
            if not medical_test_exists(cursor, test_id):
                raise HTTPException(status_code=404, detail="Medical test not found")

            # Build the update query dynamically
            update_fields = []
            update_values = []
            for field, value in test.dict(exclude_unset=True).items():
                if value is not None:
                    update_fields.append(f"{field} = %s")
                    update_values.append(value)

            if not update_fields:
                raise HTTPException(status_code=400, detail="No fields to update")

            update_query = f"UPDATE medical_tests SET {', '.join(update_fields)} WHERE test_id = %s"
            update_values.append(test_id)

            cursor.execute(update_query, update_values)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Medical test not found")

            # Fetch the updated record
            cursor.execute("SELECT * FROM medical_tests WHERE test_id = %s", (test_id,))
            updated_test = cursor.fetchone()
            return updated_test
        except Exception as e:
            logger.error(f"Error updating medical test: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# DELETE - Delete a medical test
@app.delete("/medical_tests/{test_id}")
def delete_medical_test(test_id: int):
    with get_db_cursor() as cursor:
        try:
            # Check if the medical test exists
            if not medical_test_exists(cursor, test_id):
                raise HTTPException(status_code=404, detail="Medical test not found")

            query = "DELETE FROM medical_tests WHERE test_id = %s"
            cursor.execute(query, (test_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Medical test not found")
            return {"message": "Medical test deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting medical test: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
