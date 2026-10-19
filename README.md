# Hotel & Restaurant Management System

A cloud-connected hotel and restaurant management application built using **Python, Streamlit, MySQL, and TiDB Cloud**. The system provides a centralized interface for managing guests, room reservations, restaurant orders, payments, staff, and service requests.

# Project Overview

The Hotel & Restaurant Management System was developed as a Database Systems project to apply relational database concepts to a practical management application.

The application connects a Streamlit interface to a TiDB Cloud database, enabling users to manage hotel and restaurant records through an interactive interface.

# Key Features

- **Guest Management:** Maintain guest details and contact information.
- **Room Management:** Manage room information, room types, pricing, and availability.
- **Reservation Management:** Handle room reservations, check-in dates, check-out dates, and reservation status.
- **Restaurant Management:** Organize restaurant information and menu items.
- **Food Order Management:** Record food orders and individual order items with quantities and prices.
- **Payment Management:** Maintain payment records, amounts, payment methods, and payment status.
- **Staff Management:** Store staff details, roles, contact information, and salaries.
- **Service Requests:** Track guest requests and their assigned staff members.
- **SQL Analytics:** Retrieve operational information using SQL queries, joins, and billing summaries.

## 🛠️ Tech Stack

**Technology Used**

Python
Streamlit
MySQL Connector(Python)
TiDB Cloud
SQL

# Database Design

The database consists of ten related tables designed to organize the application's core operations.

**Table - Description**

Guest - Stores guest information
Room - Stores room details and status 
Reservation - Stores room reservation records
Restaurant - Stores restaurant information 
Menu_Item - Stores restaurant menu items 
Food_Order - Stores food order records 
Order_Item - Stores individual items within food orders 
Payment - Stores payment transactions and statuses 
Staff - Stores staff information 
Service_Request - Stores guest requests and staff assignments 

The project also includes a View_Active_Billing_Summary SQL view for summarizing guest payment information.

# Database Concepts Applied

- Relational database design
- Primary keys and foreign keys
- Relationships between multiple tables
- SQL queries and joins
- Data insertion, retrieval, updating, and deletion where implemented
- Views for summarizing data
- Transactions for related database operations

# Application Architecture


              User
               |
               v
       Streamlit Interface
               |
               v
       Python Application
               |
               v
     MySQL Connector/Python
               |
               v
          TiDB Cloud
               |
               v
      Relational Database



# Prerequisites

- Python 3.10 or a compatible version supported by the dependencies
- A TiDB Cloud account or compatible MySQL database
- Git

# 1. Clone the repository


git clone https://github.com/sanjaythan/hotel-restaurant-management-system.git
cd hotel-restaurant-management-system


# 2. Create a virtual environment

```
python -m venv .venv
```

Activate it on Windows:

```
.venv\Scripts\activate
```

# 3. Install dependencies

```
pip install -r requirements.txt
```

# 4. Configure database credentials

Create a `.streamlit/secrets.toml` file in the project directory.

```
[mysql]
host = "XXX"
port = XXX
database = "XXX"
user = "XXX"
password = "XXX"
```

# 5. Run the application

streamlit run app.py
The application should open in your browser at the local Streamlit address.

## Deployment
The application is deployed using Streamlit Community Cloud and connects to TiDB Cloud for database operations.

- Repository: [GitHub](https://github.com/sanjaythan/hotel-restaurant-management-system)
- Deployment: Streamlit Community Cloud

## Learning Outcomes

- Designing a relational database for a multi-module application
- Connecting Python applications to a cloud-hosted database
- Implementing database-driven workflows
- Writing SQL queries for operational reporting
- Organizing application functionality using Streamlit
- Collaborating on a software development project
- Deploying a cloud-connected application

## Contributors

- Sanjay Thandeeswaran
- Monish Kumar T O

## Future Improvements

- Authentication and role-based access control
- More detailed revenue and occupancy analytics
- Improved reservation conflict handling
- Automated invoice generation
- Database backup and recovery procedures
- Additional validation and error handling
