from datetime import date, datetime, timedelta
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from . import models, schemas, auth, database
from .database import engine, get_db
from .auth import create_access_token, verify_password, get_password_hash, decode_access_token
import json
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="2Jew List API")
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.get("/")
def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html"))



def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> models.User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth header")
    token = authorization.split(" ", 1)[1]
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def seed_core_data(db: Session):
    if db.query(models.Task).count() == 0:
        defaults = [
            {"name":"Modeh Ani","description":"Morning blessing upon waking","category":"Prayer","tier":"Easy","estimated_time":2,"bracha_text":"Blessed are You...","instructions":"Say after waking."},
            {"name":"Shema","description":"Morning shema recitation","category":"Prayer","tier":"Easy","estimated_time":5,"bracha_text":"Hear O Israel...","instructions":"Morning and night."},
            {"name":"Charity","description":"Give tzedakah","category":"Mitzvah","tier":"Medium","estimated_time":5,"bracha_text":"Donation","instructions":"Donate any amount."},
        ]
        for t in defaults:
            task = models.Task(**t)
            db.add(task)
    if db.query(models.Achievement).count() == 0:
        a1 = models.Achievement(name="7-Day Streak Master",description="Complete full daily checklist 7 days in a row",xp_reward=200,icon="badge7.png",criteria="streak >= 7")
        a2 = models.Achievement(name="First Day",description="Complete your first day checklist",xp_reward=50,icon="badge1.png",criteria="streak >= 1")
        db.add_all([a1,a2])
    if db.query(models.Reward).count() == 0:
        r1 = models.Reward(name="Premium Theme Pack",description="Unlock special UI theme",xp_cost=1000,is_unlocked=False)
        r2 = models.Reward(name="Extra Avatar",description="Special avatar frame",xp_cost=500,is_unlocked=False)
        db.add_all([r1,r2])
    db.commit()


@app.on_event("startup")
def startup_event():
    db = next(database.get_db())
    seed_core_data(db)


@app.post("/users/register", response_model=schemas.Token)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(user_in.password)
    user = models.User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed,
        tier=user_in.tier,
        observance_level=user_in.observance_level,
        streak_start_date=date.today(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/users/login", response_model=schemas.Token)
def login_user(login: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login.email).first()
    if not user or not verify_password(login.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}


def format_user_profile(user: models.User) -> Dict[str, Any]:
    prefs = user.preferences
    if isinstance(prefs, str):
        try:
            prefs = json.loads(prefs)
        except Exception:
            prefs = {}
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "tier": user.tier,
        "observance_level": user.observance_level,
        "join_date": user.join_date,
        "current_streak": user.current_streak,
        "longest_streak": user.longest_streak,
        "streak_start_date": user.streak_start_date,
        "xp_current": user.xp_current,
        "xp_total": user.xp_total,
        "level": user.level,
        "preferences": prefs,
    }


@app.get("/users/me", response_model=schemas.UserProfile)
def get_user_me(current_user: models.User = Depends(get_current_user)):
    return format_user_profile(current_user)


