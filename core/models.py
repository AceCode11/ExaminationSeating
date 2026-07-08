from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from datetime import datetime
from typing import Optional, List

class Base(DeclarativeBase):
    pass

class ExamSession(Base):
    __tablename__ = 'exam_sessions'
    id: Mapped[int] = mapped_column(primary_key=True)
    college_name: Mapped[str] = mapped_column(String(500), default='')
    program_name: Mapped[str] = mapped_column(String(200), default='')
    exam_name: Mapped[str] = mapped_column(String(200), default='EXTERNAL')
    division: Mapped[str] = mapped_column(String(10), default='A')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    # relationships
    students: Mapped[List['Student']] = relationship(back_populates='session', cascade='all, delete-orphan')
    timetable_entries: Mapped[List['TimetableEntry']] = relationship(back_populates='session', cascade='all, delete-orphan')
    rooms: Mapped[List['Room']] = relationship(back_populates='session', cascade='all, delete-orphan')
    nor_records: Mapped[List['NORRecord']] = relationship(back_populates='session', cascade='all, delete-orphan')

class Student(Base):
    __tablename__ = 'students'
    id: Mapped[int] = mapped_column(primary_key=True)
    roll_number: Mapped[str] = mapped_column(String(50), index=True)
    student_name: Mapped[str] = mapped_column(String(300))
    session_id: Mapped[int] = mapped_column(ForeignKey('exam_sessions.id'))
    session: Mapped['ExamSession'] = relationship(back_populates='students')
    allocations: Mapped[List['Allocation']] = relationship(back_populates='student', cascade='all, delete-orphan')

class Room(Base):
    __tablename__ = 'rooms'
    id: Mapped[int] = mapped_column(primary_key=True)
    room_number: Mapped[str] = mapped_column(String(50))
    capacity: Mapped[int] = mapped_column(Integer)
    session_id: Mapped[int] = mapped_column(ForeignKey('exam_sessions.id'))
    session: Mapped['ExamSession'] = relationship(back_populates='rooms')
    allocations: Mapped[List['Allocation']] = relationship(back_populates='room', cascade='all, delete-orphan')

class TimetableEntry(Base):
    __tablename__ = 'timetable_entries'
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str] = mapped_column(String(50))
    time: Mapped[str] = mapped_column(String(50))
    subject_code: Mapped[str] = mapped_column(String(100))
    subject_name: Mapped[str] = mapped_column(String(300))
    session_id: Mapped[int] = mapped_column(ForeignKey('exam_sessions.id'))
    session: Mapped['ExamSession'] = relationship(back_populates='timetable_entries')

class Allocation(Base):
    __tablename__ = 'allocations'
    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id'))
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'))
    room: Mapped['Room'] = relationship(back_populates='allocations')
    student: Mapped['Student'] = relationship(back_populates='allocations')

class NORRecord(Base):
    __tablename__ = 'nor_records'
    id: Mapped[int] = mapped_column(primary_key=True)
    roll_number: Mapped[str] = mapped_column(String(50))
    session_id: Mapped[int] = mapped_column(ForeignKey('exam_sessions.id'))
    session: Mapped['ExamSession'] = relationship(back_populates='nor_records')

class AppSetting(Base):
    __tablename__ = 'app_settings'
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
