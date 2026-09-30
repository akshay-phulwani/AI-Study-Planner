import streamlit as st
from src.models import UserProfileInput
from src.llm import generate_roadmap
from src.database import save_roadmap, reset_planner, get_active_profile
from src.planner import get_planner_summary, update_task_completion
from src.roadmap import get_formatted_roadmap_data

st.set_page_config(
    page_title="AI Study Planner",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2563EB;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .warning-box {
        background-color: #FEF2F2;
        border-left: 5px solid #EF4444;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        color: #991B1B;
    }
    .success-box {
        background-color: #F0FDF4;
        border-left: 5px solid #22C55E;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        color: #166534;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🎓 AI Study Planner")
    st.caption("Personalized GenAI Learning Roadmap")
    st.divider()

    summary_info = get_planner_summary()
    has_plan = summary_info["has_roadmap"]

    pages = ["🎯 Setup & Goal", "📊 Dashboard", "🗺️ Roadmap View", "📅 Daily Plan"]
    if not has_plan:
        selected_page = "🎯 Setup & Goal"
        st.info("👋 Welcome! Please set your learning goal to generate your roadmap.")
    else:
        selected_page = st.radio("Navigation", pages, index=1)

    st.divider()
    if has_plan:
        profile_data = get_active_profile()
        if profile_data:
            st.markdown(f"**Goal:** `{profile_data['goal']}`")
            st.markdown(f"**Progress:** `{summary_info['progress_percent']}%`")

        if st.button("🔄 Reset & Create New Roadmap", use_container_width=True):
            reset_planner()
            st.success("Planner reset! Redirecting...")
            st.rerun()


if selected_page == "🎯 Setup & Goal":
    st.markdown('<div class="main-header">Generate Your AI Learning Roadmap</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Provide your availability and learning goals. ONE AI call generates your entire custom plan.</div>', unsafe_allow_html=True)

    with st.form("setup_form"):
        col1, col2 = st.columns(2)

        with col1:
            goal_option = st.selectbox(
                "What do you want to learn?",
                ["Data Analyst", "Data Scientist", "ML Engineer", "GenAI Developer", "Python Developer", "Other (Custom)"]
            )
            if goal_option == "Other (Custom)":
                custom_goal = st.text_input("Enter your custom goal:", placeholder="e.g. DevOps & Cloud Engineer")
                final_goal = custom_goal if custom_goal else "Software Developer"
            else:
                final_goal = goal_option

            weekday_hours = st.number_input("Weekday study hours (Mon - Fri):", min_value=0.5, max_value=12.0, value=2.0, step=0.5)
            weekend_hours = st.number_input("Weekend study hours (Sat - Sun):", min_value=0.5, max_value=16.0, value=4.0, step=0.5)

        with col2:
            busy_times = st.text_area("Which days/times are you busy?", value="Weekdays 9 AM - 5 PM (Work/College)", height=85)
            free_times = st.text_area("Which days/times are you free?", value="Weekday evenings (7 PM - 10 PM), Weekend mornings", height=85)
            preferred_time = st.selectbox("Preferred study time window:", ["Evening", "Morning", "Afternoon", "Night", "Flexible"])

        submit_btn = st.form_submit_button("✨ Generate My Roadmap", use_container_width=True, type="primary")

    if submit_btn:
        if not final_goal.strip():
            st.error("Please specify a valid learning goal.")
        else:
            with st.spinner("🤖 GenAI is analyzing your schedule and building your structured roadmap..."):
                try:
                    user_input = UserProfileInput(
                        goal=final_goal,
                        weekday_hours=weekday_hours,
                        weekend_hours=weekend_hours,
                        busy_times=busy_times,
                        free_times=free_times,
                        preferred_time=preferred_time
                    )
                    roadmap_obj = generate_roadmap(user_input)
                    save_roadmap(user_input, roadmap_obj)
                    st.success("🎉 Roadmap successfully generated and saved to SQLite!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate roadmap: {str(e)}")


elif selected_page == "📊 Dashboard":
    st.markdown('<div class="main-header">Learning Dashboard</div>', unsafe_allow_html=True)
    summary = get_planner_summary()

    if not summary["has_roadmap"]:
        st.warning("No roadmap active. Please visit the Setup page.")
    else:
        roadmap_meta = get_formatted_roadmap_data()["summary"]
        
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["progress_percent"]}%</div><div class="metric-label">Overall Progress</div></div>', unsafe_allow_html=True)
        with mcol2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["completed_tasks"]} / {summary["total_tasks"]}</div><div class="metric-label">Tasks Completed</div></div>', unsafe_allow_html=True)
        with mcol3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{roadmap_meta["estimated_weeks"]} Wks</div><div class="metric-label">Estimated Duration</div></div>', unsafe_allow_html=True)
        with mcol4:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{summary["current_phase"]}</div><div class="metric-label">Current Phase</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.progress(summary["progress_percent"] / 100.0)

        if summary["all_completed"]:
            st.balloons()
            st.markdown('<div class="success-box">🎓 <b>Congratulations!</b> You have completed your entire learning roadmap!</div>', unsafe_allow_html=True)
        else:
            active_task = summary["active_task"]
            
            if summary["has_incomplete_previous"]:
                st.markdown(f"""
                <div class="warning-box">
                    ⚠️ <b>Previous Task Incomplete</b><br>
                    Please complete Day {active_task['day_number']}: <b>{active_task['topic_name']} — {active_task['task_title']}</b> before unlocking upcoming tasks.
                </div>
                """, unsafe_allow_html=True)

            st.subheader("📍 Current Focus Target")
            card_col1, card_col2 = st.columns([3, 1])
            with card_col1:
                st.markdown(f"### Day {active_task['day_number']}: {active_task['task_title']}")
                st.markdown(f"**Topic:** `{active_task['topic_name']}` | **Phase:** `{active_task['phase_title']}`")
                st.write(active_task["task_description"])
                st.caption(f"⏱️ Suggested Duration: {active_task['suggested_duration_minutes']} minutes")
            with card_col2:
                if st.button("✅ Mark Complete", key=f"dash_complete_{active_task['task_id']}", use_container_width=True, type="primary"):
                    update_task_completion(active_task["task_id"], True)
                    st.rerun()


