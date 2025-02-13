from app import db
from datetime import datetime, timedelta
from sqlalchemy.orm import validates
import secrets
import re

class Job(db.Model):
    """Job model to store available positions"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link_hash = db.Column(db.String(50), unique=True)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    candidates = db.relationship('Candidate', backref='job', lazy=True)

    def generate_link(self, days_valid=10):
        """Generate a unique link hash and set expiry date"""
        self.link_hash = secrets.token_urlsafe(16)
        self.start_date = datetime.utcnow()
        self.end_date = self.start_date + timedelta(days=days_valid)
        self.is_active = True
        return self.link_hash

    def is_expired(self):
        """Check if the job posting has expired"""
        return datetime.utcnow() > self.end_date if self.end_date else False

    def get_application_link(self):
        """Get the full application link"""
        # Note: Replace with your actual domain when deploying
        return f"/apply/{self.link_hash}"

class Candidate(db.Model):
    """Candidate model with all required fields and validations"""
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    personal_email = db.Column(db.String(120), nullable=False)  
    mobile_no = db.Column(db.String(15), nullable=False)
    alternate_contact_no = db.Column(db.String(15))
    highest_educational_qualifications = db.Column(db.String(200), nullable=False)
    academic_performance = db.Column(db.String(50), nullable=False)
    current_company = db.Column(db.String(100))
    current_designation = db.Column(db.String(100))
    total_experience = db.Column(db.Float, nullable=False)
    relevant_experience = db.Column(db.Float, nullable=False)
    primary_skills = db.Column(db.Text, nullable=False)
    resume_attachments = db.Column(db.String(255), nullable=False)
    self_introduction_video = db.Column(db.String(255))
    referred_by = db.Column(db.String(100))
    self_declaration = db.Column(db.Boolean, nullable=False, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    @validates('job_id')
    def validate_job(self, key, value):
        if not value:
            raise ValueError("Job ID is required")
        if not Job.query.get(value):
            raise ValueError("Invalid Job ID")
        return value

    @validates('first_name', 'last_name')
    def validate_name(self, key, value):
        if not value:
            raise ValueError(f"{key} is required")
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValueError(f"{key} must contain only alphabets and spaces")
        if len(value) > 50:
            raise ValueError(f"{key} must be less than 50 characters")
        return value

    @validates('personal_email')
    def validate_email(self, key, value):
        if not value:
            raise ValueError("Email is required")
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise ValueError("Invalid email format")
        if len(value) > 120:
            raise ValueError("Email must be less than 120 characters")
        return value

    @validates('mobile_no', 'alternate_contact_no')
    def validate_phone(self, key, value):
        if value:  # alternate_contact_no is optional
            if not re.match(r'^\d{10}$', value):
                raise ValueError(f"{key} must be a 10-digit number")
            if len(value) > 15:
                raise ValueError(f"{key} must be less than 15 characters")
        elif key == 'mobile_no':  # mobile_no is required
            raise ValueError("Mobile number is required")
        return value

    @validates('highest_educational_qualifications')
    def validate_education(self, key, value):
        if not value:
            raise ValueError("Educational qualification is required")
        if len(value) > 200:
            raise ValueError("Educational qualification must be less than 200 characters")
        return value

    @validates('academic_performance')
    def validate_academic(self, key, value):
        if not value:
            raise ValueError("Academic performance is required")
        try:
            if 'cgpa' in value.lower():
                score = float(re.search(r'\d+(\.\d+)?', value).group())
                if not 0 <= score <= 10:
                    raise ValueError("CGPA must be between 0 and 10")
            else:
                score = float(re.search(r'\d+(\.\d+)?', value).group())
                if not 0 <= score <= 100:
                    raise ValueError("Percentage must be between 0 and 100")
        except (ValueError, AttributeError):
            raise ValueError("Invalid academic performance format")
        return value

    @validates('current_company', 'current_designation', 'referred_by')
    def validate_optional_strings(self, key, value):
        if value and len(value) > 100:
            raise ValueError(f"{key} must be less than 100 characters")
        return value

    @validates('total_experience', 'relevant_experience')
    def validate_experience(self, key, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{key} must be a number")
        
        if value < 0:
            raise ValueError(f"{key} cannot be negative")
        
        if key == 'relevant_experience' and hasattr(self, 'total_experience'):
            if value > self.total_experience:
                raise ValueError("Relevant experience cannot exceed total experience")
        return value

    @validates('primary_skills')
    def validate_skills(self, key, value):
        if not value:
            raise ValueError("Primary skills are required")
        skills = [s.strip() for s in value.split(',')]
        if len(skills) > 3:
            raise ValueError("Maximum 3 primary skills are allowed")
        if len(value) > 255:
            raise ValueError("Skills must be less than 255 characters total")
        return value

    @validates('resume_attachments')
    def validate_resume(self, key, value):
        if not value:
            raise ValueError("Resume attachment is required")
        if not value.lower().endswith(('.pdf', '.doc', '.docx')):
            raise ValueError("Resume must be in PDF or DOC format")
        if len(value) > 255:
            raise ValueError("File path must be less than 255 characters")
        return value

    @validates('self_introduction_video')
    def validate_video(self, key, value):
        if value and len(value) > 255:
            raise ValueError("Video path must be less than 255 characters")
        return value

    @validates('self_declaration')
    def validate_declaration(self, key, value):
        if not value:
            raise ValueError("You must accept the self declaration")
        return value

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "personal_email": self.personal_email,
            "mobile_no": self.mobile_no,
            "alternate_contact_no": self.alternate_contact_no,
            "highest_educational_qualifications": self.highest_educational_qualifications,
            "academic_performance": self.academic_performance,
            "current_company": self.current_company,
            "current_designation": self.current_designation,
            "total_experience": self.total_experience,
            "relevant_experience": self.relevant_experience,
            "primary_skills": self.primary_skills,
            "resume_attachments": self.resume_attachments,
            "self_introduction_video": self.self_introduction_video,
            "referred_by": self.referred_by,
            "self_declaration": self.self_declaration,
            "submitted_at": self.submitted_at.isoformat()
        }

    def __repr__(self):
        return f'<Candidate {self.first_name} {self.last_name}>'
