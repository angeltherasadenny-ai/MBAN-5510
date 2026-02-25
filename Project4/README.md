# 🏥 Appointment Assistant System

An AI-powered Appointment Management System that supports patient
verification, appointment rescheduling, cancellation, and preparation
instructions.

This system demonstrates structured workflow design using graph-based
logic, state handling, and modular Python architecture.

------------------------------------------------------------------------

## 📌 Project Overview

The Appointment Assistant System allows patients to:

-   ✅ Verify their appointment records\
-   🔄 Reschedule an appointment\
-   ❌ Cancel an appointment\
-   📋 Request preparation instructions

The system uses a structured conversational workflow backed by a CSV
appointment database.

------------------------------------------------------------------------

## 🗂 Project Structure

    ├── app1.py              # Main Streamlit UI application
    ├── main.py              # CLI-based execution option
    ├── graph.py             # Workflow graph logic
    ├── nodes.py             # Intent handling nodes
    ├── middleware.py        # State and validation handling
    ├── appointments.csv     # Appointment database
    ├── requirements.txt     # Project dependencies
    ├── .env.example         # Environment variable template
    ├── .gitignore           # Ignored files configuration

------------------------------------------------------------------------

## 🔁 System Workflow

1.  Patient Verification\
2.  Intent Selection (Reschedule / Cancel / Instructions)\
3.  Action Execution\
4.  Confirmation Output

The system uses graph-based logic to control transitions between steps.

------------------------------------------------------------------------

## 🛠 Technologies Used

-   Python\
-   Streamlit (UI execution)\
-   CSV Data Handling\
-   Graph-based Workflow Architecture\
-   Modular State Management

------------------------------------------------------------------------

## ▶️ How to Run

### 1️⃣ Install Dependencies

    pip install -r requirements.txt

### 2️⃣ Run Streamlit Version

    python -m streamlit run app1.py

### 3️⃣ Run CLI Version (Optional)

    python main.py

------------------------------------------------------------------------

## 📊 Data Source

The system reads appointment records from:

    appointments.csv

This file acts as the backend data store for patient appointment
records.

------------------------------------------------------------------------

## 🔐 Environment Variables

Use `.env.example` as a template for configuration if required.

Never commit real credentials or sensitive data.

------------------------------------------------------------------------

## 🧠 Key Concepts Demonstrated

-   Conversational workflow automation\
-   State-based architecture\
-   Intent-driven logic handling\
-   Modular Python project structure\
-   Human-centered appointment management system

------------------------------------------------------------------------

## 🚀 Future Improvements

-   Database integration (SQL instead of CSV)\
-   Multi-user support\
-   Authentication layer\
-   Deployment to cloud hosting\
-   Logging and audit tracking

------------------------------------------------------------------------

Built for applied analytics and automation coursework.
