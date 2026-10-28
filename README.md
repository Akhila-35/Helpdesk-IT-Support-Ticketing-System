# 🎫 Helpdesk / IT Support Ticketing System

A full-stack, role-based IT support ticket management application developed using **Python, FastAPI, Streamlit, SQLAlchemy, and SQLite**.

The system allows users to report technical issues, administrators to manage and assign tickets, and support engineers to resolve issues efficiently.

It provides secure authentication, role-based access control, automated SLA tracking, ticket status management, notifications, and a user-friendly Streamlit interface.

---

## 📌 Project Overview

The Helpdesk / IT Support Ticketing System is designed to simplify the process of managing technical support requests within an organization.

It provides a centralized platform where requesters can raise issues, administrators can review and assign tickets, and engineers can work on assigned problems.

The system follows an **admin-mediated communication model**, ensuring that requesters and engineers communicate only through administrators.

### Objectives

- Simplify IT support ticket creation and management.
- Provide role-based access to system functionality.
- Enable administrators to assign ticket priorities and categories.
- Assign support engineers to appropriate tickets.
- Track ticket progress and resolution deadlines.
- Improve communication through notifications.
- Maintain a structured ticket resolution workflow.

---

## 🚀 Key Features

### 1. User Authentication and Authorization

- Secure user registration and login.
- JWT-based authentication.
- Password hashing.
- Role-based access control.
- Restricted API access based on user roles.

### 2. Ticket Management

- Requesters can create support tickets.
- Tickets contain a title and description.
- Administrators review submitted tickets.
- Administrators assign categories and priorities.
- Administrators assign engineers.
- Engineers update ticket progress.
- Administrators close resolved tickets.

### 3. Role-Based Dashboards

The application supports three user roles:

**Requester**
- Create support tickets.
- View submitted tickets.
- Track ticket status.
- Communicate with administrators.
- Receive notifications.

**Admin**
- View and manage support tickets.
- Assign ticket categories.
- Set ticket priorities.
- Assign support engineers.
- Monitor ticket progress.
- Communicate with requesters and engineers.
- Close resolved tickets.

**Engineer**
- View assigned tickets.
- Update ticket progress.
- Resolve assigned issues.
- Communicate with administrators.
- Receive ticket notifications.

### 4. Ticket Status Tracking

Tickets move through the following statuses:

- `OPEN`
- `ASSIGNED`
- `IN_PROGRESS`
- `WAITING_FOR_USER`
- `RESOLVED`
- `CLOSED`

### 5. SLA Management

The system supports Service Level Agreement (SLA) tracking based on ticket priority.

| Priority | Resolution Time |
|---|---|
| Critical | 2 Hours |
| High | 4 Hours |
| Medium | 8 Hours |
| Low | 24 Hours |

Ticket priority is assigned by the administrator after reviewing the issue.

SLA deadlines are calculated according to the configured priority rules.

### 6. Ticket Communication System

The application uses an administrator-mediated communication model.

Two communication channels are supported:

**Requester ↔ Admin**

Requesters can communicate with administrators regarding their tickets.

**Admin ↔ Engineer**

Engineers communicate with administrators regarding assigned work.

Direct communication between requesters and engineers is restricted.

### 7. Notification System

The application generates notifications for ticket-related activities.

Features include:

- New ticket-message notifications.
- Ticket resolution notifications.
- Ticket closure notifications.
- Actual message content displayed in notifications.
- Read and unread notification indicators.
- Notification timestamps.
- Ability to mark notifications as read.

Previously received notification content remains available after marking it as read, provided the notification is retained by the backend.

### 8. Streamlit Frontend

The application provides an interactive interface using Streamlit.

Features include:

- Login interface.
- Role-based dashboards.
- Ticket creation forms.
- Ticket management screens.
- Ticket status updates.
- Ticket conversations.
- Notifications.
- Dashboard statistics.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Frontend Framework | Streamlit |
| Database | SQLite |
| ORM | SQLAlchemy |
| Data Validation | Pydantic |
| Authentication | JWT |
| Password Security | Password Hashing |
| API Documentation | Swagger UI |
| ASGI Server | Uvicorn |
| Version Control | Git and GitHub |

---

## 🏗️ System Architecture

```text
                 USER
                  |
                  v
          STREAMLIT FRONTEND
           (localhost:8501)
                  |
                  | HTTP Requests
                  v
            FASTAPI BACKEND
          (localhost:8001)
                  |
                  v
           BUSINESS LOGIC
                  |
                  v
             SQLALCHEMY
                  |
                  v
           SQLITE DATABASE
```

The Streamlit frontend sends HTTP requests to FastAPI.

FastAPI handles authentication, authorization, ticket management, assignments, messages, and notifications.

SQLAlchemy manages database operations using SQLite.

---

## 🔄 Ticket Workflow

