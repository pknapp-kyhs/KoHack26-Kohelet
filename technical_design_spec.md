# 2Jew List - Technical Design Specification

## Overview

2Jew List is a gamified Jewish mitzvah tracking web application that helps users build consistency in their spiritual practices through structured checklists, streak tracking, and community engagement. The application features a tiered system (Easy/Medium/Advanced) with personalized daily tasks, Jewish calendar integration, and social accountability features.

### Architecture
- **Backend**: Python-based API server with data persistence
- **Frontend**: Web application (designed by separate team)
- **Data Storage**: JSON-based file system with potential for database migration
- **External APIs**: Jewish calendar and zmanim (prayer times) integration

## Backend API Specification

### Base URL
```
https://api.2jewlist.com/v1
```

### Authentication
- JWT-based authentication for user sessions
- API key required for external integrations

### Core Endpoints

#### User Management
```
POST /users/register
- Register new user with tier selection
- Body: {name, email, password, tier, observance_level}

POST /users/login
- User authentication
- Body: {email, password}
- Returns: JWT token

GET /users/{user_id}
- Get user profile and current streak
- Headers: Authorization: Bearer {token}

PUT /users/{user_id}/tier
- Update user tier (Easy/Medium/Advanced)
- Body: {tier}
```

#### Daily Checklist
```
GET /users/{user_id}/checklist/{date}
- Get daily checklist for specific date
- Returns: Array of tasks with completion status

POST /users/{user_id}/checklist/{date}/complete
- Mark task as completed
- Body: {task_id, completed_at}

GET /users/{user_id}/checklist/progress
- Get current day's progress percentage
- Returns: {completed_tasks, total_tasks, percentage}
```

#### Streak System
```
GET /users/{user_id}/streak
- Get current streak information
- Returns: {current_streak, longest_streak, streak_start_date, milestones}

GET /users/{user_id}/streak/history
- Get streak history for calendar visualization
- Returns: Array of {date, completed, streak_day}
```

#### Jewish Calendar
```
GET /calendar/holidays/{year}
- Get Jewish holidays for year
- Returns: Array of {date, name, description}

GET /calendar/zmanim
- Get prayer times for location and date
- Query params: lat, lng, date
- Returns: {shacharis, mincha, maariv, candle_lighting}

GET /calendar/omer/{date}
- Get Omer count for date
- Returns: {day, week, total_days, bracha}
```

#### Social Features
```
GET /users/{user_id}/friends
- Get user's friends list
- Returns: Array of friend objects

POST /users/{user_id}/friends/{friend_id}
- Add friend
- Returns: success status

GET /leaderboard/friends/{user_id}
- Get friends leaderboard by streak
- Returns: Sorted array of users

POST /messages/send
- Send encouragement message
- Body: {from_user_id, to_user_id, message, type: 'encouragement'}
```

#### Achievements & Rewards
```
GET /users/{user_id}/achievements
- Get user's earned achievements
- Returns: Array of {id, name, description, earned_date, icon}

GET /achievements/available
- Get all available achievements
- Returns: Array of achievement definitions
```

## Frontend Design Specification

### Core Pages & Components

#### 1. Authentication Pages
- **Login/Register Form**
  - Email/password fields with validation
  - Tier selection dropdown (Easy/Medium/Advanced)
  - "Forgot Password" link
  - Social login options (optional)

#### 2. Dashboard (Main Landing Page)
- **Header**: User avatar, name, current streak counter, tier badge
- **Today's Progress**: Circular progress indicator (0-100%)
- **Quick Actions**: Mark today's tasks complete button
- **Streak Visualization**: Flame icon with streak number, calendar heatmap
- **Upcoming Tasks**: Preview of next 3 tasks
- **Motivational Quote**: Daily Jewish wisdom/inspiration

#### 3. Daily Checklist Page
- **Task List**: Interactive checklist with checkboxes
  - Task name, description, category icon
  - Completion status with timestamps
  - Progress bar at top
- **Task Details**: Expandable sections for each task
  - Instructions, bracha text, time requirements
- **Completion Animation**: Confetti/fireworks when all tasks done
- **Streak Impact**: Show how completion affects streak

#### 4. Calendar View
- **Monthly Calendar**: Highlight completed days, holidays, Omer
- **Day Details**: Click day to see tasks completed
- **Jewish Calendar Integration**:
  - Holiday indicators with names
  - Omer counter with bracha
  - Shabbos/parsha information
- **Streak Visualization**: Color-coded streak days

#### 5. Profile & Settings
- **User Profile**: Avatar, bio, Jewish identity info
- **Tier Management**: Current tier, upgrade/downgrade options
- **Statistics**: Total tasks completed, longest streak, join date
- **Achievements Gallery**: Unlocked badges with descriptions
- **Settings**: Notification preferences, privacy settings

