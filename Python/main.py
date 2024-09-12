from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysql_connector import MySQL
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import random
import smtplib
from email.message import EmailMessage
from functools import wraps
import logging
import threading
import time
from flask import current_app
import pandas as pd
from io import BytesIO
from flask import send_file
from datetime import datetime, time as datetime_time
from flask import jsonify


app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)

# MySQL DB
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DATABASE'] = 'your database name'

mysql = MySQL(app)

otp = ""

# Konfigurasi login
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# function untuk mengirim kode OTP
def send_otp(to_mail):
    global otp
    otp = "".join([str(random.randint(0, 9)) for _ in range(5)])

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    email = 'exampe-@domain.com'
    server.login(email, "your password app")

    msg = EmailMessage()
    msg['Subject'] = "Verifikasi OTP"
    msg['from'] = email
    msg['to'] = to_mail
    msg.set_content(f"Kode verifikasi OTP Anda adalah: " + otp)

    server.send_message(msg)
    server.quit()

# install scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Untuk melindungi rute
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('index'))

        # Check if the user is an admin
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if not user or not user[0]:  # user[0] (id) represents `is_admin`
            flash("Anda tidak memiliki akses ke halaman ini!")
            return redirect(url_for('success'))

        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@login_required
@admin_required
def admin_page():
    # Fetch all users and their attendance data
    cursor = mysql.connection.cursor()

    # Query to fetch user attendance data
    query = """
        SELECT u.name, u.email, a.timestamp, a.status 
        FROM users u
        LEFT JOIN attendance a ON u.id = a.user_id
        WHERE u.is_admin = 0
        ORDER BY a.timestamp DESC
    """
    cursor.execute(query)
    data = cursor.fetchall()

    # Query to calculate total staff (non-admin users)
    query_total_staff = """
        SELECT COUNT(*) 
        FROM users 
        WHERE is_admin = 0
    """
    cursor.execute(query_total_staff)
    total_staff = cursor.fetchone()[0]

    # Query to calculate total user telat
    query_total_telat = """
        SELECT COUNT(*) 
        FROM users u
        LEFT JOIN attendance a ON u.id = a.user_id
        WHERE u.is_admin = 0 AND a.status = 'telat'
    """
    cursor.execute(query_total_telat)
    total_user_telat = cursor.fetchone()[0]

    # Query to calculate total user tidak telat
    query_total_tidak_telat = """
        SELECT COUNT(*) 
        FROM users u
        LEFT JOIN attendance a ON u.id = a.user_id
        WHERE u.is_admin = 0 AND a.status = 'tidak telat'
    """
    cursor.execute(query_total_tidak_telat)
    total_user_tidak_telat = cursor.fetchone()[0]

    # Query to calculate total user alpha (absent)
    query_total_alpha = """
        SELECT COUNT(*) 
        FROM users u
        LEFT JOIN attendance a ON u.id = a.user_id
        WHERE u.is_admin = 0 AND a.status = 'alpha'
    """
    cursor.execute(query_total_alpha)
    total_user_alpha = cursor.fetchone()[0]

    cursor.close()

    # Pass all totals to the template
    return render_template('admin.html', 
                           data=data, 
                           total_staff=total_staff, 
                           total_user_telat=total_user_telat, 
                           total_user_tidak_telat=total_user_tidak_telat, 
                           total_user_alpha=total_user_alpha)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        tgl_lahir = request.form['tgl_lahir']
        email = request.form['email']
        password = request.form['password']

        # Hash the password using bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Check if email is already registered
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            flash("Email sudah terdaftar!")
            return redirect(url_for('register'))

        # Insert user into database
        cursor.execute("INSERT INTO users (name, username, tgl_lahir, email, password) VALUES (%s, %s, %s, %s, %s)", (name, username, tgl_lahir, email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        flash("Registrasi berhasil! Silakan login.")
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # Retrieve user from database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name, email, username, password, is_admin FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and bcrypt.check_password_hash(user[4], password):  # Assuming user[4] is the password hash field
        session['user_id'] = user[0]
        session['is_admin'] = user[5]  # Store admin status in session
        send_otp(email)
        flash("OTP telah dikirim ke email Anda.")
        return redirect(url_for('verify'))
    else:
        flash("Email atau password salah!")
        return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # Cek apakah email terdaftar di database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            send_otp(email)  # Mengirim OTP ke email pengguna
            session['reset_email'] = email  # Simpan email di session untuk nanti
            flash("OTP telah dikirim ke email Anda.")
            return redirect(url_for('reset_password'))
        else:
            flash("Email tidak terdaftar!")
            return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        input_otp = request.form['otp']
        new_password = request.form['new_password']

        if input_otp == otp:  # Verifikasi OTP
            email = session.get('reset_email')

            if email:
                # Hash password baru dan perbarui di database
                hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                cursor = mysql.connection.cursor()
                cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
                mysql.connection.commit()
                cursor.close()

                flash("Password berhasil direset! Silakan login.")
                return redirect(url_for('index'))
            else:
                flash("Sesi berakhir. Silakan coba lagi.")
                return redirect(url_for('forgot_password'))
        else:
            flash("Kode OTP salah!")
            return redirect(url_for('reset_password'))

    return render_template('reset_password.html')

@app.route('/verify')
@login_required
def verify():
    return render_template('verify.html')

# verifikasi OTP
@app.route('/verify-otp', methods=['POST'])
@login_required
def verify_otp_route():
    input_otp = request.form['otp']
    if input_otp == otp:
        # OTP Berhasil
        session['verified'] = True
        is_admin = session.get('is_admin')
        
        if is_admin:
            flash("Berhasil verifikasi OTP! Selamat datang Admin.")
            return redirect(url_for('admin_page'))
        else:
            flash("Berhasil verifikasi OTP!")
            return redirect(url_for('success'))
    else:
        flash("Kode OTP salah, silakan coba lagi.")
        return redirect(url_for('verify'))

@app.route('/admin/profile/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile():
    user_id = session.get('user_id')

    # Retrieve current user data
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT name, username, tgl_lahir, email FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        tgl_lahir = request.form['tgl_lahir']
        email = request.form['email']

        # Update the user profile
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE users 
            SET name = %s, username = %s, tgl_lahir = %s, email = %s 
            WHERE id = %s
        """, (name, username, tgl_lahir, email, user_id))
        mysql.connection.commit()
        cursor.close()

        flash('Profile updated successfully!')
        return redirect(url_for('profile'))

    return render_template('admin_profile.html', user=user)


@app.route('/success')
@login_required
def success():
    if not session.get('verified'):
        return redirect(url_for('verify'))
    return render_template('success.html')

def delete_attendance():
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM attendance")
        mysql.connection.commit()
        cursor.close()
        print("Data absensi telah dihapus pada jam 00:00")

# Fungsi untuk menandai absensi otomatis sebagai alpha jika user belum absensi sampai jam 10:00
def mark_alpha_for_absent_users():
    with app.app_context():
        current_date = datetime.now().date()

        try:
            # Mendapatkan semua user yang tidak absensi hari ini
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT id FROM users 
                WHERE id NOT IN (
                    SELECT user_id FROM attendance WHERE DATE(timestamp) = %s
                )
            """, (current_date,))
            absent_users = cursor.fetchall()

            # Bulk insert untuk menandai absensi sebagai alpha
            if absent_users:
                absent_values = [(user[0], datetime.now(), 'alpha') for user in absent_users]
                cursor.executemany("INSERT INTO attendance (user_id, timestamp, status) VALUES (%s, %s, %s)", absent_values)

            mysql.connection.commit()
            cursor.close()

            print(f"Absensi otomatis ditandai sebagai alpha untuk {len(absent_users)} user pada jam 10:00")
        
        except Exception as e:
            print(f"Terjadi kesalahan saat menandai alpha: {e}")

# Jadwalkan pengecekan absensi setiap hari pada jam 10:00
scheduler.add_job(mark_alpha_for_absent_users, 'cron', hour=10, minute=0)

# Jadwalkan penghapusan data absensi setiap hari pada jam 00:00
scheduler.add_job(delete_attendance, 'cron', hour=0, minute=0)

@app.route('/attendance', methods=['POST'])
@login_required
def attendance():
    user_id = session.get('user_id')
    
    # Cek apakah pengguna sudah melakukan absensi hari ini
    today = datetime.now().date()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM attendance WHERE user_id = %s AND DATE(timestamp) = %s", (user_id, today))
    attendance = cursor.fetchone()

    if attendance:
        flash("Anda sudah melakukan absensi hari ini.")
        return redirect(url_for('profile'))

    # Lanjutkan proses absensi jika belum absen
    izin = request.form.get('izin', '').strip()
    current_time = datetime.now()
    current_time_only = current_time.time()

    if current_time_only > datetime.strptime('11:10:00', '%H:%M:%S').time():
        status = "Tidak ada keterangan/alpha"
    elif datetime.strptime('08:00:00', '%H:%M:%S').time() <= current_time_only <= datetime.strptime('10:00:00', '%H:%M:%S').time():
        status = "izin" if izin else "telat"
    else:
        status = "tidak telat"

    cursor.execute("INSERT INTO attendance (user_id, timestamp, status, izin) VALUES (%s, NOW(), %s, %s)", (user_id, status, izin))
    mysql.connection.commit()
    cursor.close()

    flash("Absensi berhasil dilakukan!")
    return redirect(url_for('profile'))


if __name__ == '__main__':
    # Pastikan scheduler dijalankan bersama aplikasi
    scheduler.start()
    app.run(debug=True)

@app.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id')

    # Ambil data profil pengguna dari database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT name, username, tgl_lahir, email FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    # Cek apakah pengguna sudah melakukan absensi hari ini
    today = datetime.now().date()
    cursor.execute("SELECT * FROM attendance WHERE user_id = %s AND DATE(timestamp) = %s", (user_id, today))
    attendance = cursor.fetchone()
    cursor.close()

    # Kirim status absensi (True jika sudah absen) ke template
    already_attended = bool(attendance)

    return render_template('userpage.html', user=user, already_attended=already_attended)


@app.route('/export-attendance')
@login_required
@admin_required
def export_attendance():
    # Fetch all attendance data for non-admin users
    cursor = mysql.connection.cursor()
    query = """
        SELECT u.name, u.email, a.timestamp, a.status 
        FROM users u
        LEFT JOIN attendance a ON u.id = a.user_id
        WHERE u.is_admin = 0
        ORDER BY a.timestamp DESC
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()

    # Mengconvert menggunakan pandas
    df = pd.DataFrame(data, columns=['Name', 'Email', 'Timestamp', 'Status'])

    # Create a BytesIO buffer to save the Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')

    output.seek(0)

    # Send the Excel file as a downloadable response
    return send_file(output, download_name="attendance_data.xlsx", as_attachment=True)

@app.route('/announcements')
@login_required
def announcements():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM announcements ORDER BY created_at DESC")
    announcements = cursor.fetchall()
    cursor.close()
    return render_template('announcements.html', announcements=announcements)

@app.route('/create-announcement', methods=['GET', 'POST'])
@login_required
@admin_required
def create_announcement():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO announcements (title, content) VALUES (%s, %s)", (title, content))
        mysql.connection.commit()
        cursor.close()
        flash("Announcement created successfully!")
        return redirect(url_for('announcements'))
    return render_template('create_announcement.html')

@app.route('/edit-announcement/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_announcement(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM announcements WHERE id = %s", (id,))
    announcement = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE announcements SET title = %s, content = %s WHERE id = %s", (title, content, id))
        mysql.connection.commit()
        cursor.close()
        flash("Announcement updated successfully!")
        return redirect(url_for('announcements'))

    return render_template('edit_announcement.html', announcement=announcement)

@app.route('/user/announcements')
@login_required
def user_announcements():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM announcements")  # Assuming you have a table 'announcements'
    announcements = cursor.fetchall()
    cursor.close()
    
    return render_template('user_announcements.html', announcements=announcements)

@app.route('/check_attendance', methods=['GET'])
@login_required
def check_attendance():
    user_id = session.get('user_id')
    today = datetime.now().date()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM attendance WHERE user_id = %s AND DATE(timestamp) = %s", (user_id, today))
    attendance = cursor.fetchone()
    cursor.close()

    has_attended = attendance is not None
    return jsonify({'has_attended': has_attended})

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('verified', None)
    session.pop('is_admin', None)
    flash("Anda telah keluar.")
    return redirect(url_for('index'))