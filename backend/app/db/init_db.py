# Demo-data initialization run during application startup. Checks for existing
# accounts or table contents avoid recreating those samples on each restart.
# Company names, people and recruitment records below are demonstration data.

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.database import engine, Base
from app.db.models import (
    User, Student, RecruiterProfile, Skill, StudentSkill,
    Internship, Notification, SavedInternship, Application, Interview, Message
)
from app.core.security import get_password_hash
from app.core.avatars import pick_avatar


# Create tables if absent, then insert missing demonstration accounts and data.
# Each explicit commit makes that batch persistent before later seed steps run.
def init_db(db: Session):
    # Create tables if missing (MySQL).
    Base.metadata.create_all(bind=engine)

    # ── Seed Platform Admin ──────────────────────────────────────────────
    # Separate login flow at /api/admin/login (the regular login rejects admins).
    if not db.query(User).filter(User.email == "admin@hirehub.com").first():
        db.add(User(
            email="admin@hirehub.com",
            password_hash=get_password_hash("admin123"),
            role="admin", is_active=True,
        ))
        db.commit()

    # ── Seed Skills ──────────────────────────────────────────────────────
    if db.query(Skill).count() == 0:
        skills_data = [
            ("React.js", "Engineering"), ("TypeScript", "Engineering"),
            ("Node.js", "Engineering"), ("Python", "Engineering"),
            ("FastAPI", "Engineering"), ("Tailwind CSS", "Engineering"),
            ("SQL & MySQL", "Engineering"), ("Figma", "Design"),
            ("UI/UX Design", "Design"), ("Data Analysis", "Data Science"),
            ("Machine Learning", "Data Science"), ("Product Management", "Management"),
            ("Digital Marketing", "Marketing"), ("Next.js", "Engineering"),
            ("GraphQL", "Engineering"), ("Docker", "DevOps"),
        ]
        for name, category in skills_data:
            db.add(Skill(name=name, category=category))
        db.commit()

    # ── Seed 6 Demo Recruiters (one per company) ─────────────────────────
    # Each gets a login + full RecruiterProfile. All internships are linked
    # to the matching recruiter so every posting has a valid owner.
    recruiters_data = [
        {
            "email": "recruiter@stripe.com", "password": "recruiter123",
            "full_name": "Sarah Jenkins", "company_name": "Stripe",
            "company_logo": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?auto=format&fit=crop&w=120&q=80",
            "designation": "Lead Technical Recruiter", "phone": "+1 (415) 555-0192",
            "company_website": "https://stripe.com/careers", "company_size": "5001–10,000 employees",
            "industry": "FinTech / Payments",
            "bio": "Head of university recruiting at Stripe. Passionate about finding exceptional engineering talent and helping students launch their careers.",
            "linkedin_url": "https://linkedin.com/in/sarahjenkins", "location": "San Francisco, CA",
        },
        {
            "email": "recruiter@notion.com", "password": "recruiter123",
            "full_name": "David Chen", "company_name": "Notion",
            "company_logo": "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&w=120&q=80",
            "designation": "Senior University Recruiter", "phone": "+1 (415) 555-0144",
            "company_website": "https://notion.so/careers", "company_size": "501–2,000 employees",
            "industry": "Productivity Software",
            "bio": "Building the future of work at Notion. Always looking for backend and infra-minded students.",
            "linkedin_url": "https://linkedin.com/in/davidchen", "location": "New York, NY",
        },
        {
            "email": "recruiter@figma.com", "password": "recruiter123",
            "full_name": "Elena Rostova", "company_name": "Figma",
            "company_logo": "https://images.unsplash.com/photo-1620207418302-439b387441b0?auto=format&fit=crop&w=120&q=80",
            "designation": "Design Talent Acquisition Lead", "phone": "+1 (415) 555-0177",
            "company_website": "https://figma.com/careers", "company_size": "501–2,000 employees",
            "industry": "Design Tools",
            "bio": "Championing the next generation of product designers at Figma. Portfolio > words.",
            "linkedin_url": "https://linkedin.com/in/elena frostova", "location": "San Francisco, CA",
        },
        {
            "email": "recruiter@spotify.com", "password": "recruiter123",
            "full_name": "Marcus Vance", "company_name": "Spotify",
            "company_logo": "https://images.unsplash.com/photo-1614680376573-df3480f0c6ff?auto=format&fit=crop&w=120&q=80",
            "designation": "Global Student Programs Specialist", "phone": "+1 (212) 555-0123",
            "company_website": "https://spotify.com/careers", "company_size": "5001–10,000 employees",
            "industry": "Music Streaming / Audio",
            "bio": "Connecting ML-curious students with Spotify's world-class data science org.",
            "linkedin_url": "https://linkedin.com/in/marcusvance", "location": "Boston, MA",
        },
        {
            "email": "recruiter@vercel.com", "password": "recruiter123",
            "full_name": "Claire Vance", "company_name": "Vercel",
            "company_logo": "https://images.unsplash.com/photo-1559136555-9303baea8ebd?auto=format&fit=crop&w=120&q=80",
            "designation": "Engineering Director", "phone": "+1 (415) 555-0188",
            "company_website": "https://vercel.com/careers", "company_size": "201–500 employees",
            "industry": "Developer Tools / Edge Compute",
            "bio": "Shipping the modern web at Vercel. We hire strong full-stack generalists.",
            "linkedin_url": "https://linkedin.com/in/clairevance", "location": "Remote",
        },
        {
            "email": "recruiter@linear.com", "password": "recruiter123",
            "full_name": "Karla Singh", "company_name": "Linear",
            "company_logo": "https://images.unsplash.com/photo-1599305445671-ac291c95aaa9?auto=format&fit=crop&w=120&q=80",
            "designation": "Head of People", "phone": "+1 (415) 555-0155",
            "company_website": "https://linear.app/careers", "company_size": "51–200 employees",
            "industry": "Productivity / Project Tools",
            "bio": "Helping Linear build a product-driven team. PM interns welcome.",
            "linkedin_url": "https://linkedin.com/in/karlasingh", "location": "Remote",
        },
    ]

    recruiter_profiles = {}  # company_name -> RecruiterProfile
    for rd in recruiters_data:
        user = db.query(User).filter(User.email == rd["email"]).first()
        if not user:
            user = User(
                email=rd["email"], password_hash=get_password_hash(rd["password"]),
                role="recruiter", is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            profile = RecruiterProfile(
                user_id=user.id, full_name=rd["full_name"], company_name=rd["company_name"],
                company_logo=rd["company_logo"], designation=rd["designation"], phone=rd["phone"],
                company_website=rd["company_website"], company_size=rd["company_size"],
                industry=rd["industry"], bio=rd["bio"], linkedin_url=rd["linkedin_url"],
                location=rd["location"],
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)

            db.add(Notification(
                user_id=user.id, title="Welcome to HireHub Recruiter! 🎉",
                message=f"Your recruiter account for {rd['company_name']} is ready. Start posting internship positions to attract top talent.",
                type="info"))
            db.commit()
        else:
            profile = db.query(RecruiterProfile).filter(RecruiterProfile.user_id == user.id).first()

        if profile:
            recruiter_profiles[rd["company_name"]] = profile

    # ── Seed Demo Student ────────────────────────────────────────────────
    demo_user = db.query(User).filter(User.email == "student@demo.com").first()
    if not demo_user:
        demo_user = User(
            email="student@demo.com", password_hash=get_password_hash("password123"),
            role="student", is_active=True,
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

        student_profile = Student(
            user_id=demo_user.id, full_name="Alex Morgan",
            phone="+1 (555) 234-5678",
            avatar_url=pick_avatar("female", demo_user.id),
            gender="female",
            university="Stanford University", degree="Bachelor of Science",
            field_of_study="Computer Science & AI", graduation_year=2026, cgpa=3.85,
            bio="Passionate Full-Stack Developer & AI Enthusiast seeking summer 2026 engineering internships.",
            location="San Francisco, CA", preferred_mode="Remote",
            expected_stipend="₹35,000 / month", portfolio_url="https://alexmorgan.dev",
            github_url="https://github.com/alexmorgan", linkedin_url="https://linkedin.com/in/alexmorgan",
        )
        db.add(student_profile)
        db.commit()
        db.refresh(student_profile)

        for skill_name, level in [("React.js", "Advanced"), ("TypeScript", "Intermediate"),
                                   ("Python", "Advanced"), ("Figma", "Intermediate")]:
            skill = db.query(Skill).filter(Skill.name == skill_name).first()
            if skill:
                db.add(StudentSkill(student_id=student_profile.id, skill_id=skill.id, proficiency_level=level))
        db.commit()

        db.add_all([
            Notification(user_id=demo_user.id, title="Welcome to HireHub! 🎉",
                         message="Your student profile is ready. Explore top internship opportunities.",
                         type="info"),
            Notification(user_id=demo_user.id, title="Application Status Updated 🚀",
                         message="Stripe shortlisted your application for Frontend Engineering Intern!",
                         type="application"),
            Notification(user_id=demo_user.id, title="Interview Scheduled 📅",
                         message="Your interview with Sarah Jenkins at Stripe is scheduled for next Monday.",
                         type="info"),
        ])
        db.commit()

    # ── Seed Internships (each linked to its company's recruiter) ────────
    if db.query(Internship).count() == 0:
        # Translate a demo company name into its recruiter profile foreign key.
        def rid(company):
            p = recruiter_profiles.get(company)
            return p.id if p else None

        internships_data = [
            {
                "recruiter_id": rid("Stripe"),
                "title": "Frontend Software Engineering Intern",
                "company_name": "Stripe", "location": "San Francisco, CA", "mode": "Remote",
                "stipend_amount": 45000, "duration": "3 Months",
                "description": "Join Stripe's core Dashboard team to build modern payment interfaces using React, TypeScript, and Tailwind CSS.",
                "eligibility": "Currently enrolled in BS/MS in Computer Science or related engineering field graduating in 2026/2027.",
                "responsibilities": "• Implement responsive frontend components\n• Optimize performance and accessibility\n• Write robust unit and e2e tests\n• Collaborate with UX designers",
                "benefits": "• ₹45,000/month stipend\n• Mentorship with Staff Engineers\n• Equipment setup stipend ($1,500)\n• Fast-track to full-time offer",
                "recruiter_name": "Sarah Jenkins", "recruiter_email": "sarah.jenkins@stripe.com",
                "recruiter_title": "Lead Technical Recruiter",
                "skills_required": "React.js, TypeScript, Tailwind CSS, REST APIs",
                "is_external": False, "is_active": True,
                "deadline": datetime.utcnow() + timedelta(days=25),
            },
            {
                "recruiter_id": rid("Notion"),
                "title": "Backend Systems & FastAPI Intern",
                "company_name": "Notion", "location": "New York, NY", "mode": "Hybrid",
                "stipend_amount": 40000, "duration": "6 Months",
                "description": "Work on high-concurrency API infrastructure powering collaboration for millions of global users.",
                "eligibility": "Strong proficiency in Python, SQL, and API development.",
                "responsibilities": "• Architect RESTful API endpoints\n• Design database schemas\n• Implement JWT authentication\n• Monitor server performance",
                "benefits": "• Flexible hybrid schedule\n• Health insurance\n• Daily gourmet lunches\n• PPO opportunities",
                "recruiter_name": "David Chen", "recruiter_email": "dchen@notion.so",
                "recruiter_title": "Senior University Recruiter",
                "skills_required": "Python, FastAPI, SQL & MySQL, Docker",
                "is_external": False, "is_active": True,
                "deadline": datetime.utcnow() + timedelta(days=18),
            },
            {
                "recruiter_id": rid("Figma"),
                "title": "UI/UX Product Design Intern",
                "company_name": "Figma", "location": "Remote", "mode": "Remote",
                "stipend_amount": 38000, "duration": "4 Months",
                "description": "Craft intuitive visual experiences, design tokens, and high-fidelity mockups for next-generation creative tools.",
                "eligibility": "Portfolio showing UI/UX design process and Figma expertise.",
                "responsibilities": "• Conduct user research\n• Design component libraries\n• Collaborate with frontend developers\n• Design sprints",
                "benefits": "• Remote flexible environment\n• Figma Pro access\n• Design masterclass access",
                "recruiter_name": "Elena Rostova", "recruiter_email": "elena@figma.com",
                "recruiter_title": "Design Talent Acquisition Lead",
                "skills_required": "Figma, UI/UX Design, Tailwind CSS",
                "is_external": True, "external_link": "https://figma.com/careers/internships",
                "is_active": True, "deadline": datetime.utcnow() + timedelta(days=30),
            },
            {
                "recruiter_id": rid("Spotify"),
                "title": "Data Science & ML Intern",
                "company_name": "Spotify", "location": "Boston, MA", "mode": "In-Office",
                "stipend_amount": 42000, "duration": "3 Months",
                "description": "Develop recommendation algorithms personalizing music for over 500 million active listeners worldwide.",
                "eligibility": "Enrolled in CS, Statistics, Data Science, or Mathematics.",
                "responsibilities": "• Build ML recommendation models\n• Analyze user interaction data\n• Conduct A/B tests\n• Present insights to product leads",
                "benefits": "• Free Spotify Premium lifetime\n• Relocation stipend\n• Hackathon events",
                "recruiter_name": "Marcus Vance", "recruiter_email": "marcus.v@spotify.com",
                "recruiter_title": "Global Student Programs Specialist",
                "skills_required": "Python, Data Analysis, Machine Learning, SQL & MySQL",
                "is_external": False, "is_active": True,
                "deadline": datetime.utcnow() + timedelta(days=14),
            },
            {
                "recruiter_id": rid("Vercel"),
                "title": "Full-Stack Web Development Intern",
                "company_name": "Vercel", "location": "Remote", "mode": "Remote",
                "stipend_amount": 50000, "duration": "6 Months",
                "description": "Build edge computing dashboards and serverless runtime integrations powering the modern web.",
                "eligibility": "Proficient in TypeScript, React.js, Next.js, and REST APIs.",
                "responsibilities": "• Implement performant developer dashboard features\n• Build CI/CD integrations\n• Address community issues",
                "benefits": "• Top stipend (₹50,000/month)\n• M3 Max MacBook Pro provided\n• Open-source mentorship",
                "recruiter_name": "Claire Vance", "recruiter_email": "claire@vercel.com",
                "recruiter_title": "Engineering Director",
                "skills_required": "React.js, TypeScript, Node.js, Next.js",
                "is_external": False, "is_active": True,
                "deadline": datetime.utcnow() + timedelta(days=22),
            },
            {
                "recruiter_id": rid("Linear"),
                "title": "Product Management Intern",
                "company_name": "Linear", "location": "Remote", "mode": "Remote",
                "stipend_amount": 35000, "duration": "3 Months",
                "description": "Work alongside the product team to define roadmaps, conduct user research, and shape the future of developer productivity tools.",
                "eligibility": "Interested in product strategy, user research, and data-driven decision making.",
                "responsibilities": "• Define product requirements\n• Conduct user interviews\n• Analyze usage metrics\n• Write product specs",
                "benefits": "• Remote-first culture\n• Product masterclass sessions\n• Direct CEO access",
                "recruiter_name": "Karla Singh", "recruiter_email": "karla@linear.app",
                "recruiter_title": "Head of People",
                "skills_required": "Product Management, Data Analysis, Figma",
                "is_external": False, "is_active": True,
                "deadline": datetime.utcnow() + timedelta(days=35),
            },
        ]
        for data in internships_data:
            db.add(Internship(**data))
        db.commit()

        # Seed sample application + interview for demo student
        student = db.query(Student).filter(Student.user_id == demo_user.id).first()
        stripe_job = db.query(Internship).filter(Internship.company_name == "Stripe").first()
        notion_job = db.query(Internship).filter(Internship.company_name == "Notion").first()
        stripe_recruiter = recruiter_profiles.get("Stripe")

        if student and stripe_job:
            app = Application(
                student_id=student.id, internship_id=stripe_job.id,
                status="Shortlisted",
                cover_letter="I am thrilled to apply for this role at Stripe!",
                resume_url="https://alexmorgan.dev/resume.pdf",
            )
            db.add(app)
            db.commit()
            db.refresh(app)

            if stripe_recruiter:
                db.add(Interview(
                    recruiter_id=stripe_recruiter.id, application_id=app.id,
                    internship_id=stripe_job.id,
                    scheduled_at=datetime.utcnow() + timedelta(days=3, hours=10),
                    duration_minutes=45, interview_type="Video Call",
                    meeting_link="https://meet.google.com/abc-defg-hij",
                    notes="Technical round — React & TypeScript fundamentals, system design basics.",
                    status="Scheduled",
                ))
                db.commit()

        if student and notion_job:
            db.add(SavedInternship(student_id=student.id, internship_id=notion_job.id))
            db.commit()

        # Seed a short demo chat between the demo student and the Stripe
        # recruiter so the Messages section has content on first login.
        if student and stripe_recruiter and stripe_job:
            recruiter_user = db.query(User).filter(User.id == stripe_recruiter.user_id).first()
            if recruiter_user and db.query(Message).count() == 0:
                base = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
                db.add_all([
                    Message(sender_id=recruiter_user.id, receiver_id=demo_user.id,
                            content=f"Hi Alex! Thanks for applying to the {stripe_job.title} role — your background caught our eye. 🎉",
                            is_read=True, sent_at=base - timedelta(days=1)),
                    Message(sender_id=demo_user.id, receiver_id=recruiter_user.id,
                            content="Thank you, Sarah! I'm really excited about the opportunity. Happy to walk through my React projects anytime.",
                            is_read=True, sent_at=base - timedelta(days=1, minutes=-5)),
                    Message(sender_id=recruiter_user.id, receiver_id=demo_user.id,
                            content="Great! Your technical interview is coming up — let me know if you have any questions before then.",
                            is_read=False, sent_at=base - timedelta(hours=2)),
                ])
                db.commit()
