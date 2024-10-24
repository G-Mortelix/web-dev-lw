from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, Flask, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from google.oauth2.service_account import Credentials
import gspread, requests, uuid, os
from extensions import db
from model_db import Admin, News, Inquiry, get_inquiries, get_inquiry_by_id
from dotenv import load_dotenv
from functools import wraps

admin_bp = Blueprint('admin_bp', __name__)

limiter = Limiter(key_func=get_remote_address)

g_credpath = os.getenv('g_api_cred')
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(g_credpath, scopes=scope)
client = gspread.authorize(creds)
sheet_jobapplicants = client.open("JobPostings").worksheet("applications")

try: 
    sheet_jobposition = client.open("JobPostings").worksheet("jobpositions")
except Exception as e:
    print(f"Error opening the sheet: {e}")
    flash("Could not access Google Sheet. Please check your connection or credentials.")

def init_app(app):
    limiter.init_app(app)

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:  
            flash("Please log in to access the admin dashboard.", "error")
            return redirect(url_for('admin_bp.admin_login'))  
        if current_user.role != 'admin':  
            flash("You do not have permission to access this page.", "error")
            return redirect(url_for('admin_bp.admin_login'))  
        return func(*args, **kwargs)
    return decorated_view

#login routes
@admin_bp.route('/admin-login', methods=['GET', 'POST'])
@limiter.limit("8 per minute")
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
 
        admin = Admin.query.filter_by(username=username).first()

        if admin:
            if admin.check_password(password):
                print("Password matched successfully!")
                login_user(admin)
                return redirect(url_for('admin_bp.admin_dashboard'))
            else:
                print("Password did not match!")
        else:
            print("No admin found with that username.")

        flash('Invalid credentials, please try again.')
    
    return render_template('admin/admin-login.html')

#homepage for admin
@admin_bp.route('/admin/admin-dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/admin-dashboard.html')

#job management
@admin_bp.route('/admin/manage-jobs')
@login_required
@admin_required
def manage_jobs():
    jobs = sheet_jobposition.get_all_records() 
    return render_template('admin/manage-jobs.html', jobs=jobs)

@admin_bp.route('/admin/add-job', methods=['GET', 'POST'])
@login_required
@admin_required
def add_job():
    if request.method == 'POST':
        title = request.form['title']
        group = request.form['group']
        description = request.form['description']
        requirements = request.form['requirements']
        location = request.form['location']
        status = request.form['status']
        post_date = request.form['post_date']
        notes = request.form['notes']

        job_uuid = str(uuid.uuid4())

        sheet_jobposition.append_row([job_uuid, title, description, requirements, group, location, status, post_date, notes])

        return redirect(url_for('admin_bp.manage_jobs'))
    return render_template('admin/add-job.html')

