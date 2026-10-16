# Account registration, login and current-user lookup. A successful login
# returns a JWT; protected endpoints use get_current_user to decode it and load
# the account from MySQL. Student and recruiter details live in separate profiles.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Student, RecruiterProfile, Skill, StudentSkill
from app.schemas.schemas import UserRegisterRequest, UserLoginRequest, ForgotPasswordRequest, TokenResponse
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from fastapi.security import OAuth2PasswordBearer
from app.core.avatars import pick_avatar

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
# A second scheme that does NOT error on a missing token, so public endpoints
# (e.g. browsing internships) can optionally enrich results for logged-in users.
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


# Dependency shared by protected routes: decode the bearer token, load its
# user, and reject missing or deactivated accounts before running the endpoint.
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials",
                            headers={"WWW-Authenticate": "Bearer"})
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        # Admins can deactivate accounts mid-session; existing tokens die too.
        raise HTTPException(status_code=403, detail="This account has been deactivated.")
    return user


# Reject duplicate email addresses and admin self-registration, create the
# account, then create its role-specific profile and optional student skills.
# The returned token signs the user in immediately after registration.
@router.post("/register", response_model=TokenResponse)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    if payload.role == "admin":
        raise HTTPException(status_code=403, detail="Administrator accounts cannot be self-registered.")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Account with this email already exists")

    new_user = User(email=payload.email,
                    password_hash=get_password_hash(payload.password),
                    role=payload.role or "student", is_active=True)
    # Registration is split across several commits below: account, profile and
    # skills are not created as one all-or-nothing transaction.
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if new_user.role == "recruiter":
        profile = RecruiterProfile(
            user_id=new_user.id, full_name=payload.full_name,
            company_name=payload.company_name or "My Company",
            designation=payload.designation, phone=payload.phone,
            company_size=payload.company_size, industry=payload.industry,
            company_website=payload.company_website
        )
        db.add(profile)
        db.commit()
    else:
        student = Student(
            user_id=new_user.id, full_name=payload.full_name,
            phone=payload.phone, university=payload.university,
            degree=payload.degree, field_of_study=payload.field_of_study,
            graduation_year=payload.graduation_year, preferred_mode=payload.preferred_mode,
            expected_stipend=payload.expected_stipend, portfolio_url=payload.portfolio_url,
            github_url=payload.github_url, linkedin_url=payload.linkedin_url,
            gender=payload.gender,
            avatar_url=pick_avatar(payload.gender, new_user.id),
        )
        db.add(student)
        db.commit()
        db.refresh(student)

        for skill_name in (payload.skills or []):
            skill = db.query(Skill).filter(Skill.name == skill_name).first()
            if not skill:
                skill = Skill(name=skill_name, category="General")
                db.add(skill)
                db.commit()
                db.refresh(skill)
            db.add(StudentSkill(student_id=student.id, skill_id=skill.id, proficiency_level="Intermediate"))
        db.commit()

    token = create_access_token({"sub": str(new_user.id), "email": new_user.email, "role": new_user.role})
    avatar = None
    gender = None
    if new_user.role != "recruiter":
        sp = db.query(Student).filter(Student.user_id == new_user.id).first()
        if sp:
            avatar = sp.avatar_url
            gender = sp.gender
    return TokenResponse(access_token=token, token_type="bearer",
                         user_id=new_user.id, email=new_user.email,
                         full_name=payload.full_name, role=new_user.role,
                         avatar_url=avatar, gender=gender)


# Check the password and active flag, load the display name for the role,
# and return the signed token plus the identity displayed by the interface.
@router.post("/login", response_model=TokenResponse)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if user.role == "admin":
        raise HTTPException(status_code=403, detail="Administrators must sign in from the admin portal.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been deactivated by an administrator.")

    full_name = user.email.split("@")[0].title()
    avatar = None
    gender = None
    if user.role == "recruiter":
        rp = db.query(RecruiterProfile).filter(RecruiterProfile.user_id == user.id).first()
        if rp:
            full_name = rp.full_name
            avatar = rp.company_logo
    else:
        sp = db.query(Student).filter(Student.user_id == user.id).first()
        if sp:
            full_name = sp.full_name
            avatar = sp.avatar_url
            gender = sp.gender

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    return TokenResponse(access_token=token, token_type="bearer",
                         user_id=user.id, email=user.email,
                         full_name=full_name, role=user.role,
                         avatar_url=avatar, gender=gender)


# Currently checks whether the email exists and returns a confirmation.
# There is no reset-token creation or email delivery in this endpoint.
@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email address not found")
    return {"message": "Password reset instructions sent to your email."}


# Return account identity with the associated profile ID and avatar.
# Account IDs and student/recruiter profile IDs refer to different tables.
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    full_name = current_user.email
    extra_id = None
    avatar_url = None
    gender = None
    if current_user.role == "recruiter":
        rp = db.query(RecruiterProfile).filter(RecruiterProfile.user_id == current_user.id).first()
        if rp:
            full_name = rp.full_name
            extra_id = rp.id
            avatar_url = rp.company_logo
    else:
        sp = db.query(Student).filter(Student.user_id == current_user.id).first()
        if sp:
            full_name = sp.full_name
            extra_id = sp.id
            avatar_url = sp.avatar_url
            gender = sp.gender
    return {"id": current_user.id, "email": current_user.email,
            "role": current_user.role, "profile_id": extra_id, "full_name": full_name,
            "avatar_url": avatar_url, "gender": gender}
