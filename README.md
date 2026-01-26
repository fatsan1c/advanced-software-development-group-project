# Paragon Apartment Management System (PAMS)

## Overview
Paragon Apartment Management System (PAMS) is a Python-based desktop application designed to improve operational efficiency for a multi-location apartment management company. It consolidates tenant, apartment, payment, and maintenance data into a secure, scalable system with role-based access control and reporting capabilities.

## Features
- User and role management (Admin, Finance, Maintenance, Manager, Front Desk)
- Tenant registration, lease tracking, and early exit handling
- Apartment management with location and occupancy details
- Payment and billing simulation with late payment notifications
- Maintenance request tracking and resolution logging
- Dynamic reporting for occupancy, financials, and maintenance costs
- Integrated database with mock data for testing and demonstration

## Tech Stack
- **Language:** Python 3.x  
- **Database:** MySQL or SQLite  
- **GUI Framework:** Tkinter or PyQt  
- **Testing:** unittest / pytest  
- **Version Control:** Git and GitHub  

## Installation

### Quick Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/shamykyzer/systems-development-group-project.git
   cd advanced-software-development-group-project
   ```

2. Set up the virtual environment 
   > **Windows:**
   > ```powershell
   > cd setupfiles
   > powershell -ExecutionPolicy Bypass -File .\setup.ps1
   > ```
   
   > **Linux/Mac:**
   > ```bash
   > cd setupfiles
   > chmod +x setup.sh
   > ./setup.sh
   > ```
   
   - The setup script will automatically:
      - Create a virtual environment
      - Install all dependencies
      - Create a `.env` file from the template

3. Import the provided SQL dump from `/setupfiles/paragonapartments_full_dump.sql` to mySQL and open a connection.

4. Edit `/paragonapartments/.env` with your database credentials.

### 5. Run the Application:

   > ```bash
   > python paragonapartments/main.py
   > ```


All UML design diagrams, methodology reports, and test documentation are available in the /docs directory. These include:
   - Use Case, Class, and Sequence diagrams
   - Agile methodology report
   - Test case documentation and screenshots

### Assessment Context:

Developed as part of the Advanced Software Development (UFCF8S-30-2) module at UWE Bristol. This project demonstrates full software lifecycle implementation — from requirements analysis and design to coding, testing, and evaluation.
