import random
import smtplib
from email.message import EmailMessage

otp = ""
for i in range(5):
    otp += str(random.randint(0, 9))

server = smtplib.SMTP('smtp.gmail.com', 587)

server.starttls()

email = 'alpiyangini@gmail.com'
server.login("alpiyangini@gmail.com", "agcf upsy qcyr xehk")
to_mail = input("Masukkan alamat emailmu: ")

msg = EmailMessage()
msg['Subject'] = "Verifikasi OTP"
msg['from'] = email
msg['to'] = to_mail
msg.set_content(f"Kode verifikasi OTP Anda adalah: " + otp)

server.send_message(msg)

input_otp = input("Masukkan kode OTP: ")
if input_otp == otp:
    print("Berhasil verfikasi OTP")
else:
    print("Kode OTP salah")

print("Email terkirim.")