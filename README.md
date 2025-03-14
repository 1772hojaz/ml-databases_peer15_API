# Liver Disease Prediction API

This project provides a FastAPI-based RESTful API for managing patient data, medical tests, and diagnoses related to liver disease.


## API LINK
- https://ml-databases-peer15-api-w1yu-q265fdkji.vercel.app/docs#/
  
## Features

- **Patient Management**: Create, read, update, and delete patient records.
- **Medical Test Management**: Record and retrieve medical test results for patients.
- **Diagnosis Management**: Record and retrieve diagnoses for patients.

## Deployment on Vercel

1. **Push Your Code to a Git Repository**:
   - Ensure your code is pushed to a Git repository (e.g., GitHub, GitLab).

2. **Sign Up/Log In to Vercel**:
   - Go to [Vercel](https://vercel.com) and sign up or log in.

3. **Create a New Project**:
   - Click on "New Project" and connect your Git repository.

4. **Configure the Project**:
   - Vercel will automatically detect the `vercel.json` file and configure the project.

5. **Set Environment Variables**:
   - Set the database connection details (e.g., `DATABASE_HOST`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME`) in the Vercel dashboard under "Environment Variables".

6. **Deploy**:
   - Click "Deploy" to start the deployment process.

## API Endpoints

- **Patient Endpoints**
- POST /patients/: Create a new patient.
- GET /patients/: Retrieve all patients.
- GET /patients/{patient_id}: Retrieve a specific patient by ID.
- PUT /patients/{patient_id}: Update a patient by ID.
- DELETE /patients/{patient_id}: Delete a patient by ID.
  ---
- **Medical Test Endpoints**
- 
- POST /medical_tests/: Create a new medical test.
- GET /medical_tests/: Retrieve all medical tests.
- GET /medical_tests/{test_id}: Retrieve a specific medical test by ID.
- PUT /medical_tests/{test_id}: Update a medical test by ID.
- DELETE /medical_tests/{test_id}: Delete a medical test by ID.
  ---
- **Diagnosis Endpoints**
- 
- POST /diagnosis/: Create a new diagnosis.
- GET /diagnosis/: Retrieve all diagnoses.
