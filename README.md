# 🏔️ Trekking Management Application

A full-stack role-based web application for managing trekking activities, 
built with Flask, Jinja2, Bootstrap, and SQLite as part of the Modern 
Application Development I (MAD-I) course project.

The system supports three roles — **Admin**, **Trek Staff**, and **User 
(Trekker)** — enabling trek creation and approval, staff assignment, 
slot-based trek bookings, and complete trekking history tracking, while 
preventing overbooking and unauthorized access.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask |
| Templating | Jinja2 |
| Frontend | HTML, CSS, Bootstrap |
| Database | SQLite (via Flask-SQLAlchemy ORM) |
| Auth | Flask-Login, Werkzeug (password hashing) |

---

## 👥 Roles & Functionalities

### Admin (pre-existing, no registration)
- Create, edit, remove treks
- Approve or blacklist trek staff
- Assign staff to treks
- View all users, staff, and treks
- Search treks/staff/users by name or ID
- View all bookings and trekking history

### Trek Staff (self-register, needs Admin approval)
- Register and log in (after approval)
- View treks assigned by Admin
- Update available slots and trek status
- View registered participants per trek
- Mark treks as started/completed

### User / Trekker (self-register)
- Register and log in
- View available/open treks
- Search and filter by difficulty/location
- Book treks and track booking status
- View trekking history

---

## 📂 Project Structure
Trekking-Management-Application/
│
├── app.py # Main Flask app entry point
├── config.py # App configuration (DB URI, secret key)
├── models.py # SQLAlchemy models (User, Trek, Booking, StaffProfile)
├── create_admin.py # Script to create DB tables + pre-existing Admin
├── requirements.txt # Python dependencies
├── .gitignore
├── README.md
│
├── instance/ # SQLite DB (auto-generated, git-ignored)
│
├── templates/ # Jinja2 HTML templates
│ └── base.html
│
└── static/
└── css/
└── style.css

---

## 🗄️ Database Schema (Milestone 1)

### User
Stores login credentials and role for all 3 user types.
| Field | Type | Notes |
|---|---|---|
| id | Integer (PK) | |
| name | String | |
| email | String | Unique |
| password_hash | String | Hashed via Werkzeug |
| role | String | Admin / Staff / Trekker |
| contact | String | |
| is_blacklisted | Boolean | |
| is_approved | Boolean | Relevant for Staff |
| created_at | DateTime | |

### StaffProfile
Extends User with staff-specific approval status (1-to-1 with User).
| Field | Type | Notes |
|---|---|---|
| id | Integer (PK) | |
| user_id | Integer (FK → users.id) | Unique |
| status | String | Pending / Approved / Blacklisted |

### Trek
| Field | Type | Notes |
|---|---|---|
| id | Integer (PK) | |
| name | String | |
| location | String | |
| difficulty | String | Easy / Moderate / Hard |
| duration | Integer | In days |
| description | Text | |
| available_slots | Integer | |
| total_slots | Integer | |
| assigned_staff_id | Integer (FK → staff_profiles.id) | |
| status | String | Pending/Approved/Open/Closed/Completed |
| start_date | Date | |
| end_date | Date | |
| created_at | DateTime | |

### Booking
| Field | Type | Notes |
|---|---|---|
| id | Integer (PK) | |
| user_id | Integer (FK → users.id) | |
| trek_id | Integer (FK → treks.id) | |
| booking_date | DateTime | |
| status | String | Booked / Cancelled / Completed |

### Relationships
- `User` ↔ `Booking` — one-to-many (a user can have multiple bookings)
- `Trek` ↔ `Booking` — one-to-many (a trek can have multiple bookings)
- `User` ↔ `StaffProfile` — one-to-one (a staff user has one staff profile)
- `StaffProfile` ↔ `Trek` — one-to-many (a staff member can be assigned multiple treks)

---

## ⚙️ Setup Instructions (Local Development)

```bash
# 1. Clone the repository
git clone https://github.com/23f2000490/Trekking-Management-Application.git
cd Trekking-Management-Application

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the database and pre-existing Admin user
python create_admin.py

# 5. Run the application
python app.py
```

Default Admin login (for local testing):
- **Email:** admin@trekapp.com
- **Password:** admin123



