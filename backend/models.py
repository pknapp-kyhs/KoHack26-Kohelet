import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from .database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    tier = Column(String, default="Easy")
    observance_level = Column(String, default="Moderate")
    join_date = Column(Date, default=date.today)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    streak_start_date = Column(Date, nullable=True)
    xp_current = Column(Integer, default=0)
    xp_total = Column(Integer, default=0)
    level = Column(Integer, default=1)
    preferences = Column(Text, default='{"notifications": true, "reminders": true, "public_profile": false}')

    checklist_items = relationship("ChecklistItem", back_populates="user", cascade="all, delete")
    friends = relationship("Friend", back_populates="user", cascade="all, delete")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete")
    rewards = relationship("UserReward", back_populates="user", cascade="all, delete")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    category = Column(String, default="General")
    tier = Column(String, default="Easy")
    estimated_time = Column(Integer, default=5)
    bracha_text = Column(Text, default="")
    instructions = Column(Text, default="")


class ChecklistItem(Base):
    __tablename__ = "checklist_items"
    id = Column(String, primary_key=True, default=gen_uuid)
    date = Column(Date, nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="checklist_items")
    task = relationship("Task")


class Friend(Base):
    __tablename__ = "friends"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    friend_id = Column(String, nullable=False)

    user = relationship("User", back_populates="friends")


class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=gen_uuid)
    from_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    to_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, default="encouragement")
    created_at = Column(DateTime, default=datetime.utcnow)


class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    xp_reward = Column(Integer, default=0)
    icon = Column(String, default="")
    criteria = Column(String, default="")


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(String, ForeignKey("achievements.id"), nullable=False)
    earned_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")


class Reward(Base):
    __tablename__ = "rewards"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    xp_cost = Column(Integer, default=0)
    is_unlocked = Column(Boolean, default=False)


class UserReward(Base):
    __tablename__ = "user_rewards"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    reward_id = Column(String, ForeignKey("rewards.id"), nullable=False)
    redeemed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="rewards")
    reward = relationship("Reward")
