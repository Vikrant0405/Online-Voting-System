# Online Voting System

A desktop voting application built with Python using Tkinter for GUI and MySQL for database management. This system provides a secure and efficient way to conduct online voting with admin and user functionalities.

## Features

### Admin Features
- **Admin Login** - Secure authentication for administrators
- **Add New User** - Register new voters in the system
- **Add Candidate** - Add election candidates
- **Show Users** - View all registered users
- **Show All Candidates** - View all candidates in the election
- **Show Result** - View voting results
- **Show Graph** - Visual representation of voting results
- **Start/Stop Voting** - Control the voting period
- **Reset Voting** - Reset all votes for a new election

### User Features
- **User Login** - Secure authentication using Voter ID or Aadhar Card
- **Cast Vote** - Vote for preferred candidates
- **Vote Status** - Check if user has already voted

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.x
- MySQL Server
- Required Python packages:
  - `tkinter` (included with Python)
  - `mysql-connector-python`
  - `matplotlib`

## Installation

1. **Clone the repository**
   
```
bash
   git clone <repository-url>
   cd Online-Voting-System
   
```

2. **Install Python dependencies**
   
```
bash
   pip install mysql-connector-python matplotlib
   
```

3. **Setup MySQL Database**
   - Create a database named `voting_system`
   - Create the required tables:
     - `users` table with columns: id, username, password, aadharId, voterID, gender, is_voted, voted_condi, role
     - `candidates` table with columns: id, name, party, voter (vote count)

4. **Configure Database Connection**
   - Open `index.py` and modify the database connection settings:
     
```
python
     self.conn = mysql.connector.connect(
         host="localhost",
         database="voting_system",
         username="your_username",
         password="your_password"
     )
     
```

## Usage

1. **Run the application**
   
```
bash
   python index.py
   
```

2. **Login**
   - **Admin Login**: Use admin credentials (role = "admin" in users table)
   - **User Login**: Use Voter ID or Aadhar Card number with password

3. **Admin Operations**
   - Add new users and candidates
   - Start the voting process
   - View results and statistics
   - Reset voting when needed

4. **User Operations**
   - Login with credentials
   - Cast vote for preferred candidate
   - Cannot vote twice (system prevents duplicate votes)

## Project Structure

```
Online-Voting-System/
├── index.py          # Main application file
├── README.md         # Project documentation
└── .git/             # Git repository
```

## Technology Stack

- **Frontend**: Tkinter (Python GUI framework)
- **Backend**: Python
- **Database**: MySQL
- **Data Visualization**: Matplotlib

## Database Schema

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| username | VARCHAR | User's name |
| pwd | VARCHAR | User's password |
| adharId | VARCHAR | Aadhar Card number |
| voterID | VARCHAR | Voter ID number |
| gender | VARCHAR | User's gender |
| is_voted | INT | Vote status (0/1) |
| voted_condi | INT | Voting condition |
| role | VARCHAR | User role (admin/voter) |

### Candidates Table
| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| name | VARCHAR | Candidate's name |
| party | VARCHAR | Political party |
| voter | INT | Vote count |

## License

This project is for educational purposes.
