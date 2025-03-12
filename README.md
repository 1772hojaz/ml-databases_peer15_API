# Liver Disease Prediction API

This project provides a FastAPI-based RESTful API for managing patient data, medical tests, and diagnoses related to liver disease.

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

- **Create a Patient**:
  - `POST /patients/`
  - Request Body:
    ```json
    {
      "age": 30,
      "gender": "male"
    }
    ```

- **Get All Patients**:
  - `GET /patients/`

- **Root Endpoint**:
  - `GET /`
