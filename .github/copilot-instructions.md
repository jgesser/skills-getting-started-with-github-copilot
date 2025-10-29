# Copilot Instructions for Mergington High School Activities API

## Project Overview
This is a **FastAPI-based web application** for managing high school extracurricular activities. The architecture combines a Python backend (`src/app.py`) with a vanilla JavaScript frontend (`src/static/`). Data is stored **in-memory only** - all state resets on server restart.

## Key Architecture Patterns

### Backend Structure (`src/app.py`)
- **Single-file FastAPI app** with embedded data - no external database
- **Activity data model**: Uses activity names as keys, stores participant emails in arrays
- **Static file serving**: `/static` route serves the frontend from `src/static/`
- **Root redirect**: `/` automatically redirects to `/static/index.html`

```python
# Core data structure pattern used throughout
activities = {
    "Activity Name": {
        "description": "...",
        "schedule": "...", 
        "max_participants": int,
        "participants": ["email1@mergington.edu", "email2@mergington.edu"]
    }
}
```

### Frontend Structure (`src/static/`)
- **Vanilla JavaScript** (no frameworks) with async/await API calls
- **Two-column layout**: Activities list + signup form
- **Dynamic content**: Activities loaded from `/activities` endpoint, form populated dynamically
- **Error handling**: User-friendly messages with auto-hide after 5 seconds

## Development Workflow

### Running the Application
- **Primary method**: Use VS Code debugger with "Launch Mergington WebApp" configuration
- **Alternative**: `uvicorn src.app:app --reload` from project root
- **Not**: `python app.py` (no `__main__` block exists)

### Testing Setup
- **Test framework**: pytest (configured in `pytest.ini`)
- **Current state**: No test files exist yet - tests should be created in root or `tests/` directory
- **Python path**: Configured to include current directory

### API Endpoints
- `GET /activities` - Returns complete activities dict with participant lists
- `POST /activities/{activity_name}/signup?email=<email>` - Adds email to participants array
- **No authentication** - simple email validation only
- **Error cases**: Activity not found (404), already signed up (400)

## Project-Specific Conventions

### Email Format
All student emails follow pattern: `name@mergington.edu`

### Activity Naming
Activity names are used as **direct dictionary keys** - avoid special characters that would require URL encoding

### Frontend State Management
- No state persistence - page refreshes reload from API
- Form resets after successful signup
- Participant lists displayed in real-time after each load

### File Organization
```
src/
├── app.py              # Complete backend logic
├── static/
│   ├── index.html      # Main UI structure  
│   ├── app.js          # API interactions & DOM manipulation
│   └── styles.css      # Responsive design with flexbox
└── README.md           # API documentation
```

## Common Modifications

### Adding New Activities
Add directly to the `activities` dict in `app.py` - follows existing structure pattern

### UI Changes
- Modify `src/static/index.html` for structure
- Update `src/static/app.js` for behavior  
- Style changes in `src/static/styles.css` (uses flexbox, mobile-responsive)

### API Extensions
Extend FastAPI app in `app.py` - consider participant capacity limits and email validation patterns

## Dependencies
- **Runtime**: `fastapi`, `uvicorn` (see `requirements.txt`)
- **Development**: VS Code debugger configuration already set up
- **No external services** - completely self-contained application