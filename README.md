# 📊 Lawhizz Accounting Service – Corporate Website

A private corporate website developed for an accounting firm, featuring a public-facing user experience alongside an internal admin dashboard. Built to support dynamic content updates, job application handling, and company news management through a secure interface.

---

## 🌐 Website Overview

This website is divided into **two main modules**:

### 🧑‍💼 Public User Site
Standard informational site available to all visitors. Includes company information, services, job openings, and a way to contact the company.

**User Pages:**
- Homepage
- About Us
- Services
  - Bookkeeping Service
  - Business Administration
  - Human Resources
- Events
- Career
  - Internship Jobs
  - Fresh Graduates Jobs
  - Professional Jobs
- News
- Contact

---

### 🔐 Admin Dashboard
Accessible through secure login, allowing internal staff to manage key content displayed on the user side.

**Admin Pages:**
- Admin Login
- Admin Dashboard:
  - Manage Job Applications
  - Manage Job Positions
  - Manage News Articles
  - Manage User Inquiries

> Each of these sections supports full **CRUD** (Create, Read, Update, Delete) operations.

---

## 🛠️ Technologies Used

| Tool | Purpose |
|------|---------|
| **Python** | Main programming language |
| **Flask** | Web framework (routes, templates, and backend logic) |
| **HTML / CSS / JavaScript** | Frontend structure and styling |
| **MySQL** | Relational database for storing site data |
| **Google API Integration** | Used in job application flow (e.g. Google Forms/Sheets) |
| **Visual Studio Code** | IDE used for development |
| **GitHub** | Version control (repo is private for confidentiality) |

---

## 📁 Project Structure (Simplified)

``` /project-root ├── app.py ├── admin_routes.py ├── user_routes.py ├── model_db.py ├── extensions.py ├── static/ ├── templates/ ├── info/ │ ├── requirements.txt │ └── directory.txt ├── .gitignore ├── .env  ```


---

## 🚀 Deployment
The site is prepared for deployment on **Vercel**, using Flask as the backend handler and MySQL for persistent storage.

---

## 🔒 Note
This is a **private project developed for internal corporate use**. Source code and assets are not intended for public sharing due to company policy.

