from app import create_app, db
from app.models import Candidate, Job
from datetime import datetime

def view_database():
    app = create_app()
    with app.app_context():
        print("\n=== Jobs ===")
        jobs = Job.query.all()
        for job in jobs:
            print(f"Job ID: {job.id}")
            print(f"Title: {job.title}")
            print(f"Description: {job.description}")
            print("-" * 50)
        
        print("\n=== Candidates ===")
        candidates = Candidate.query.all()
        
        if not candidates:
            print("No candidates found in the database.")
            return
        
        for candidate in candidates:
            print("\nCandidate Details:")
            print("=" * 50)
            print(f"ID: {candidate.id}")
            print(f"Job ID: {candidate.job_id}")
            print(f"Name: {candidate.first_name} {candidate.last_name}")
            print(f"Personal Email: {candidate.personal_email}")
            print(f"Mobile Number: {candidate.mobile_no}")
            print(f"Alternate Contact Number: {candidate.alternate_contact_no or 'N/A'}")
            print(f"Highest Educational Qualification: {candidate.highest_educational_qualifications}")
            print(f"Academic Performance: {candidate.academic_performance}")
            print(f"Current Company: {candidate.current_company or 'N/A'}")
            print(f"Current Designation: {candidate.current_designation or 'N/A'}")
            print(f"Total Experience: {candidate.total_experience} years")
            print(f"Relevant Experience: {candidate.relevant_experience} years")
            print(f"Primary Skills: {candidate.primary_skills}")
            print(f"Resume Attachments: {candidate.resume_attachments or 'N/A'}")
            print(f"Self-Introduction Video: {candidate.self_introduction_video or 'N/A'}")
            print(f"Referred By: {candidate.referred_by or 'N/A'}")
            print(f"Self-Declaration: {'Yes' if candidate.self_declaration else 'No'}")
            print(f"Submitted At: {candidate.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if candidate.submitted_at else 'N/A'}")
            print("=" * 50)

def main():
    print("RecruitEase Database Viewer")
    print("=" * 30)
    try:
        view_database()
    except Exception as e:
        print(f"Error viewing database: {str(e)}")
    
    print("\nTo view the web interface, run the Flask app and visit:")
    print("http://127.0.0.1:5000/admin/candidates")

if __name__ == "__main__":
    main()