@admin_bp.route('/admin/edit-job/<string:job_uuid>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_job(job_uuid):
    jobs = sheet_jobposition.get_all_records()

    job_index = next((i for i, job in enumerate(jobs) if job['UUID'] == str(job_uuid)), None)
 
    if job_index is None:
        flash('Job not found!', 'error')
        return redirect(url_for('admin_bp.manage_jobs'))

    job = jobs[job_index]  # Get job details

    try:
        job['Post Date'] = datetime.strptime(job['Post Date'], '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError:
        job['Post Date'] = job['Post Date']

    if request.method == 'POST':
        # Update the job details
        title = request.form['title']
        description = request.form['description']
        requirements = request.form['requirements']
        group = request.form['group']
        location = request.form['location']
        status = request.form['status']
        post_date = request.form['post_date']
        notes = request.form['notes']

        # Update the row with new data
        sheet_jobposition.update(f'A{job_index + 2}', [[job_uuid, title, description, requirements, group, location, status, post_date, notes]])

        return redirect(url_for('admin_bp.manage_jobs'))
    
    return render_template('admin/edit-job.html', job=job, job_uuid=job_uuid)

@admin_bp.route('/admin/delete-job/<string:job_uuid>')
@login_required
@admin_required
def delete_job(job_uuid):
    jobs = sheet_jobposition.get_all_records()
    
    # Find the row with the matching UUID
    row_to_delete = None
    for idx, job in enumerate(jobs, start=2):  
        if job['UUID'] == job_uuid:
            row_to_delete = idx
            break

    if row_to_delete:
            sheet_jobposition.delete_rows(row_to_delete)
            flash('Job deleted successfully.', 'success')
    else:
        flash('Job not found.', 'error')

    return redirect(url_for('admin_bp.manage_jobs'))

@admin_bp.route('/admin/view-applications')
@login_required
@admin_required
def view_applications():
    applications = sheet_jobapplicants.get_all_records()  

    for app in applications:
        contact_number = str(app.get('Contact Number', ''))
        ic_number = str(app.get('IC Number', ''))

        # Fix Contact Number (prepend '0' if necessary)
        if (len(contact_number) == 9 or len(contact_number) == 10) and not contact_number.startswith("0"):
            contact_number = "0" + contact_number

        # Fix IC Number (do not add an extra '0' if it already starts with '0')
        if len(ic_number) > 1 and not ic_number.startswith("0"):
            ic_number = "0" + ic_number

        app['Contact Number'] = contact_number
        app['IC Number'] = ic_number

        # Format the date if necessary
        date_submitted = app.get('Timestamp')
        if date_submitted:
            try:
                app['Date Submitted'] = datetime.strptime(date_submitted, '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d')
            except ValueError:
                app['Date Submitted'] = date_submitted

    return render_template('admin/view-applications.html', applications=applications)

#news management
@admin_bp.route('/admin/manage-news')
@login_required
@admin_required
def manage_news():
    all_news = News.query.all()  # Retrieve all news
    return render_template('admin/manage-news.html', news_list=all_news)

@admin_bp.route('/admin/add-news', methods=['GET', 'POST'])
@login_required
@admin_required
def add_news():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        source = request.form['source']
        image_url = request.form['image_url']

        new_article = News(
            title=title,
            content=content,
            category=category,
            source=source,
            image_url=image_url
        )
        db.session.add(new_article)
        db.session.commit()

        flash('News article added successfully!')
        return redirect(url_for('admin_bp.manage_news'))

    return render_template('admin/add-news.html')

#edit existing news
@admin_bp.route('/admin/edit-news/<int:news_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_news(news_id):
    news_article = News.query.get_or_404(news_id)

    if request.method == 'POST':
        news_article.title = request.form['title']
        news_article.content = request.form['content']
        news_article.category = request.form['category']
        news_article.source = request.form['source']
        news_article.image_url = request.form['image_url']

        db.session.commit()
        flash('News article updated successfully!')
        return redirect(url_for('admin_bp.manage_news'))

    return render_template('admin/edit-news.html', news=news_article)

#delete news
@admin_bp.route('/admin/delete-news/<int:news_id>', methods=['POST'])
@login_required
@admin_required
def delete_news(news_id):
    news_article = News.query.get_or_404(news_id)
    db.session.delete(news_article)
    db.session.commit()

    flash('News article deleted successfully!')
    return redirect(url_for('admin_bp.manage_news'))

#inquiries management
@admin_bp.route('/admin/view-inquiries')
@login_required
@admin_required
def view_inquiries():
    inquiries = get_inquiries()
    return render_template('admin/view-inquiries.html', inquiries=inquiries)

@admin_bp.route('/admin/reply-inquiry/<int:inquiry_id>', methods=['GET'])
@login_required
@admin_required
def reply_inquiry(inquiry_id):
    inquiry = get_inquiry_by_id(inquiry_id)
    
    user_email = inquiry.email  
    subject = f"Reply to your inquiry: {inquiry.subject}"  
    mailto_link = f"mailto:{user_email}?subject={subject}&body=Dear {inquiry.name},%0D%0A%0D%0A"  
    
    # Redirect admin to mailto link
    return redirect(mailto_link)

@admin_bp.route('/admin/delete-inquiry/<int:inquiry_id>', methods=['POST', 'GET'])
@login_required
@admin_required
def delete_inquiry(inquiry_id):
    inquiry = get_inquiry_by_id(inquiry_id)
    
    if not inquiry:
        flash('Inquiry not found.', 'error')
        return redirect(url_for('admin_bp.view_inquiries'))

    try:
        # Delete the inquiry from the database
        db.session.delete(inquiry)
        db.session.commit()
        flash('Inquiry deleted successfully.', 'success')
    except Exception as e:
        flash(f"Error deleting inquiry: {str(e)}", 'error')
    
    return redirect(url_for('admin_bp.view_inquiries'))


#logout
@admin_bp.route('/admin/logout')
@login_required
@limiter.exempt
def admin_logout():
    logout_user()
    return redirect(url_for('admin_bp.admin_login')) 
