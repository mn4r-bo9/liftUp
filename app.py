import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

# ============================================================
# LiftUp — تطبيق لياقة محلي قابل للتطوير
# هذا الإصدار ملف واحد ويخزن البيانات في SQLite بجانب app.py.
# لا تنشره للعامة قبل إضافة نظام حسابات ومراجعة أمنية.
# ============================================================

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "liftup.db"

st.set_page_config(
    page_title="LiftUp | Train Smarter",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- اللغة والنصوص --------------------
TEXT = {
    "ar": {
        "home": "الرئيسية",
        "log": "تسجيل تمرين",
        "library": "مكتبة التمارين",
        "plan": "الجدول الأسبوعي",
        "history": "سجل التمارين",
        "stats": "الإحصائيات",
        "settings": "الإعدادات",
        "welcome": "مرحبًا بك في LiftUp",
        "tagline": "تمرّن بذكاء. ارتقِ بقوتك.",
        "summary": "ملخص تدريبك",
        "total": "التمارين المسجلة",
        "week": "جلسات هذا الأسبوع",
        "volume": "حجم التدريب هذا الأسبوع",
        "quick": "ابدأ رحلتك",
        "log_desc": "سجّل الوزن والمجموعات والعدات والملاحظات.",
        "plan_desc": "خطّط أيام التدريب والراحة.",
        "exercise": "اسم التمرين",
        "muscle": "العضلة المستهدفة",
        "equipment": "المعدات",
        "weight": "الوزن (كجم)",
        "sets": "عدد المجموعات",
        "reps": "العدات لكل مجموعة",
        "notes": "ملاحظات (اختياري)",
        "duration": "مدة التمرين (دقيقة)",
        "save": "حفظ التمرين",
        "saved": "تم حفظ التمرين بنجاح!",
        "required": "اكتب اسم التمرين أولًا.",
        "recent": "آخر التمارين المسجلة",
        "none": "لا توجد تمارين مسجلة حتى الآن.",
        "search": "ابحث عن تمرين",
        "filter": "تصفية حسب العضلة",
        "all": "الكل",
        "day": "اليوم",
        "activity": "النشاط",
        "rest": "راحة",
        "training": "تدريب",
        "save_plan": "حفظ الجدول",
        "plan_saved": "تم حفظ الجدول الأسبوعي.",
        "date": "التاريخ",
        "edit": "تعديل",
        "delete": "حذف",
        "confirm_delete": "هل أنت متأكد من حذف هذا السجل؟",
        "confirm": "نعم، احذف",
        "cancel": "إلغاء",
        "updated": "تم تحديث التمرين.",
        "deleted": "تم حذف التمرين.",
        "no_results": "لا توجد نتائج مطابقة.",
        "language": "اللغة",
        "appearance": "المظهر",
        "light": "فاتح",
        "dark": "داكن",
        "mint": "نعناعي وأبيض",
        "blue": "أزرق فاتح وأبيض",
        "purple": "بنفسجي وأبيض",
        "sand": "رملي وزيتوني",
        "charcoal": "فحمي وأخضر",
        "theme": "لوحة الألوان",
        "settings_saved": "تم حفظ الإعدادات لهذا التشغيل.",
        "records": "الأرقام القياسية",
        "exercise_count": "عدد السجلات",
        "avg_weight": "متوسط الوزن",
        "chart": "تطور الوزن حسب التمرين",
        "choose_exercise": "اختر تمرينًا لعرض تطور وزنه",
        "no_chart": "سجّل التمرين نفسه أكثر من مرة حتى يظهر تطور الوزن.",
        "volume_chart": "حجم التدريب حسب اليوم",
        "empty_day": "اختر نشاطًا لكل يوم ثم احفظ الجدول.",
        "about": "حول LiftUp",
        "about_text": "نسخة محلية أولية. بياناتك محفوظة على هذا الجهاز فقط.",
        "warning": "تنبيه: هذا الإصدار لا يحتوي على حسابات مستخدمين أو مزامنة سحابية.",
        "kg": "كجم",
        "sets_short": "مجموعات",
        "reps_short": "عدات",
        "minutes": "دقيقة",
        "filter_equipment": "تصفية حسب المعدات",
        "bodyweight": "وزن الجسم",
        "dumbbell": "دمبل",
        "barbell": "بار",
        "machine": "جهاز",
        "cable": "كيبل",
        "bands": "أشرطة مقاومة",
        "other": "أخرى",
        "chest": "الصدر",
        "back": "الظهر",
        "shoulders": "الأكتاف",
        "biceps": "البايسبس",
        "triceps": "الترايسبس",
        "legs": "الأرجل",
        "glutes": "الأرداف",
        "core": "عضلات البطن",
        "full": "الجسم كامل",
        "cardio": "القلب واللياقة",
        "arms": "الذراعان",
        "push": "دفع",
        "pull": "سحب",
        "lower": "الجزء السفلي",
        "upper": "الجزء العلوي",
        "custom": "مخصص",
        "goal": "هدفك",
        "goal_muscle": "زيادة العضلات",
        "goal_strength": "زيادة القوة",
        "goal_fitness": "اللياقة العامة",
        "days": "أيام التدريب المفضلة",
        "profile_saved": "تم حفظ التفضيلات.",
        "sets_detail": "تفاصيل المجموعة",
        "edit_title": "تعديل سجل تمرين",
        "select_record": "اختر سجلًا لتعديله",
        "update": "حفظ التعديلات",
        "export": "تنزيل سجل التمارين CSV",
        "download_help": "ملف CSV يحتوي على سجلات التمارين المحلية.",
    },
    "en": {
        "home": "Home", "log": "Log Workout", "library": "Exercise Library",
        "plan": "Weekly Plan", "history": "Workout History", "stats": "Statistics",
        "settings": "Settings", "welcome": "Welcome to LiftUp",
        "tagline": "Train Smarter. Rise Stronger.", "summary": "Training Summary",
        "total": "Workout records", "week": "Sessions this week",
        "volume": "Training volume this week", "quick": "Start Your Journey",
        "log_desc": "Record weight, sets, reps and notes.", "plan_desc": "Plan training and rest days.",
        "exercise": "Exercise name", "muscle": "Target muscle", "equipment": "Equipment",
        "weight": "Weight (kg)", "sets": "Number of sets", "reps": "Reps per set",
        "notes": "Notes (optional)", "duration": "Workout duration (minutes)",
        "save": "Save workout", "saved": "Workout saved!", "required": "Enter an exercise name.",
        "recent": "Recent workouts", "none": "No workouts recorded yet.",
        "search": "Search exercises", "filter": "Filter by muscle", "all": "All",
        "day": "Day", "activity": "Activity", "rest": "Rest", "training": "Training",
        "save_plan": "Save plan", "plan_saved": "Weekly plan saved.", "date": "Date",
        "edit": "Edit", "delete": "Delete", "confirm_delete": "Delete this record?",
        "confirm": "Yes, delete", "cancel": "Cancel", "updated": "Workout updated.",
        "deleted": "Workout deleted.", "no_results": "No matching results.",
        "language": "Language", "appearance": "Appearance", "light": "Light",
        "dark": "Dark", "mint": "Mint & White", "blue": "Light Blue & White",
        "purple": "Purple & White", "sand": "Sand & Olive", "charcoal": "Charcoal & Green",
        "theme": "Color palette", "settings_saved": "Settings saved for this run.",
        "records": "Personal bests", "exercise_count": "Records",
        "avg_weight": "Average weight", "chart": "Weight progress by exercise",
        "choose_exercise": "Choose an exercise to view weight progress",
        "no_chart": "Log the same exercise more than once to see progress.",
        "volume_chart": "Training volume by day", "empty_day": "Choose an activity for each day and save.",
        "about": "About LiftUp", "about_text": "Local starter version. Data is stored on this device only.",
        "warning": "Note: this version has no user accounts or cloud sync.",
        "kg": "kg", "sets_short": "sets", "reps_short": "reps",
        "minutes": "minutes", "filter_equipment": "Filter by equipment",
        "bodyweight": "Bodyweight", "dumbbell": "Dumbbell", "barbell": "Barbell",
        "machine": "Machine", "cable": "Cable", "bands": "Resistance bands",
        "other": "Other", "chest": "Chest", "back": "Back", "shoulders": "Shoulders",
        "biceps": "Biceps", "triceps": "Triceps", "legs": "Legs", "glutes": "Glutes",
        "core": "Core", "full": "Full body", "cardio": "Cardio", "arms": "Arms",
        "push": "Push", "pull": "Pull", "lower": "Lower body", "upper": "Upper body",
        "custom": "Custom", "goal": "Your goal", "goal_muscle": "Muscle gain",
        "goal_strength": "Strength", "goal_fitness": "General fitness",
        "days": "Preferred training days", "profile_saved": "Preferences saved.",
        "sets_detail": "Set details", "edit_title": "Edit workout record",
        "select_record": "Choose a record to edit", "update": "Save changes",
        "export": "Download workout history CSV", "download_help": "CSV of local workout records.",
    },
}

if "language" not in st.session_state:
    st.session_state.language = "ar"
if "theme" not in st.session_state:
    st.session_state.theme = "Mint & White"

LANG = st.session_state.language
T = TEXT[LANG]


def tr(key):
    return T.get(key, key)


MUSCLES = ["chest", "back", "shoulders", "biceps", "triceps", "legs",
           "glutes", "core", "full", "cardio", "arms"]
EQUIPMENT = ["bodyweight", "dumbbell", "barbell", "machine", "cable", "bands", "other"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAY_AR = {
    "Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء",
    "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"
}
PALETTES = {
    "Mint & White": ("#F2F8F5", "#155B49", "#FFFFFF", "#D7E8DF"),
    "Light Blue & White": ("#F2F7FC", "#245A8D", "#FFFFFF", "#D9E7F5"),
    "Purple & White": ("#F7F4FB", "#6741A5", "#FFFFFF", "#E5DDF3"),
    "Sand & Olive": ("#F8F5EC", "#59643A", "#FFFFFF", "#E8E0CC"),
    "Charcoal & Green": ("#202A27", "#52B788", "#2C3733", "#46534D"),
}
palette = PALETTES.get(st.session_state.theme, PALETTES["Mint & White"])
bg, accent, card, border = palette
text_color = "#F5F7F6" if st.session_state.theme == "Charcoal & Green" else "#20312B"

st.markdown(f"""
<style>
.stApp {{ background: {bg}; color: {text_color}; }}
.block-container {{ max-width: 1200px; padding-top: 1.8rem; padding-bottom: 3rem; }}
.hero {{ background: linear-gradient(120deg, {accent}, #247A65); padding: 30px;
         border-radius: 20px; color: white; margin-bottom: 20px; }}
.hero h1, .hero p {{ color: white; }}
div[data-testid="stMetric"] {{ background: {card}; padding: 16px; border-radius: 14px;
                              border: 1px solid {border}; }}
div[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 14px; }}
.stButton > button, .stFormSubmitButton > button {{ border-radius: 10px; }}
</style>
""", unsafe_allow_html=True)

# -------------------- قاعدة البيانات والترقية الآمنة --------------------
def connect_db():
    return sqlite3.connect(DB_PATH, timeout=15)


def init_db():
    with closing(connect_db()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise TEXT NOT NULL DEFAULT 'Workout',
                muscle TEXT NOT NULL DEFAULT 'full',
                equipment TEXT NOT NULL DEFAULT 'other',
                weight REAL NOT NULL DEFAULT 0,
                sets INTEGER NOT NULL DEFAULT 1,
                reps INTEGER NOT NULL DEFAULT 1,
                duration INTEGER NOT NULL DEFAULT 0,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT ''
            )
        """)
        columns = {row[1] for row in conn.execute("PRAGMA table_info(workouts)")}
        needed = {
            "exercise": "TEXT NOT NULL DEFAULT 'Workout'",
            "muscle": "TEXT NOT NULL DEFAULT 'full'",
            "equipment": "TEXT NOT NULL DEFAULT 'other'",
            "weight": "REAL NOT NULL DEFAULT 0",
            "sets": "INTEGER NOT NULL DEFAULT 1",
            "reps": "INTEGER NOT NULL DEFAULT 1",
            "duration": "INTEGER NOT NULL DEFAULT 0",
            "notes": "TEXT DEFAULT ''",
            "created_at": "TEXT NOT NULL DEFAULT ''",
        }
        for name, definition in needed.items():
            if name not in columns:
                conn.execute(f"ALTER TABLE workouts ADD COLUMN {name} {definition}")
        conn.execute(
            "UPDATE workouts SET created_at=? WHERE created_at IS NULL OR created_at=''",
            (datetime.now().strftime("%Y-%m-%d %H:%M"),),
        )
        conn.execute("""
            CREATE TABLE IF NOT EXISTS weekly_plan (
                day TEXT PRIMARY KEY,
                activity TEXT NOT NULL DEFAULT 'rest',
                focus TEXT NOT NULL DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        conn.commit()


def add_workout(data):
    with closing(connect_db()) as conn:
        conn.execute("""
            INSERT INTO workouts
            (exercise, muscle, equipment, weight, sets, reps, duration, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["exercise"], data["muscle"], data["equipment"], data["weight"],
            data["sets"], data["reps"], data["duration"], data["notes"],
            datetime.now().strftime("%Y-%m-%d %H:%M"),
        ))
        conn.commit()


def list_workouts():
    with closing(connect_db()) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(
            "SELECT * FROM workouts ORDER BY created_at DESC, id DESC"
        ).fetchall()]


def update_workout(workout_id, data):
    with closing(connect_db()) as conn:
        conn.execute("""
            UPDATE workouts SET exercise=?, muscle=?, equipment=?, weight=?, sets=?,
                reps=?, duration=?, notes=? WHERE id=?
        """, (
            data["exercise"], data["muscle"], data["equipment"], data["weight"],
            data["sets"], data["reps"], data["duration"], data["notes"], workout_id,
        ))
        conn.commit()


def delete_workout(workout_id):
    with closing(connect_db()) as conn:
        conn.execute("DELETE FROM workouts WHERE id=?", (workout_id,))
        conn.commit()


def save_plan(rows):
    with closing(connect_db()) as conn:
        conn.executemany("""
            INSERT INTO weekly_plan(day, activity, focus) VALUES (?, ?, ?)
            ON CONFLICT(day) DO UPDATE SET activity=excluded.activity, focus=excluded.focus
        """, rows)
        conn.commit()


def load_plan():
    with closing(connect_db()) as conn:
        saved = {row[0]: (row[1], row[2]) for row in conn.execute(
            "SELECT day, activity, focus FROM weekly_plan"
        )}
    return {day: saved.get(day, ("rest", "")) for day in DAYS}


def save_pref(key, value):
    with closing(connect_db()) as conn:
        conn.execute("""
            INSERT INTO preferences(key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (key, str(value)))
        conn.commit()


def load_pref(key, default):
    with closing(connect_db()) as conn:
        row = conn.execute("SELECT value FROM preferences WHERE key=?", (key,)).fetchone()
    return row[0] if row else default


init_db()

# قائمة التمارين المقترحة
EXERCISES = [
    ("Bench Press", "chest", "barbell"),
    ("Push-up", "chest", "bodyweight"),
    ("Dumbbell Fly", "chest", "dumbbell"),
    ("Lat Pulldown", "back", "machine"),
    ("Pull-up", "back", "bodyweight"),
    ("Barbell Row", "back", "barbell"),
    ("Seated Cable Row", "back", "cable"),
    ("Shoulder Press", "shoulders", "dumbbell"),
    ("Lateral Raise", "shoulders", "dumbbell"),
    ("Biceps Curl", "biceps", "dumbbell"),
    ("Hammer Curl", "biceps", "dumbbell"),
    ("Triceps Pushdown", "triceps", "cable"),
    ("Squat", "legs", "barbell"),
    ("Leg Press", "legs", "machine"),
    ("Romanian Deadlift", "legs", "barbell"),
    ("Leg Curl", "legs", "machine"),
    ("Calf Raise", "legs", "machine"),
    ("Hip Thrust", "glutes", "barbell"),
    ("Plank", "core", "bodyweight"),
    ("Crunch", "core", "bodyweight"),
    ("Treadmill", "cardio", "machine"),
]
exercise_names = sorted({item[0] for item in EXERCISES})

# -------------------- تنقل التطبيق --------------------
PAGES = ["home", "log", "library", "plan", "history", "stats", "settings"]
PAGE_LABELS = {
    "home": "🏠 " + tr("home"),
    "log": "🏋️ " + tr("log"),
    "library": "📚 " + tr("library"),
    "plan": "📅 " + tr("plan"),
    "history": "📖 " + tr("history"),
    "stats": "📈 " + tr("stats"),
    "settings": "⚙️ " + tr("settings"),
}
if "page" not in st.session_state:
    st.session_state.page = "home"

with st.sidebar:
    st.title("💪 LiftUp")
    st.caption("Train Smarter. Rise Stronger.")
    st.divider()
    selected = st.radio(
        tr("home") + " / " + tr("settings"),
        PAGES,
        format_func=lambda key: PAGE_LABELS[key],
        index=PAGES.index(st.session_state.page),
        key="nav_radio",
        label_visibility="collapsed",
    )
    st.session_state.page = selected
    st.divider()
    st.caption(tr("about_text"))
    st.caption("v1.0 • Local prototype")

page = st.session_state.page
workouts = list_workouts()
today = date.today()
week_start = today - timedelta(days=today.weekday())
this_week = [
    w for w in workouts
    if w["created_at"][:10] and week_start.isoformat() <= w["created_at"][:10] <= today.isoformat()
]
weekly_volume = sum(w["weight"] * w["sets"] * w["reps"] for w in this_week)

# -------------------- الصفحة الرئيسية --------------------
if page == "home":
    st.markdown(f"""
    <div class="hero">
      <h1>💪 {tr("welcome")}</h1>
      <p>{tr("tagline")}</p>
      <p>{'كل تمرين يقربك من هدفك. ابدأ اليوم واصنع تقدمك.' if LANG == 'ar' else 'Every workout brings you closer to your goal.'}</p>
    </div>
    """, unsafe_allow_html=True)
    st.subheader(tr("summary"))
    c1, c2, c3 = st.columns(3)
    c1.metric(tr("total"), len(workouts))
    c2.metric(tr("week"), len(this_week))
    c3.metric(tr("volume"), f"{weekly_volume:,.0f} kg")
    st.write("")
    st.subheader(tr("quick"))
    a, b = st.columns(2)
    with a:
        with st.container(border=True):
            st.subheader("🏋️ " + tr("log"))
            st.write(tr("log_desc"))
            if st.button(tr("log"), use_container_width=True):
                st.session_state.page = "log"
                st.rerun()
    with b:
        with st.container(border=True):
            st.subheader("📅 " + tr("plan"))
            st.write(tr("plan_desc"))
            if st.button(tr("plan"), use_container_width=True):
                st.session_state.page = "plan"
                st.rerun()
    st.info("التقدم المستمر أهم من الكمال. تمرّن بذكاء واسترح عند الحاجة." if LANG == "ar"
            else "Consistency beats perfection. Train smart and recover when needed.")

# -------------------- تسجيل تمرين --------------------
elif page == "log":
    st.title("🏋️ " + tr("log"))
    st.write(tr("log_desc"))
    suggestions = ["— " + tr("custom") + " —"] + exercise_names
    with st.form("add_workout_form", clear_on_submit=True):
        selected_ex = st.selectbox(tr("exercise"), suggestions)
        custom_ex = ""
        if selected_ex.startswith("—"):
            custom_ex = st.text_input(tr("exercise") + " *")
        default_ex = custom_ex.strip() if selected_ex.startswith("—") else selected_ex

        c1, c2 = st.columns(2)
        with c1:
            muscle = st.selectbox(tr("muscle"), MUSCLES, format_func=tr)
            equipment = st.selectbox(tr("equipment"), EQUIPMENT, format_func=tr)
            weight = st.number_input(tr("weight"), min_value=0.0, max_value=1000.0, value=20.0, step=2.5)
        with c2:
            sets = st.number_input(tr("sets"), min_value=1, max_value=100, value=3, step=1)
            reps = st.number_input(tr("reps"), min_value=1, max_value=500, value=10, step=1)
            duration = st.number_input(tr("duration"), min_value=0, max_value=1000, value=0, step=5)
        notes = st.text_area(tr("notes"))
        submitted = st.form_submit_button("💾 " + tr("save"), use_container_width=True)

    if submitted:
        exercise_name = default_ex.strip()
        if not exercise_name:
            st.error(tr("required"))
        else:
            add_workout({
                "exercise": exercise_name, "muscle": muscle, "equipment": equipment,
                "weight": weight, "sets": sets, "reps": reps,
                "duration": duration, "notes": notes.strip(),
            })
            st.success(tr("saved"))
            st.rerun()

    st.divider()
    st.subheader(tr("recent"))
    recent = list_workouts()[:5]
    if not recent:
        st.info(tr("none"))
    for w in recent:
        with st.container(border=True):
            st.markdown(f"**{w['exercise']}**")
            st.write(
                f"{tr('weight')}: {w['weight']:g} | {tr('sets')}: {w['sets']} | "
                f"{tr('reps')}: {w['reps']}"
            )
            st.caption(w["created_at"])
            if w["notes"]:
                st.write(w["notes"])

# -------------------- مكتبة التمارين --------------------
elif page == "library":
    st.title("📚 " + tr("library"))
    query = st.text_input(tr("search"))
    muscle_filter = st.selectbox(tr("filter"), ["all"] + MUSCLES, format_func=lambda x: tr(x) if x != "all" else tr("all"))
    equipment_filter = st.selectbox(tr("filter_equipment"), ["all"] + EQUIPMENT, format_func=lambda x: tr(x) if x != "all" else tr("all"))
    rows = []
    for name, muscle, equipment in EXERCISES:
        if query and query.casefold() not in name.casefold():
            continue
        if muscle_filter != "all" and muscle != muscle_filter:
            continue
        if equipment_filter != "all" and equipment != equipment_filter:
            continue
        rows.append({
            tr("exercise"): name,
            tr("muscle"): tr(muscle),
            tr("equipment"): tr(equipment),
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info(tr("no_results"))
    st.caption("المكتبة أولية ويمكن توسيعها وإضافة الرسومات لاحقًا." if LANG == "ar"
               else "Starter library; more exercises and illustrations can be added later.")

# -------------------- الجدول الأسبوعي --------------------
elif page == "plan":
    st.title("📅 " + tr("plan"))
    st.write(tr("empty_day"))
    current_plan = load_plan()
    with st.form("weekly_plan_form"):
        form_values = {}
        for day in DAYS:
            left, right = st.columns([1, 2])
            with left:
                st.markdown(f"**{DAY_AR[day] if LANG == 'ar' else day}**")
            with right:
                old_activity, old_focus = current_plan[day]
                activity = st.selectbox(
                    tr("activity"),
                    ["rest", "upper", "lower", "push", "pull", "full", "custom"],
                    index=["rest", "upper", "lower", "push", "pull", "full", "custom"].index(old_activity)
                    if old_activity in ["rest", "upper", "lower", "push", "pull", "full", "custom"] else 0,
                    format_func=lambda x: tr(x),
                    key=f"plan_activity_{day}",
                )
                focus = st.text_input(
                    "تفاصيل" if LANG == "ar" else "Focus",
                    value=old_focus,
                    key=f"plan_focus_{day}",
                    placeholder="مثال: صدر وترايسبس" if LANG == "ar" else "e.g. chest and triceps",
                )
                form_values[day] = (activity, focus)
        save_week = st.form_submit_button(tr("save_plan"), use_container_width=True)
    if save_week:
        save_plan([(day, *form_values[day]) for day in DAYS])
        st.success(tr("plan_saved"))
        st.rerun()
    st.divider()
    for day in DAYS:
        activity, focus = current_plan[day]
        day_name = DAY_AR[day] if LANG == "ar" else day
        with st.container(border=True):
            st.markdown(f"**{day_name} — {tr(activity)}**")
            if focus:
                st.write(focus)

# -------------------- السجل مع التعديل والحذف --------------------
elif page == "history":
    st.title("📖 " + tr("history"))
    all_workouts = list_workouts()
    if not all_workouts:
        st.info(tr("none"))
    else:
        export_df = pd.DataFrame(all_workouts)
        export_df = export_df.drop(columns=["id"], errors="ignore")
        csv_data = export_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            tr("export"), data=csv_data, file_name="liftup_workouts.csv",
            mime="text/csv", help=tr("download_help"),
        )
        options = {
            f"#{w['id']} — {w['exercise']} — {w['created_at']}": w
            for w in all_workouts
        }
        chosen_label = st.selectbox(tr("select_record"), list(options.keys()))
        chosen = options[chosen_label]

        with st.expander("✏️ " + tr("edit_title"), expanded=False):
            with st.form(f"edit_form_{chosen['id']}"):
                e_name = st.text_input(tr("exercise"), value=chosen["exercise"])
                e1, e2 = st.columns(2)
                with e1:
                    e_muscle = st.selectbox(tr("muscle"), MUSCLES,
                        index=MUSCLES.index(chosen["muscle"]) if chosen["muscle"] in MUSCLES else 0,
                        format_func=tr)
                    e_equipment = st.selectbox(tr("equipment"), EQUIPMENT,
                        index=EQUIPMENT.index(chosen["equipment"]) if chosen["equipment"] in EQUIPMENT else 0,
                        format_func=tr)
                    e_weight = st.number_input(tr("weight"), min_value=0.0, max_value=1000.0,
                        value=float(chosen["weight"]), step=2.5)
                with e2:
                    e_sets = st.number_input(tr("sets"), min_value=1, max_value=100, value=int(chosen["sets"]))
                    e_reps = st.number_input(tr("reps"), min_value=1, max_value=500, value=int(chosen["reps"]))
                    e_duration = st.number_input(tr("duration"), min_value=0, max_value=1000, value=int(chosen["duration"]))
                e_notes = st.text_area(tr("notes"), value=chosen["notes"] or "")
                update_pressed = st.form_submit_button(tr("update"), use_container_width=True)
            if update_pressed:
                if not e_name.strip():
                    st.error(tr("required"))
                else:
                    update_workout(chosen["id"], {
                        "exercise": e_name.strip(), "muscle": e_muscle,
                        "equipment": e_equipment, "weight": e_weight,
                        "sets": e_sets, "reps": e_reps,
                        "duration": e_duration, "notes": e_notes.strip(),
                    })
                    st.success(tr("updated"))
                    st.rerun()

        with st.expander("🗑️ " + tr("delete"), expanded=False):
            st.warning(tr("confirm_delete"))
            confirm = st.checkbox(tr("confirm_delete"), key=f"confirm_delete_{chosen['id']}")
            if st.button("🗑️ " + tr("confirm"), disabled=not confirm, key=f"delete_{chosen['id']}"):
                delete_workout(chosen["id"])
                st.success(tr("deleted"))
                st.rerun()

        st.divider()
        for w in all_workouts:
            with st.container(border=True):
                st.markdown(f"**{w['exercise']}**")
                st.write(f"{w['weight']:g} kg • {w['sets']} sets × {w['reps']} reps")
                st.caption(w["created_at"])
                if w["notes"]:
                    st.write(w["notes"])

# -------------------- الإحصائيات --------------------
elif page == "stats":
    st.title("📈 " + tr("stats"))
    all_workouts = list_workouts()
    if not all_workouts:
        st.info(tr("none"))
    else:
        df = pd.DataFrame(all_workouts)
        df["created_date"] = pd.to_datetime(df["created_at"], errors="coerce").dt.date
        df["volume"] = df["weight"] * df["sets"] * df["reps"]
        c1, c2, c3 = st.columns(3)
        c1.metric(tr("total"), len(df))
        c2.metric(tr("avg_weight"), f"{df['weight'].mean():.1f} kg")
        c3.metric(tr("records"), df.groupby("exercise")["weight"].max().count())

        st.subheader(tr("chart"))
        exercise_choice = st.selectbox(tr("choose_exercise"), sorted(df["exercise"].unique()))
        progress = df[df["exercise"] == exercise_choice].sort_values("created_at")
        if len(progress) >= 2:
            chart_df = progress[["created_at", "weight"]].set_index("created_at")
            st.line_chart(chart_df, y="weight")
        else:
            st.info(tr("no_chart"))

        st.subheader(tr("volume_chart"))
        daily = df.groupby("created_date", dropna=True)["volume"].sum().sort_index()
        if not daily.empty:
            st.bar_chart(daily)
        st.caption("حجم التدريب هنا محسوب بالوزن × المجموعات × العدات، ولا يشمل تمارين وزن الجسم بدقة.")

# -------------------- الإعدادات --------------------
elif page == "settings":
    st.title("⚙️ " + tr("settings"))
    st.subheader(tr("appearance"))
    with st.form("settings_form"):
        lang_choice = st.selectbox(
            tr("language"), ["ar", "en"],
            index=0 if st.session_state.language == "ar" else 1,
            format_func=lambda x: "العربية" if x == "ar" else "English",
        )
        theme_keys = list(PALETTES.keys())
        current_theme = st.session_state.theme
        theme_choice = st.selectbox(
            tr("theme"), theme_keys,
            index=theme_keys.index(current_theme) if current_theme in theme_keys else 0,
            format_func=lambda x: {
                "Mint & White": tr("mint"), "Light Blue & White": tr("blue"),
                "Purple & White": tr("purple"), "Sand & Olive": tr("sand"),
                "Charcoal & Green": tr("charcoal"),
            }[x],
        )
        goal_choice = st.selectbox(
            tr("goal"), ["goal_muscle", "goal_strength", "goal_fitness"],
            format_func=tr,
        )
        days_choice = st.multiselect(
            tr("days"), DAYS,
            default=["Monday", "Wednesday", "Friday"],
            format_func=lambda x: DAY_AR[x] if LANG == "ar" else x,
        )
        settings_submit = st.form_submit_button(tr("profile_saved"), use_container_width=True)
    if settings_submit:
        st.session_state.language = lang_choice
        st.session_state.theme = theme_choice
        save_pref("goal", goal_choice)
        save_pref("training_days", ",".join(days_choice))
        st.success(tr("settings_saved"))
        st.rerun()

    st.divider()
    st.subheader(tr("about"))
    st.write(tr("about_text"))
    st.warning(tr("warning"))
    st.caption(f"Database: {DB_PATH.name}")
