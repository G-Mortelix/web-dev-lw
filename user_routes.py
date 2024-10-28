from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Flask, current_app
from random import choice
import feedparser, spacy, os, gspread, smtplib, datetime, requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from bs4 import BeautifulSoup
from extensions import db
from model_db import News, add_inquiry, get_inquiries, get_inquiry_by_id
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
nlp = spacy.load("en_core_web_sm")

SENDER_EMAIL = os.getenv('sendermail')  # Your personal email for now
SENDER_PASSWORD = os.getenv('senderpw')  # Your personal email password
RECIPIENT_EMAIL = os.getenv('recipientmail')

g_credpath = os.getenv('g_api_cred')
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file", "https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
drive_creds = Credentials.from_service_account_file(g_credpath, scopes=DRIVE_SCOPES)
drive_service = build('drive', 'v3', credentials=drive_creds)

FOLDER_ID = '138OTG4Dg8M7LROJBTQPm_RTTerSlz6QF'
ALLOWED_EXTENSIONS = {'pdf'} 


scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(g_credpath, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("JobPostings").worksheet("jobpositions")

app = Flask(__name__)
user_bp = Blueprint('user_bp', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/')
def home():
    return render_template('home.html')

@user_bp.route('/about')
def about():
    return render_template('about.html')

@user_bp.route('/services')
def services():
    return render_template('services.html')

#service routes
@user_bp.route('/services/<service>')
def service_detail(service):
    valid_services = ['bookkeeping', 'business-administration', 'human-resources']

    if service in valid_services:
        return render_template('service-detail.html', service=service)
    else:
        return render_template('service-detail.html', service='not-found'), 404

@user_bp.route('/events')
def events():
    return render_template('events.html')

#career routes
@user_bp.route('/career')
def career():
    return render_template('career.html')

@user_bp.route('/career/<string:group>')
def career_by_group(group):
    jobs = sheet.get_all_records()
    filtered_jobs = [job for job in jobs if job['Group'] == group]
    return render_template('career-group.html', jobs=filtered_jobs, group=group)

@user_bp.route('/get-job-positions/<string:group>', methods=['GET'])
def get_job_positions(group):
    jobs = sheet.get_all_records() 
    filtered_jobs = [{'id': job['Job ID'], 'position': job['Position']} for job in jobs if job['Group'] == group]
    return jsonify(filtered_jobs)  

#news section
def clean_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text()

@user_bp.route('/news')
def news_list():
    # Fetch the latest 10 government news
    articles = News.query.filter(News.category.in_(['Announcement', 'Infomercial'])).order_by(News.id.desc()).limit(10).all()
    return render_template('news.html', articles=articles)

@user_bp.route('/news/<int:news_id>')
def news_detail(news_id):
    article = News.query.get_or_404(news_id)
    return render_template('news-detail.html', article=article)

#contact section
@user_bp.route('/contact')
def contact():
    return render_template('contact.html')

def send_inquiry_email(name, user_email, subject, message):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL  
    msg['Subject'] = f"Inquiry from {name}: {subject}"
    msg['Reply-To'] = user_email  

    # Email body
    body = f"Name: {name}\nEmail: {user_email}\nSubject: {subject}\n\nMessage:\n{message}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Set up the SMTP server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")

@user_bp.route('/submit-inquiry', methods=['POST'])
def submit_inquiry():
    name = request.form['name']
    user_email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    add_inquiry(name, user_email, subject, message)
    send_inquiry_email(name, user_email, subject, message)
    
    flash('Inquiry submitted successfully!')
    return redirect(url_for('user_bp.contact'))
