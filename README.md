---

# Flask Attendance and Announcement Management System

This Flask application provides an attendance management system with user and admin functionalities. It includes features for user registration, login, OTP verification, attendance tracking, announcement management, and more.

## Features

- **User Registration & Login:** Users can register and log in using a secure system with hashed passwords.
- **OTP Verification:** After login, users are required to verify their identity via a One-Time Password (OTP) sent to their email.
- **Attendance Management:** Users can submit their attendance, which is automatically marked as late, absent (alpha), or on time based on the submission time.
- **Admin Dashboard:** Admin users can view all user attendance records, manage user profiles, and create/edit announcements.
- **Automated Attendance:** Automatically marks absent users who haven't submitted attendance by a set time.
- **Data Export:** Admins can export attendance data to Excel format for record-keeping.
- **Announcements:** Admins can create and manage announcements that are visible to users.

## Requirements

- Python 3.x
- Flask
- Flask-MySQL-Connector
- Flask-Bcrypt
- Flask-APScheduler
- Pandas
- Openpyxl

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/alpiawo/Flask-Attendance.git
   cd <repository-directory>
   ```

2. **Install Dependencies**

   Create a virtual environment and install the required packages:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Configure the Application**

   Update the Flask configuration settings in `app.py`:

   - Set your MySQL database connection details:
     ```python
     app.config['MYSQL_HOST'] = 'localhost'
     app.config['MYSQL_USER'] = 'your-username'
     app.config['MYSQL_PASSWORD'] = 'your-password'
     app.config['MYSQL_DATABASE'] = 'your-database-name'
     ```

   - Replace placeholder email and password in `send_otp` function:
     ```python
     email = 'your-email@example.com'
     server.login(email, 'your-email-password')
     ```

4. **Database Setup**

   Ensure that you have a MySQL database with the following tables:

   - `users`: Stores user information.
   - `attendance`: Tracks attendance records.
   - `announcements`: Manages announcements.

   Create the required tables using the provided SQL scripts or through your database management tool.

## Running the Application

1. **Start the Flask Application**

   ```bash
   python app.py
   ```

   The application will run in debug mode and can be accessed at `http://localhost:5000`.

2. **Access the Application**

   - **Home Page**: `http://localhost:5000/`
   - **Login Page**: `http://localhost:5000/login`
   - **Registration Page**: `http://localhost:5000/register`
   - **Admin Dashboard**: `http://localhost:5000/admin`
   - **Announcements Page**: `http://localhost:5000/announcements`
   - **Create Announcement**: `http://localhost:5000/create-announcement`
   - **Edit Announcement**: `http://localhost:5000/edit-announcement/<id>`
   - **Profile Page**: `http://localhost:5000/profile`

## Routes

- `/`: Render the login page.
- `/register`: Handle user registration.
- `/login`: Handle user login and OTP verification.
- `/forgot-password`: Request password reset.
- `/reset-password`: Reset password using OTP.
- `/verify`: Render OTP verification page.
- `/verify-otp`: Handle OTP verification.
- `/admin`: Admin dashboard displaying user attendance data.
- `/attendance`: Handle attendance submissions.
- `/profile`: Display and edit user profile.
- `/export-attendance`: Export attendance data as an Excel file.
- `/announcements`: Display all announcements.
- `/create-announcement`: Create a new announcement.
- `/edit-announcement/<id>`: Edit an existing announcement.
- `/user/announcements`: Display announcements for users.
- `/check_attendance`: Check if the user has attended today.
- `/logout`: Logout and end the user session.

## Scheduled Tasks

- **Delete Attendance Records**: Every day at 00:00.
- **Mark Absences as Alpha**: Every day at 10:00 for users who haven't marked attendance.

## Notes

- Make sure to handle the secret key and database credentials securely.
- Adjust the scheduler configurations based on your application's requirements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to adjust any sections according to your specific needs or additional details you might want to include!
