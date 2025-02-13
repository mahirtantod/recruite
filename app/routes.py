from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for
from app.models import db, Candidate, Job
import os
from werkzeug.utils import secure_filename
import re
from datetime import datetime

main = Blueprint('main', __name__)

ALLOWED_RESUME_EXTENSIONS = {'pdf', 'doc', 'docx'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov'}

def allowed_resume_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_RESUME_EXTENSIONS

def allowed_video_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

@main.route('/')
def index():
    """Redirect to admin if no specific job link"""
    return redirect(url_for('admin.index'))

@main.route('/apply/<link_hash>')
def apply(link_hash):
    """Handle job-specific application"""
    print(f"Accessing job with link_hash: {link_hash}")  # Debug log
    
    job = Job.query.filter_by(link_hash=link_hash).first_or_404()
    print(f"Found job: {job.id} - {job.title}")  # Debug log
    
    if job.is_expired():
        return render_template('expired.html')
    
    if not job.is_active:
        return render_template('inactive.html')
    
    # Store job_id in session
    session['job_id'] = job.id
    print(f"Stored job_id in session: {job.id}")  # Debug log
    
    session['state'] = 'initial'
    session['candidate_data'] = {}
    
    return render_template('index.html', job=job)

@main.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file provided'})
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    if not allowed_resume_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload PDF or DOC files only.'})
    
    try:
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        resume_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes')
        file.save(os.path.join(resume_folder, filename))
        
        # Store the filename in session with the resumes/ prefix
        candidate_data = session.get('candidate_data', {})
        candidate_data['resume_attachments'] = os.path.join('resumes', filename)
        session['candidate_data'] = candidate_data
        
        return jsonify({'message': 'Resume uploaded successfully'})
    except Exception as e:
        return jsonify({'error': f'Error uploading resume: {str(e)}'})

@main.route('/api/upload-video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({
            'error': 'No file provided',
            'stopRecording': True
        })
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({
            'error': 'No file selected',
            'stopRecording': True
        })
    
    if not allowed_video_file(file.filename):
        return jsonify({
            'error': 'Invalid file type. Please upload MP4 or WebM files only.',
            'stopRecording': True
        })
    
    try:
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_recording.webm")
        video_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos')
        file.save(os.path.join(video_folder, filename))
        
        # Store the filename in session with the videos/ prefix
        candidate_data = session.get('candidate_data', {})
        candidate_data['self_introduction_video'] = os.path.join('videos', filename)
        session['candidate_data'] = candidate_data
        
        return jsonify({
            'message': 'Video uploaded successfully',
            'stopRecording': True
        })
    except Exception as e:
        return jsonify({
            'error': f'Error uploading video: {str(e)}',
            'stopRecording': True
        })

