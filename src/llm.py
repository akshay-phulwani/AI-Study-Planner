import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import OpenAI
from src.models import UserProfileInput, Roadmap

load_dotenv()


def generate_roadmap(user_input: UserProfileInput) -> Roadmap:
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    prompt = f"""
Create a structured, step-by-step learning roadmap for a student who wants to learn: {user_input.goal}.

User Profile & Constraints:
- Target Goal/Role: {user_input.goal}
- Weekday Study Capacity: {user_input.weekday_hours} hours/day
- Weekend Study Capacity: {user_input.weekend_hours} hours/day
- Busy Times/Schedule Restrictions: {user_input.busy_times}
- Preferred Free Times: {user_input.free_times}
- Preferred Time Window: {user_input.preferred_time}

Requirements:
1. Divide the roadmap into logical, ordered learning phases.
2. Under each phase, define specific topics.
3. Under each topic, break down practical daily tasks with sequential day numbers starting from 1 (e.g. Day 1, Day 2, Day 3...).
4. Tailor task durations (in minutes) to fit the user's weekday/weekend hours and availability constraints.
5. Provide actionable, concise titles and clear study instructions for every daily task.
"""

    if gemini_key:
        client = genai.Client(api_key=gemini_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Roadmap,
                temperature=0.2,
            ),
        )
        return Roadmap.model_validate_json(response.text)

    elif openai_key:
        client = OpenAI(api_key=openai_key)
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert curriculum designer and career mentor."},
                {"role": "user", "content": prompt},
            ],
            response_format=Roadmap,
        )
        return completion.choices[0].message.parsed

    else:
        raise ValueError("No valid API key found. Please set GEMINI_API_KEY in your .env file.")