```text
          REQUESTER
              |
              | Creates Ticket
              v
             OPEN
              |
              v
            ADMIN
              |
              | Reviews Ticket
              | Assigns Category
              | Sets Priority
              | Assigns Engineer
              v
           ASSIGNED
              |
              v
           ENGINEER
              |
              | Starts Working
              v
          IN_PROGRESS
              |
              | Resolves Issue
              v
           RESOLVED
              |
              v
            ADMIN
              |
              | Reviews Resolution
              | Closes Ticket
              v
            CLOSED
```

If additional information is required, the ticket may enter the `WAITING_FOR_USER` state.

Communication with the requester is handled through the administrator.

---

## 📂 Project Structure

The following is an illustrative structure. File and folder names may differ in the actual repository.

```text
helpdesk_it_support_ticketing_system/
│
├── app/
│   ├── api/
│   │   └── ...
│   │
│   ├── core/
│   │   └── ...
│   │
│   ├── services/
│   │   └── ...
│   │
│   ├── main.py
│   └── ...
│
├── frontend/
│   └── ...
│
├── requirements.txt
│
└── README.md
```

---

## ⚙️ Installation and Setup

### Prerequisites

Ensure the following are installed:

- Python
- VS Code or another code editor
- Git (optional)

### Step 1: Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
```

Navigate to the project directory:

```bash
cd helpdesk_it_support_ticketing_system
```

Replace the placeholder with your actual GitHub repository URL.

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Ensure the repository includes the required dependency file.

### Step 4: Configure the Backend

Configure the database connection, JWT secret, and other required application settings.

Use a secure JWT secret and avoid committing credentials or sensitive configuration values to GitHub.

### Step 5: Start FastAPI

Open the first terminal and run:

```bash
uvicorn app.main:app --reload --port 8001
```

FastAPI will run at:

http://127.0.0.1:8001

Swagger API documentation:

http://127.0.0.1:8001/docs

### Step 6: Configure Streamlit

Ensure the frontend API configuration points to the FastAPI backend.

Example:

```python
API_BASE_URL = "http://127.0.0.1:8001"
```

Adjust the URL if your backend uses a different port or API prefix.

### Step 7: Start Streamlit

Open a second terminal.

Run the Streamlit entry-point file.

For example:

```bash
streamlit run streamlit_app.py
```

Or, if the application is located inside the frontend directory:

```bash
streamlit run frontend/app.py
```

Use the command matching your actual project structure.

Open:

http://localhost:8501

**Note:** Both FastAPI and Streamlit must be running for the frontend to communicate with the backend in this development setup.

---

## 📡 API Documentation

FastAPI provides interactive API documentation through Swagger UI.

The backend includes functionality for:

- Authentication
- User management
- Ticket management
- Ticket categories
- Engineer assignments
- Ticket comments
- Notifications

API endpoints can be explored and tested using Swagger UI.

The exact available endpoints depend on the current backend implementation.

---

## 🧪 Application Testing

The application can be tested using Swagger UI and Streamlit.

### Requester Testing

1. Log in as a requester.
2. Create a support ticket.
3. View the submitted ticket.
4. Check ticket status.
5. Send a message to the administrator.
6. View notifications.

### Admin Testing

1. Log in as an administrator.
2. View submitted tickets.
3. Assign ticket categories and priorities.
4. Assign engineers.
5. Monitor ticket progress.
6. Communicate with requesters and engineers.
7. Close resolved tickets.

### Engineer Testing

1. Log in as an engineer.
2. View assigned tickets.
3. Change ticket status to `IN_PROGRESS`.
4. Communicate with the administrator.
5. Resolve assigned tickets.

---

## 🔐 Security Features

The application uses several security mechanisms:

- JWT-based authentication.
- Password hashing.
- Role-based authorization.
- Protected API endpoints.
- Restricted ticket operations.
- Administrator-controlled engineer assignment.
- Separate communication channels.
- Backend permission validation.

Sensitive operations should be protected at the backend level, not only through frontend controls.

---

## 📊 Dashboard Statistics

The system provides ticket statistics to help users monitor support activity.

Useful dashboard metrics include:

- Total Tickets
- Open Tickets
- In-Progress Tickets
- Resolved Tickets
- Closed Tickets

Resolved and Closed are treated as separate statuses.

A ticket marked `CLOSED` is not counted as currently `RESOLVED` unless the dashboard explicitly calculates completed tickets using both statuses.

---

## 🌟 Advantages

- Centralized IT support management.
- Clear separation of user responsibilities.
- Structured ticket lifecycle.
- Improved issue tracking.
- Priority-based SLA management.
- Secure role-based access.
- Organized communication.
- Interactive frontend.
- REST API architecture.
- Easy local development using SQLite.

---

## 🔮 Future Enhancements

Potential improvements include:

- Advanced ticket search and filtering.
- SLA breach alerts.
- Email notifications.
- Ticket analytics and reporting.
- File attachments