#### 6. Social Features
- **Friends List**: Search/add friends by username
- **Friends Feed**: See friends' recent achievements/streaks
- **Leaderboards**:
  - Friends leaderboard (sortable by streak)
  - Global leaderboard (top 100)
- **Messages**: Send/receive encouragement messages
- **Group Challenges**: Create/join weekly challenges

#### 7. Achievement System
- **Achievement Modal**: Pop-up when earning new badge
- **Achievement Gallery**: Grid of earned/unearned achievements
- **Progress Tracking**: Show progress toward next achievement

### UI/UX Design Principles

#### Visual Design
- **Color Scheme**: Blue tones for trust/spirituality, gold for achievements
- **Typography**: Clean, readable fonts with Hebrew support
- **Icons**: Consistent iconography for tasks, achievements, calendar
- **Responsive**: Mobile-first design, tablet/desktop optimized

#### Interaction Design
- **Progressive Disclosure**: Show essential info first, details on demand
- **Gamification Elements**: Progress bars, streak counters, achievement unlocks
- **Feedback Systems**: Toast notifications, loading states, error handling
- **Accessibility**: Screen reader support, keyboard navigation, high contrast

#### Jewish-Specific UX
- **Hebrew Text Support**: Proper RTL layout, font rendering
- **Cultural Sensitivity**: Appropriate imagery, respectful content
- **Calendar Integration**: Intuitive Jewish date display alongside Gregorian
- **Spiritual Context**: Include brachos, explanations, learning opportunities

## Data Models

### User Model
```json
{
  "id": "uuid",
  "name": "string",
  "email": "string",
  "tier": "Easy|Medium|Advanced",
  "streak": {
    "current": 0,
    "longest": 0,
    "start_date": "2024-01-01"
  },
  "join_date": "2024-01-01",
  "achievements": ["achievement_id"],
  "preferences": {
    "notifications": true,
    "reminders": true,
    "public_profile": false
  }
}
```

### Task Model
```json
{
  "id": "uuid",
  "name": "Modeh Ani",
  "description": "Morning blessing upon waking",
  "category": "Prayer",
  "tier": "Easy",
  "estimated_time": 2,
  "bracha_text": "Hebrew text",
  "instructions": "How to perform the mitzvah"
}
```

### Checklist Model
```json
{
  "date": "2024-01-15",
  "user_id": "uuid",
  "tasks": [
    {
      "task_id": "uuid",
      "completed": true,
      "completed_at": "2024-01-15T07:30:00Z"
    }
  ],
  "progress_percentage": 75
}
```

## Integration Points

### Real-time Updates
- WebSocket connection for live streak updates
- Push notifications for reminders and achievements
- Real-time friend activity feed

### External Integrations
- **Jewish Calendar API**: For holidays and zmanim
- **Push Notification Service**: For reminders
- **Analytics**: Track user engagement and retention

### Error Handling
- Graceful degradation when APIs are unavailable
- Offline mode for basic checklist functionality
- Clear error messages with retry options

## User Flows

### New User Onboarding
1. Register → Select tier → Complete onboarding survey
2. Receive first daily checklist
3. Tutorial walkthrough of main features
4. Connect with friends (optional)

### Daily Usage Flow
1. Open app → View dashboard with progress
2. Navigate to checklist → Complete tasks
3. Receive achievement notifications
4. View updated streak and statistics

### Social Interaction Flow
1. Add friends → View friends' progress
2. Send encouragement messages
3. Participate in group challenges
4. Compete on leaderboards

## Performance Requirements

### Response Times
- API responses: <200ms for core features
- Page loads: <2 seconds
- Real-time updates: <500ms

### Scalability
- Support 10,000+ concurrent users
- Handle peak usage during Jewish holidays
- Efficient caching for calendar data

### Security
- End-to-end encryption for sensitive data
- Rate limiting on API endpoints
- Secure JWT token management

## Testing Strategy

### Backend Testing
- Unit tests for all algorithms (streak calculation, validation)
- Integration tests for API endpoints
- Load testing for concurrent users

### Frontend Testing
- Component testing for UI elements
- E2E testing for critical user flows
- Cross-browser compatibility testing

### QA Checklist
- [ ] All API endpoints documented and tested
- [ ] Responsive design on mobile/tablet/desktop
- [ ] Hebrew text rendering correct
- [ ] Offline functionality works
- [ ] Accessibility standards met
- [ ] Performance benchmarks achieved

---

*This specification serves as the technical foundation for both backend development and frontend design. The backend team will implement the API endpoints, while the frontend team uses this spec to build the user interface and integrate with the provided APIs.*</content>
<parameter name="filePath">c:\Users\nateb\OneDrive\Desktop\code\KoHack26-Kohelet\technical_design_spec.md