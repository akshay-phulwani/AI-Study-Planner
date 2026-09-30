from typing import List, Optional
from pydantic import BaseModel, Field


class DailyTask(BaseModel):
    day_number: int = Field(description="Sequential day index starting from 1")
    title: str = Field(description="Actionable title of the daily task")
    description: str = Field(description="Specific concepts, readings, or hands-on practice items")
    suggested_duration_minutes: int = Field(description="Suggested duration in minutes")


class Topic(BaseModel):
    topic_name: str = Field(description="Name of the topic")
    estimated_hours: float = Field(description="Total estimated study hours for this topic")
    daily_tasks: List[DailyTask] = Field(description="Ordered daily tasks for this topic")


class Phase(BaseModel):
    phase_number: int = Field(description="Sequential phase index starting from 1")
    phase_title: str = Field(description="Title of the phase")
    description: str = Field(description="Summary of what the learner achieves in this phase")
    topics: List[Topic] = Field(description="Topics belonging to this phase")


class Roadmap(BaseModel):
    goal: str = Field(description="The career or skill goal")
    estimated_weeks: int = Field(description="Total estimated roadmap duration in weeks")
    summary: str = Field(description="Overview of the personalized study strategy")
    phases: List[Phase] = Field(description="Chronological phases of the roadmap")


class UserProfileInput(BaseModel):
    goal: str
    weekday_hours: float
    weekend_hours: float
    busy_times: str
    free_times: str
    preferred_time: Optional[str] = "Flexible"
