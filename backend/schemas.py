from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


class UserBase(BaseModel):
    name: str
    email: EmailStr
    tier: Optional[str] = "Easy"
    observance_level: Optional[str] = "Moderate"


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    id: str
    name: str
    email: EmailStr
    tier: str
    observance_level: str
    join_date: date
    current_streak: int
    longest_streak: int
    streak_start_date: Optional[date]
    xp_current: int
    xp_total: int
    level: int
    preferences: Dict[str, Any]

    class Config:
        orm_mode = True


class TierUpdate(BaseModel):
    tier: str


class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    tier: Optional[str] = "Easy"
    estimated_time: Optional[int] = 5
    bracha_text: Optional[str] = None
    instructions: Optional[str] = None


class Task(TaskBase):
    id: str
    class Config:
        orm_mode = True


class ChecklistItemCreate(BaseModel):
    task_id: str
    completed: bool
    completed_at: Optional[datetime] = None


class ChecklistItemResponse(BaseModel):
    task_id: str
    completed: bool
    completed_at: Optional[datetime]

    class Config:
        orm_mode = True


class ChecklistResponse(BaseModel):
    date: date
    user_id: str
    tasks: List[ChecklistItemResponse]
    progress_percentage: float


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    streak_start_date: Optional[date]
    milestones: List[str]


class StreakHistoryItem(BaseModel):
    date: date
    completed: bool
    streak_day: int


class FriendResponse(BaseModel):
    friend_id: str


class MessageSend(BaseModel):
    from_user_id: str
    to_user_id: str
    message: str
    type: str = "encouragement"


class AchievementResponse(BaseModel):
    id: str
    name: str
    description: str
    earned_date: Optional[datetime]
    icon: Optional[str]

    class Config:
        orm_mode = True


class RewardResponse(BaseModel):
    id: str
    name: str
    description: str
    xp_cost: int
    is_unlocked: bool

    class Config:
        orm_mode = True


class XPAdd(BaseModel):
    points: int
    source: str
    metadata: Optional[Dict[str, Any]] = None


class XPResponse(BaseModel):
    xp_current: int
    xp_to_next_level: int
    level: int
    total_xp: int


class CalendarHoliday(BaseModel):
    date: date
    name: str
    description: Optional[str]


class ZmanimResponse(BaseModel):
    shacharis: str
    mincha: str
    maariv: str
    candle_lighting: str


class OmerResponse(BaseModel):
    day: int
    week: int
    total_days: int
    bracha: str
