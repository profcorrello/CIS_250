# Library Management System Scope Statement

## Project Overview

The Library Management System is designed to automate core library operations including inter-library loans (ILL), fine management, and book hold queues. The system aims to streamline patron interactions and administrative workflows through a centralized API-driven architecture.

## In Scope

### 1. Patron Management

- **Patron Registration**: Creation and management of patron profiles.
- **Patron Types**: Support for distinct patron categories with different privileges:
  - General Integration
  - Student
  - Staff

### 2. Inventory Management

- **Book Tracking**: Management of book details (Title, Author, ISBN).
- **Status Tracking**: Real-time status updates (Available, Checked Out, Lost).
- **Item Types**: Categorization of items (Books, DVDs, Reference Materials) to support variable fine logic.

### 3. Circulation & Holds

- **Hold Queues**: First-In-First-Out (FIFO) reservation system for popular titles.
- **Hold Management**:
  - Placing holds on specific books.
  - Viewing active holds for books and patrons.
  - Automatic expiry of unclaimed holds (default 5 days).
  - Logic to promote the next patron in queue when a copy becomes available.

### 4. Fine Management

- **Automated Calculation**: Dynamic fine calculation based on:
  - Days overdue.
  - Patron type (e.g., lower/no fines for Staff).
  - Item type (e.g., higher fines for Reference materials).
- **Policies**:
  - Grace periods (default 1 day).
  - Maximum fine caps per item.
- **Tracking**:
  - Recording fine reasons and amounts.
  - Tracking payment status (Paid/Unpaid).

### 5. Inter-Library Loans (ILL)

- **Request Management**: Lifecycle management of ILL requests:
  - Stages: Draft -> Submitted -> In Transit -> Received -> Checked Out -> Returned.
- **Partner Integration**: Management of partner library profiles (Contact info, Shipping address).
- **Status Tracking**: Granular tracking of request status for patrons and staff.

## Out of Scope

- **Payment Processing**: Integration with payment gateways (Stripe, PayPal) is not included in this phase.
- **User Authentication**: Advanced authentication (OAuth, SSO, Password hashing) is not currently implemented; the system uses basic email identification.
- **Frontend Interface**: This project focuses solely on the Backend API; no graphical user interface (GUI) is included.
- **Notification Delivery**: While logic exists to identify when users _should_ be notified, the actual delivery mechanism (Email/SMS server integration) is out of scope.

## Technical Boundaries

- **Architecture**: RESTful API using FastAPI.
- **Database**: SQL-based persistence (likely SQLite/PostgreSQL via SQLAlchemy).
- **Deployment**: Local execution environment.