@main.route('/api/chat', methods=['POST'])
def chat():
    try:
        message = request.json.get('message', '').strip()
        state = session.get('state', 'initial')
        candidate_data = session.get('candidate_data', {})
        job_id = session.get('job_id')
        
        print(f"Chat API - Current job_id in session: {job_id}")  # Debug log

        if not job_id:
            print("No job_id found in session!")  # Debug log
            return jsonify({
                'response': 'Session expired. Please start over from the job application link.',
                'completed': False
            })
        
        # Verify job still exists
        job = Job.query.get(job_id)
        if not job:
            print(f"Job with id {job_id} not found!")  # Debug log
            return jsonify({
                'response': 'Invalid job. Please start over from the job application link.',
                'completed': False
            })

        print(f"Processing application for job: {job.id} - {job.title}")  # Debug log

        if state == 'initial':
            # Create a dummy job if none exists
            job = Job.query.first()
            if not job:
                job = Job(title='Software Developer', description='Python Developer Position')
                db.session.add(job)
                db.session.commit()
            
            # Store job_id in session
            session['job_id'] = job.id
            session['state'] = 'greeting'
            session['candidate_data'] = {}  # Initialize empty candidate data
            return jsonify({'response': "Hi! I'm the RecruitEase chatbot. I'll help you with your job application. Let's start with your name. What should I call you?"})

        elif state == 'greeting':
            session['state'] = 'asking_first_name'
            return jsonify({'response': "Great! What is your first name?"})

        elif state == 'asking_first_name':
            if not re.match(r'^[a-zA-Z\s]+$', message):
                return jsonify({'response': 'First name must contain only alphabets. Please try again:'})
            candidate_data['first_name'] = message.strip()
            session['state'] = 'asking_last_name'
            session['candidate_data'] = candidate_data
            return jsonify({'response': 'What is your last name?'})

        elif state == 'asking_last_name':
            if not re.match(r'^[a-zA-Z\s]+$', message):
                return jsonify({'response': 'Last name must contain only alphabets. Please try again:'})
            candidate_data['last_name'] = message.strip()
            session['state'] = 'asking_email'
            session['candidate_data'] = candidate_data
            return jsonify({'response': 'Please enter your personal email address:'})

        elif state == 'asking_email':
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message):
                return jsonify({'response': 'Invalid email format. Please enter a valid email address:'})
            candidate_data['personal_email'] = message.strip()
            session['state'] = 'asking_mobile'
            session['candidate_data'] = candidate_data
            return jsonify({'response': 'Please enter your 10-digit mobile number:'})

        elif state == 'asking_mobile':
            if not re.match(r'^\d{10}$', message):
                return jsonify({'response': 'Mobile number must be exactly 10 digits. Please try again:'})
            candidate_data['mobile_no'] = message.strip()
            session['state'] = 'asking_alternate_mobile'
            session['candidate_data'] = candidate_data
            return jsonify({'response': 'Would you like to provide an alternate contact number? (Enter the number or type "skip"):'})

        elif state == 'asking_alternate_mobile':
            if message.lower() != 'skip':
                if not re.match(r'^\d{10}$', message):
                    return jsonify({'response': 'Alternate number must be exactly 10 digits. Please try again or type "skip":'})
                candidate_data['alternate_contact_no'] = message.strip()
            session['state'] = 'asking_education'
            session['candidate_data'] = candidate_data
            return jsonify({'response': 'What is your highest educational qualification?'})

        elif state == 'asking_education':
            candidate_data['highest_educational_qualifications'] = message.strip()
            session['state'] = 'asking_academic'
            session['candidate_data'] = candidate_data
            return jsonify({'response': 'Please enter your academic performance (e.g., "8.5 CGPA" or "75%"):'})

        elif state == 'asking_academic':
            candidate_data['academic_performance'] = message.strip()
            session['state'] = 'asking_company'
            session['candidate_data'] = candidate_data
            return jsonify({'response': 'Are you currently employed? If yes, please enter your company name (or type "no"):'})

        elif state == 'asking_company':
            if message.lower() != 'no':
                candidate_data['current_company'] = message.strip()
                session['state'] = 'asking_designation'
                session['candidate_data'] = candidate_data
                return jsonify({'response': 'What is your current designation?'})
            else:
                candidate_data['total_experience'] = 0
                candidate_data['relevant_experience'] = 0
                session['state'] = 'asking_skills'
                session['candidate_data'] = candidate_data
                return jsonify({'response': 'Please enter your primary skills (comma-separated):'})

        elif state == 'asking_designation':
            candidate_data['current_designation'] = message.strip()
            session['state'] = 'asking_total_experience'
            session['candidate_data'] = candidate_data
            return jsonify({'response': 'Please enter your total work experience in years (e.g., 2.5):'})

        elif state == 'asking_total_experience':
            try:
                exp = float(message)
                if exp < 0:
                    return jsonify({'response': 'Experience cannot be negative. Please try again:'})
                candidate_data['total_experience'] = exp
                session['state'] = 'asking_relevant_experience'
                session['candidate_data'] = candidate_data
                return jsonify({'response': 'Please enter your relevant experience in years:'})
            except ValueError:
                return jsonify({'response': 'Please enter a valid number for experience (e.g., 2.5):'})

        elif state == 'asking_relevant_experience':
            try:
                exp = float(message)
                if exp < 0:
                    return jsonify({'response': 'Experience cannot be negative. Please try again:'})
                candidate_data['relevant_experience'] = exp
                session['state'] = 'asking_skills'
                session['candidate_data'] = candidate_data
                return jsonify({'response': 'Please enter your primary skills (comma-separated):'})
            except ValueError:
                return jsonify({'response': 'Please enter a valid number for experience (e.g., 2.5):'})

        elif state == 'asking_skills':
            candidate_data['primary_skills'] = message.strip()
            session['state'] = 'asking_resume'
            session['candidate_data'] = candidate_data
            return jsonify({'response': 'Please upload your resume (PDF/DOC format):'})

        elif state == 'asking_resume':
            if message.lower() == 'resume uploaded':
                session['state'] = 'asking_video'
                session['candidate_data'] = candidate_data
                return jsonify({'response': 'Great! Now, please record a short self-introduction video (maximum 2 minutes):'})
            return jsonify({'response': 'Please use the upload button to submit your resume.'})

        elif state == 'asking_video':
            if message.lower() == 'video uploaded':
                session['state'] = 'asking_referral'
                session['candidate_data'] = candidate_data
                return jsonify({'response': 'Were you referred by someone? If yes, please enter their name (or type "no"):'})
            return jsonify({'response': 'Please use the record button to submit your video.'})

        elif state == 'asking_referral':
            if message.lower() != 'no':
                candidate_data['referred_by'] = message.strip()
            session['state'] = 'asking_declaration'
            session['candidate_data'] = candidate_data
            return jsonify({'response': 'Please confirm that all information provided is true and accurate (type "yes" to confirm):'})

        elif state == 'asking_declaration':
            if message.lower() != 'yes':
                return jsonify({'response': 'You must confirm the declaration to proceed. Type "yes" to confirm:'})
            
            try:
                # Create candidate object with the correct job_id
                candidate = Candidate(
                    job_id=job_id,  # Use the job_id from session
                    first_name=candidate_data['first_name'],
                    last_name=candidate_data['last_name'],
                    personal_email=candidate_data['personal_email'],
                    mobile_no=candidate_data['mobile_no'],
                    alternate_contact_no=candidate_data.get('alternate_contact_no'),
                    highest_educational_qualifications=candidate_data['highest_educational_qualifications'],
                    academic_performance=candidate_data['academic_performance'],
                    current_company=candidate_data.get('current_company'),
                    current_designation=candidate_data.get('current_designation'),
                    total_experience=float(candidate_data['total_experience']),
                    relevant_experience=float(candidate_data['relevant_experience']),
                    primary_skills=candidate_data['primary_skills'],
                    resume_attachments=candidate_data.get('resume_attachments'),
                    self_introduction_video=candidate_data.get('self_introduction_video'),
                    referred_by=candidate_data.get('referred_by'),
                    self_declaration=True,
                    submitted_at=datetime.utcnow()
                )
                
                print(f"About to save candidate for job: {job.id} - {job.title}")  # Debug log
                
                db.session.add(candidate)
                db.session.commit()
                
                print(f"Successfully saved candidate with ID: {candidate.id} for job: {job.id} - {job.title}")  # Debug log
                
                # Clear session after successful save
                session.clear()
                
                return jsonify({
                    'response': 'Thank you for completing your application! We will review your information and get back to you soon.',
                    'completed': True,
                    'stopRecording': True
                })
            except Exception as e:
                db.session.rollback()
                print(f"Error saving candidate: {str(e)}")
                print(f"Current session data: {session.get('candidate_data')}")
                return jsonify({
                    'response': f'Error saving your application: {str(e)}. Please try again.',
                    'stopRecording': True
                })

        # Rest of the chat logic...
        session['candidate_data'] = candidate_data
        return jsonify({'response': 'Invalid state. Please start over.'})

    except Exception as e:
        print(f"Error in chat route: {str(e)}")  # Debug log
        return jsonify({'response': f'An error occurred: {str(e)}. Please try again.'})
