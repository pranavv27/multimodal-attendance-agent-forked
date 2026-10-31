import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./classroom_agent.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, default="T101")
    session_name = Column(String, default="CS101 - Intro to AI")
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    avg_engagement = Column(Float, default=85.0)
    total_participants = Column(Integer, default=0)

    metrics = relationship("PersonMetric", back_populates="session", cascade="all, delete-orphan")
    attendance = relationship("AttendanceRecord", back_populates="session", cascade="all, delete-orphan")

class PersonMetric(Base):
    __tablename__ = "person_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), index=True)
    student_id = Column(String, index=True)
    student_name = Column(String, default="Student")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    attention_score = Column(Float, default=80.0)
    emotion = Column(String, default="attentive") # attentive, neutral, distracted, tired
    head_pose = Column(String, default="front")
    noise_level = Column(Float, default=-25.0)

    session = relationship("Session", back_populates="metrics")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), index=True)
    student_id = Column(String, index=True)
    student_name = Column(String)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    duration_seconds = Column(Float, default=0.0)
    status = Column(String, default="In Progress") # Present, In Progress, Absent

    session = relationship("Session", back_populates="attendance")

def init_db():
    Base.metadata.create_all(bind=engine)
    # Seed default sample data if table is empty
    db = SessionLocal()
    try:
        if db.query(Session).count() == 0:
            sample_session = Session(
                teacher_id="T101",
                session_name="CS101 - Interactive Machine Learning",
                start_time=datetime.utcnow(),
                avg_engagement=86.4,
                total_participants=3
            )
            db.add(sample_session)
            db.commit()
            db.refresh(sample_session)

            # Sample students
            students = [
                ("S101", "Pranav Ghodki", 88.0, 920.0, "Present")
            ]
            for s_id, s_name, att, dur, status in students:
                rec = AttendanceRecord(
                    session_id=sample_session.id,
                    student_id=s_id,
                    student_name=s_name,
                    duration_seconds=dur,
                    status=status
                )
                db.add(rec)
            db.commit()
    finally:
        db.close()
