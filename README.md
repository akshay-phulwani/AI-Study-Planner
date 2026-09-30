# 🎓 AI Study Planner

A practical GenAI web application built with **Python, Streamlit, Pydantic, SQLite, and Google Gemini API**. 

The AI Study Planner creates personalized, step-by-step learning roadmaps tailored to a user's target career goal and weekly availability. It demonstrates structured LLM generation, Pydantic schema validation, local database persistence, and deterministic task progression logic.

---

## 🌟 Key Architecture Highlights

1. **ONE Structured LLM Call**: Generates a complete hierarchical roadmap (Phases ➔ Topics ➔ Daily Tasks) in a single API call using Google Gemini API (`gemini-2.5-flash`).
2. **Pydantic Validation**: Enforces strict JSON schema validation to guarantee structured, error-free data before database ingestion.
3. **SQLite Persistence**: Stores the profile, roadmap, phases, topics, daily tasks, and completion timestamps locally.
4. **Zero Extra LLM Calls for Daily Tracking**: All task completion, dependency lock, progress calculation, and daily plan rendering are handled 100% via standard Python and SQL queries.

---

## 📁 Project Structure

```text
AI-Study-Planner/
│
├── app.py                   # Streamlit dashboard interface (4 pages)
├── requirements.txt         # Project Python dependencies
├── .env.example             # Template for API keys
├── .gitignore               # Excludes secrets & database files
├── README.md                # Project documentation & interview guide
│
├── data/
│   └── study_planner.db     # SQLite database
│
└── src/
    ├── __init__.py
    ├── models.py            # Pydantic data schemas (Roadmap, Phase, Topic, DailyTask)
    ├── llm.py               # GenAI integration (1 LLM call with Pydantic validation)
    ├── roadmap.py           # Roadmap formatting helpers
    ├── database.py          # SQLite schema initialization and CRUD queries
    └── planner.py           # Task progression & completion business logic
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10 or higher
- A free Google Gemini API key (or OpenAI API key)

### 2. Setup Environment
Clone or navigate to the project directory and install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Run the Application
Launch the Streamlit dashboard:

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 💡 How it Works (Data Flow)

```text
[User Setup Input]
       │
       ▼
[ONE LLM API Call] ──► Google Gemini API (gemini-2.5-flash) with Structured Output
       │
       ▼
[Pydantic Schema Validation] ──► Roadmap -> Phase -> Topic -> DailyTask
       │
       ▼
[SQLite Storage] ──► Saved in data/study_planner.db
       │
       ▼
[Python Task Progression Logic] ──► Handles completion order & locks incomplete tasks
       │
       ▼
[Streamlit 4-Page Interface] ──► Setup, Dashboard, Roadmap Tree, Daily Plan
```

---

## 🎙️ Internship Interview Talking Points

### 1. Why use a single LLM API call instead of calling LLMs daily?
> *"Calling an LLM daily for static progress updates adds latency, increases cost, and introduces non-deterministic outputs. By making one structured API call up front, we generate the full plan, validate it, and store it in SQLite. Daily progress tracking is then handled deterministically via standard SQL queries and Python business logic."*

### 2. How is structured output guaranteed?
> *"We pass a Pydantic `Roadmap` model schema directly to the Gemini API (`response_schema=Roadmap`). The response is parsed with `Roadmap.model_validate_json()`, ensuring type safety and valid nested structures before writing to SQLite."*

### 3. How does the incomplete task dependency lock work?
> *"In `src/planner.py`, we query tasks ordered by `day_number`. The application filters for the first task where `completed = 0`. If an earlier day's task is still incomplete, the planner flags `has_incomplete_previous = True` and displays a warning banner locking future tasks until the pending task is marked complete."*