@app.get("/users/{user_id}", response_model=schemas.UserProfile)
def get_user_profile(user_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return current_user


@app.put("/users/{user_id}/tier")
def update_tier(user_id: str, tier_update: schemas.TierUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    current_user.tier = tier_update.tier
    db.commit()
    return {"success": True, "tier": current_user.tier}


def find_or_create_checklist(user: models.User, target_date: date, db: Session):
    items = db.query(models.ChecklistItem).filter(models.ChecklistItem.user_id == user.id, models.ChecklistItem.date == target_date).all()
    if items:
        return items
    available_tasks = db.query(models.Task).filter(models.Task.tier.in_([user.tier, "Easy"])).all()
    created = []
    for task in available_tasks:
        item = models.ChecklistItem(user_id=user.id, task_id=task.id, date=target_date)
        db.add(item)
        created.append(item)
    db.commit()
    return created


@app.get("/users/{user_id}/checklist/{date}", response_model=schemas.ChecklistResponse)
def get_checklist(user_id: str, date: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    target_date = datetime.fromisoformat(date).date()
    items = find_or_create_checklist(current_user, target_date, db)
    total = len(items)
    completed = sum(1 for i in items if i.completed)
    percent = (completed / total * 100) if total else 0
    response_items = [schemas.ChecklistItemResponse(task_id=i.task_id, completed=i.completed, completed_at=i.completed_at) for i in items]
    return schemas.ChecklistResponse(date=target_date, user_id=user_id, tasks=response_items, progress_percentage=percent)


@app.post("/users/{user_id}/checklist/{date}/complete")
def complete_checklist(user_id: str, date: str, data: schemas.ChecklistItemCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    target_date = datetime.fromisoformat(date).date()
    item = db.query(models.ChecklistItem).filter(models.ChecklistItem.user_id == user_id, models.ChecklistItem.date == target_date, models.ChecklistItem.task_id == data.task_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist task not found")
    item.completed = data.completed
    item.completed_at = data.completed_at or datetime.utcnow()
    db.commit()
    update_streak(current_user, target_date, db)
    return {"success": True}


def update_streak(user: models.User, target_date: date, db: Session):
    day_items = db.query(models.ChecklistItem).filter(models.ChecklistItem.user_id == user.id, models.ChecklistItem.date == target_date).all()
    if not day_items or not all(i.completed for i in day_items):
        return
    yesterday = target_date - timedelta(days=1)
    prev_day = db.query(models.ChecklistItem).filter(models.ChecklistItem.user_id == user.id, models.ChecklistItem.date == yesterday).all()
    prev_complete = bool(prev_day and all(i.completed for i in prev_day))
    if prev_complete:
        user.current_streak += 1
    else:
        user.current_streak = 1
        user.streak_start_date = target_date
    if user.current_streak > user.longest_streak:
        user.longest_streak = user.current_streak
    db.commit()


@app.get("/users/{user_id}/checklist/progress")
def get_checklist_progress(user_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    today = date.today()
    items = db.query(models.ChecklistItem).filter(models.ChecklistItem.user_id == user_id, models.ChecklistItem.date == today).all()
    if not items:
        items = find_or_create_checklist(current_user, today, db)
    total = len(items)
    completed = sum(i.completed for i in items)
    return {"completed_tasks": completed, "total_tasks": total, "percentage": (completed / total * 100) if total else 0}


@app.get("/users/{user_id}/streak", response_model=schemas.StreakResponse)
def streak_info(user_id: str, current_user: models.User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    landmarks = []
    if current_user.current_streak >= 7:
        landmarks.append("7-day streak")
    if current_user.current_streak >= 30:
        landmarks.append("30-day streak")
    return schemas.StreakResponse(current_streak=current_user.current_streak, longest_streak=current_user.longest_streak, streak_start_date=current_user.streak_start_date, milestones=landmarks)


@app.get("/users/{user_id}/streak/history", response_model=List[schemas.StreakHistoryItem])
def streak_history(user_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    checklists = db.query(models.ChecklistItem).filter(models.ChecklistItem.user_id == user_id).order_by(models.ChecklistItem.date).all()
    by_date = {}
    for item in checklists:
        by_date.setdefault(item.date, True)
        if not item.completed:
            by_date[item.date] = False
    streak_day = 0
    history = []
    for dt in sorted(by_date.keys()):
        completed = by_date[dt]
        if completed:
            streak_day += 1
        else:
            streak_day = 0
        history.append(schemas.StreakHistoryItem(date=dt, completed=completed, streak_day=streak_day))
    return history


@app.get("/calendar/holidays/{year}", response_model=List[schemas.CalendarHoliday])
def get_holidays(year: int):
    holidays = [
        {"date": date(year, 9, 15), "name": "Rosh Hashanah", "description": "Jewish New Year"},
        {"date": date(year, 9, 24), "name": "Yom Kippur", "description": "Day of Atonement"},
    ]
    return holidays


@app.get("/calendar/zmanim", response_model=schemas.ZmanimResponse)
def get_zmanim(lat: float, lng: float, date: str):
    _ = datetime.fromisoformat(date).date()
    return schemas.ZmanimResponse(shacharis="06:00", mincha="13:30", maariv="19:40", candle_lighting="18:00")


@app.get("/calendar/omer/{date}", response_model=schemas.OmerResponse)
def get_omer(date: str):
    target_date = datetime.fromisoformat(date).date()
    start = date.today().replace(year=target_date.year, month=3, day=16)
    if start > target_date:
        start = target_date
    omer_day = (target_date - start).days + 1
    if omer_day < 1 or omer_day > 49:
        raise HTTPException(status_code=404, detail="Date outside Omer")
    week = ((omer_day - 1) // 7) + 1
    bracha = "Baruch ata..." if 1 <= omer_day <= 49 else ""
    return schemas.OmerResponse(day=omer_day, week=week, total_days=49, bracha=bracha)


@app.get("/users/{user_id}/friends", response_model=List[schemas.FriendResponse])
def get_friends(user_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    friendships = db.query(models.Friend).filter(models.Friend.user_id == user_id).all()
    return [schemas.FriendResponse(friend_id=f.friend_id) for f in friendships]


@app.post("/users/{user_id}/friends/{friend_id}")
def add_friend(user_id: str, friend_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    if db.query(models.Friend).filter(models.Friend.user_id == user_id, models.Friend.friend_id == friend_id).first():
        return {"success": True, "message": "Already friends"}
    db.add(models.Friend(user_id=user_id, friend_id=friend_id))
    db.commit()
    return {"success": True}


@app.get("/leaderboard/friends/{user_id}")
def friends_leaderboard(user_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    friend_ids = [f.friend_id for f in db.query(models.Friend).filter(models.Friend.user_id == user_id).all()]
    users = db.query(models.User).filter(models.User.id.in_(friend_ids)).order_by(models.User.current_streak.desc()).all()
    return [{"id": u.id, "name": u.name, "current_streak": u.current_streak} for u in users]


@app.post("/messages/send")
def send_message(message: schemas.MessageSend, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.id != message.from_user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    msg = models.Message(**message.dict())
    db.add(msg)
    db.commit()
    return {"success": True}


@app.get("/users/{user_id}/achievements", response_model=List[schemas.AchievementResponse])
def user_achievements(user_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    earned = db.query(models.UserAchievement).filter(models.UserAchievement.user_id == user_id).all()
    return [schemas.AchievementResponse(id=e.achievement.id, name=e.achievement.name, description=e.achievement.description, earned_date=e.earned_date, icon=e.achievement.icon) for e in earned]


@app.get("/achievements/available", response_model=List[schemas.AchievementResponse])
def achievements_available(db: Session = Depends(get_db)):
    all_ach = db.query(models.Achievement).all()
    return [schemas.AchievementResponse(id=a.id, name=a.name, description=a.description, earned_date=None, icon=a.icon) for a in all_ach]


@app.get("/users/{user_id}/xp", response_model=schemas.XPResponse)
def get_xp(user_id: str, current_user: models.User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    next_level = (current_user.level + 1) * 1000
    return schemas.XPResponse(xp_current=current_user.xp_current, xp_to_next_level=max(next_level - current_user.xp_current, 0), level=current_user.level, total_xp=current_user.xp_total)


@app.post("/users/{user_id}/xp/add", response_model=schemas.XPResponse)
def add_xp(user_id: str, xp_add: schemas.XPAdd, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    current_user.xp_current += xp_add.points
    current_user.xp_total += xp_add.points
    leveled = False
    while current_user.xp_current >= current_user.level * 1000:
        current_user.xp_current -= current_user.level * 1000
        current_user.level += 1
        leveled = True
    db.commit()
    next_level = (current_user.level + 1) * 1000
    return schemas.XPResponse(xp_current=current_user.xp_current, xp_to_next_level=max(next_level - current_user.xp_current, 0), level=current_user.level, total_xp=current_user.xp_total)


@app.get("/users/{user_id}/rewards", response_model=List[schemas.RewardResponse])
def get_rewards(user_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    user_rewards = db.query(models.UserReward).filter(models.UserReward.user_id == user_id).all()
    reward_ids = [ur.reward_id for ur in user_rewards]
    all_rewards = db.query(models.Reward).all()
    return [schemas.RewardResponse(id=r.id, name=r.name, description=r.description, xp_cost=r.xp_cost, is_unlocked=(r.id in reward_ids)) for r in all_rewards]


@app.post("/users/{user_id}/rewards/redeem")
def redeem_reward(user_id: str, payload: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    reward_id = payload.get("reward_id")
    reward = db.query(models.Reward).filter(models.Reward.id == reward_id).first()
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    if current_user.xp_current < reward.xp_cost:
        raise HTTPException(status_code=400, detail="Not enough XP")
    if db.query(models.UserReward).filter(models.UserReward.user_id == user_id, models.UserReward.reward_id == reward_id).first():
        return {"success": False, "message": "Already redeemed"}
    current_user.xp_current -= reward.xp_cost
    db.add(models.UserReward(user_id=user_id, reward_id=reward_id))
    db.commit()
    return {"success": True, "remaining_xp": current_user.xp_current, "reward_details": {"id": reward.id, "name": reward.name, "description": reward.description}}
