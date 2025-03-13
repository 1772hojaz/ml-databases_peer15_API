from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from app.connection import get_db_connection  # Ensure this import is correct

# Initialize FastAPI App
app = FastAPI()

# Pydantic models for request validation
class PatientCreate(BaseModel):
    age: int
    gender: str  # Accepts "male" or "female"

class MedicalTestCreate(BaseModel):
    patient_id: int
    total_bilirubin: float
    direct_bilirubin: float
    alkaline_phosphatase: int  # Fixed typo
    alamine_aminotransferase: int
    aspartate_aminotransferase: int
    total_proteins: float
    albumin: float
    albumin_and_globulin_ratio: float

class DiagnosisCreate(BaseModel):
    patient_id: int
    diagnosis: int  # 1 for liver disease, 0 for no disease

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

# Create (POST) - Add a new patient
@app.post("/patients/", response_model=Dict[str, str])
def create_patient(patient: PatientCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Convert gender to binary (1 for male, 0 for female)
        gender_binary = convert_gender_to_binary(patient.gender)
        query = "INSERT INTO patients (age, gender) VALUES (%s, %s)"
        cursor.execute(query, (patient.age, gender_binary))
        connection.commit()
        return {"message": "Patient created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        connection.close()

# Read (GET) - Get all patients
@app.get("/patients/", response_model=Dict[str, List[Dict]])
def get_patients():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM patients"
        cursor.execute(query)
        patients = cursor.fetchall()
        # Convert binary gender back to string
        for patient in patients:
            patient["gender"] = convert_binary_to_gender(patient["gender"])
        return {"patients": patients}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        connection.close()

# Update (PUT) - Update a patient
@app.put("/patients/{patient_id}", response_model=Dict[str, str])
def update_patient(patient_id: int, patient: PatientCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Convert gender to binary
        gender_binary = convert_gender_to_binary(patient.gender)
        query = "UPDATE patients SET age = %s, gender = %s WHERE patient_id = %s"
        cursor.execute(query, (patient.age, gender_binary, patient_id))
        connection.commit()
        return {"message": "Patient updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        connection.close()

# Delete (DELETE) - Delete a patient
@app.delete("/patients/{patient_id}", response_model=Dict[str, str])
def delete_patient(patient_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = "DELETE FROM patients WHERE patient_id = %s"
        cursor.execute(query, (patient_id,))
        connection.commit()
        return {"message": "Patient deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        connection.close()

# Create (POST) - Add a new medical test
@app.post("/medical_tests/", response_model=Dict[str, str])
def create_medical_test(test: MedicalTestCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
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
        connection.commit()
        return {"message": "Medical test created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        connection.close()

# Read (GET) - Get all medical tests
@app.get("/medical_tests/", response_model=Dict[str, List[Dict]])
def get_medical_tests():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM medical_tests"
        cursor.execute(query)
        tests = cursor.fetchall()
        return {"medical_tests": tests}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        connection.close()

# Create (POST) - Add a new diagnosis
@app.post("/diagnosis/", response_model=Dict[str, str])
def create_diagnosis(diagnosis: DiagnosisCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Validate diagnosis value (must be 0 or 1)
        if diagnosis.diagnosis not in [0, 1]:
            raise ValueError("Diagnosis must be 0 or 1")
        query = "INSERT INTO diagnosis (patient_id, diagnosis) VALUES (%s, %s)"
        cursor.execute(query, (diagnosis.patient_id, diagnosis.diagnosis))
        connection.commit()
        return {"message": "Diagnosis created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        connection.close()

# Read (GET) - Get all diagnoses
@app.get("/diagnosis/", response_model=Dict[str, List[Dict]])
def get_diagnoses():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM diagnosis"
        cursor.execute(query)
        diagnoses = cursor.fetchall()
        return {"diagnoses": diagnoses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        connection.close()

# Root endpoint
@app.get("/", response_model=Dict[str, str])
def read_root():
    return {"message": "Welcome to the Liver Disease Prediction API"}
