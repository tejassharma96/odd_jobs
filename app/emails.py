from flask_mail import Message
from flask import render_template
from app import mail
from config import ADMINS

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def send_job_email(job):
    employer = job.employer
    employee = job.employee
    if employee is None or employer is None:
        return
    
    text = render_template('job_email.txt',
                           employee=employee,
                           employer=employer)

    html = render_template('job_email.html',
                           employee=employee,
                           employer=employer)

    send_email(subject='Odd Jobs Introduction!',
               sender=ADMINS[0],
               recipients=[employer.email, employee.email],
               text_body=text,
               html_body=html)