elif selected_page == "🗺️ Roadmap View":
    st.markdown('<div class="main-header">Complete Learning Roadmap</div>', unsafe_allow_html=True)
    roadmap_data = get_formatted_roadmap_data()

    if not roadmap_data["phases"]:
        st.warning("No active roadmap found.")
    else:
        summary_meta = roadmap_data["summary"]
        st.info(f"**Goal:** {summary_meta['goal']} | **Estimated Weeks:** {summary_meta['estimated_weeks']}\n\n**Strategy:** {summary_meta['summary']}")

        for phase in roadmap_data["phases"]:
            with st.expander(f"Phase {phase['phase_number']}: {phase['phase_title']}", expanded=True):
                st.write(phase["description"])
                st.divider()

                for topic in phase["topics"]:
                    st.markdown(f"#### 📌 {topic['topic_name']} *({topic['estimated_hours']} hrs)*")
                    
                    for task in topic["daily_tasks"]:
                        status_icon = "✅" if task["completed"] == 1 else "⏳"
                        st.markdown(f"- {status_icon} **Day {task['day_number']}:** {task['title']} *({task['suggested_duration_minutes']} mins)*")
                        st.caption(f"  └ {task['description']}")
                    st.write("")


elif selected_page == "📅 Daily Plan":
    st.markdown('<div class="main-header">Daily Action Plan</div>', unsafe_allow_html=True)
    summary = get_planner_summary()

    if not summary["has_roadmap"]:
        st.warning("No active roadmap found.")
    elif summary["all_completed"]:
        st.markdown('<div class="success-box">🎉 All tasks in your roadmap are complete! Great job!</div>', unsafe_allow_html=True)
    else:
        active_task = summary["active_task"]

        if summary["has_incomplete_previous"]:
            st.markdown(f"""
            <div class="warning-box">
                <b>⚠️ Action Required: Previous task incomplete</b><br>
                Complete <b>Day {active_task['day_number']} ({active_task['topic_name']} — {active_task['task_title']})</b> first.
            </div>
            """, unsafe_allow_html=True)

        st.subheader("Today's Target")
        with st.container(border=True):
            st.markdown(f"## {active_task['topic_name']} — {active_task['task_title']}")
            st.markdown(f"**Duration:** ⏱️ `{active_task['suggested_duration_minutes']} minutes` | **Day Number:** `Day {active_task['day_number']}`")
            st.divider()

            st.markdown("### Tasks & Instructions:")
            st.write(active_task["task_description"])

            st.divider()
            col_act1, col_act2 = st.columns([1, 4])
            with col_act1:
                if st.button("Mark Complete ✅", key=f"daily_done_{active_task['task_id']}", type="primary"):
                    update_task_completion(active_task["task_id"], True)
                    st.rerun()
