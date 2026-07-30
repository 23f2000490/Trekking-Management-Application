---

## 🗄️ Database Schema

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

Then open **http://127.0.0.1:5000** in your browser.

---

## Test Credentials 

Admin 
Email : admin@trekapp.com
password : admin123

Staff :
Email: staff1@gmail.com
passowrd : 12345

User
Email : 23f2000490@ds.study.iitm.ac.in
password : 12345
