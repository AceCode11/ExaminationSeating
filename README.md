# Exam Automation System

## Overview
A robust desktop application built with PyQt6 and SQLAlchemy designed to automate and streamline examination management tasks, including seating arrangements, attendance sheet generation, and timetable tracking.

## Core Functionalities
- **Data Import & Processing**: Smart import of student attendance and timetables from Excel files with auto-detection of column headers.
- **Attendance Management**: Automatically categorize valid students and "NOR" (Not On Roll) students.
- **Timetable Management**: Import and track examination schedules.
- **Seating Arrangements**: Allocate students to available rooms dynamically based on room capacities and requirements.
- **PDF Report Generation**: Generate print-ready PDF files for:
  - Attendance sheets (with customizable headers and structured layouts)
  - Seating charts for exam rooms
  - Student details stickers (with customizable dimensions, font sizes, and layout options)
- **Session Management**: Persistent data storage utilizing a local SQLite database to manage multiple exam sessions.

## Requirements
The system requires **Python 3.8+** to run. All required dependencies are listed in the `requirements.txt` file:

- `PyQt6` - For the graphical user interface.
- `SQLAlchemy` - For database ORM.
- `pandas` - For robust data processing and manipulation.
- `openpyxl` - For reading Excel files.
- `reportlab` - For generating PDF documents.

### Installation
Install the necessary Python packages using `pip`:
```bash
pip install -r requirements.txt
```

## Required Input Files (Excel Format)
The application imports data using Excel files (`.xlsx` or `.xls`). It features a smart column detection system that looks for specific keywords within the header row, meaning exact column names are not strictly required as long as the keywords match.

### 1. Attendance Data Sheet
This sheet provides the list of students participating in an exam session.
- **Required Column**: `RollNumber` 
  *(Accepted keywords: `roll`, `seatno`, `seat_no`, `seat`, `id`, `studentid`, `prn`, `enrollment`, `enrollmentno`, `regno`, `registration`)*
- **Optional Column**: `StudentName` 
  *(Accepted keywords: `name`, `fullname`, `studentname`, `student`)*

*Note: If a student's name is missing or left blank, the application will automatically categorize them as "NOR" (Not On Roll).*

### 2. Timetable Data Sheet
This sheet outlines the schedule for the exams.
- **Required Columns**:
  - `Date` *(Accepted keywords: `date`)*
  - `Time` *(Accepted keywords: `time`)*
  - `SubjectCode` *(Accepted keywords: `code`, `subject code`, `subjectcode`, `papercode`)*
  - `SubjectName` *(Accepted keywords: `subject name`, `subject`, `subjectname`, `paper`, `papername`)*

## How to Run
To launch the application, execute the `main.py` script from the project's root directory:
```bash
python main.py
```
