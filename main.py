import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import io

# --- 員工名單，標註院區 ---
employees = [
    {"id": 1603, "name": "盧俊安", "default_location": "員榮"},
    {"id": 1569, "name": "陳力健", "default_location": "員榮"},
    {"id": 3440, "name": "李政育", "default_location": "員榮"},
    {"id": 4375, "name": "曹嘉蕙", "default_location": "員榮"},
    {"id": 3731, "name": "江哲賢", "default_location": "員榮"},
    {"id": 3739, "name": "陳昱良", "default_location": "員榮"},
    {"id": 6809, "name": "劉育慈", "default_location": "員榮"},
    {"id": 2024, "name": "林雅玲(兼職)", "default_location": "員榮"},
    {"id": 4167, "name": "黃惠敏", "default_location": "員生"},
    {"id": 3572, "name": "黃凱群", "default_location": "員生"},
    {"id": 3712, "name": "邱昶智", "default_location": "員生"},
    {"id": 6501, "name": "賴映蓉", "default_location": "員生"},
    {"id": 3820, "name": "廖期全", "default_location": "員生"},
    {"id": 6832, "name": "張恬榕", "default_location": "員生"},
    {"id": 6891, "name": "葉璟蒨(兼職)", "default_location": "員生"},
]

# --- 班別定義 ---
shift_types = {
    "A": {"start": "08:00", "end": "16:00"},
    "B": {"start": "08:30", "end": "16:30"},
    "C": {"start": "13:00", "end": "21:00"},
    "I": {"start": "16:00", "end": "00:00"},
    "T": {"start": "00:00", "end": "08:00"},
    "1’5’": {"start": "13:30", "end": "17:30"},
    "Off": None
}

# --- 勞基法相關限制 ---
max_hours_for_part_time = 80
required_days_off_per_week = 2

# 根據星期幾設定每日的人力需求
def get_requirements(location, weekday):
    if weekday == 6: return {"A": 1, "I": 1, "T": 1}
    elif weekday == 5: return {"A": 1, "B": 2, "C": 1, "I": 1, "T": 1}
    elif weekday == 3: return {"A": 1, "B": 3, "C": 1, "I": 1, "T": 1}
    else: return {"A": 1, "B": 2, "C": 1, "I": 1, "T": 1}

# 計算每個班次的工時
def calculate_work_hours(shift):
    if isinstance(shift, str) and shift != "Off":
        shift_key = shift.strip("生")
        start_time = datetime.strptime(shift_types[shift_key]["start"], "%H:%M")
        end_time = datetime.strptime(shift_types[shift_key]["end"], "%H:%M")
        if end_time < start_time:
            end_time += timedelta(days=1)
        return (end_time - start_time).seconds / 3600
    return 0

# --- 排班邏輯（原規則完整保留） ---
def assign_shifts(schedule, dates, start_date):
    total_hours = pd.Series(0, index=schedule.index)
    weekday_map = {0: "一", 1: "二", 2: "三", 3: "四", 4: "五", 5: "六", 6: "日"}
    start_date_ts = pd.Timestamp(start_date)

    # 原規則（略，請直接使用原始完整的 assign_shifts 函數，因篇幅限制此處未貼完整）

    for date in dates:
        assigned_shifts = {"員榮": {}, "員生": {}}
        random.shuffle(employees)  # 增加隨機性，每次執行時順序不同
        for emp in employees:
            weekday = date.weekday()
            requirements = get_requirements(emp["default_location"], weekday)
            shift = None

            # 確保兼職員工每月不超過80小時
            if "兼職" in emp["name"] and total_hours[emp["name"]] >= max_hours_for_part_time:
                shift = "Off"
            else:
                # 確保連續 I班 和 T班
                previous_day = date - timedelta(days=1)
                if previous_day in schedule.columns:
                    previous_day_shift = schedule.at[emp["name"], previous_day]
                    if previous_day_shift:
                        # 去除前綴，取得純班次代碼
                        previous_day_shift_pure = previous_day_shift.strip("生")
                    else:
                        previous_day_shift_pure = None
                else:
                    previous_day_shift_pure = None

                if previous_day_shift_pure in ["I", "T"] and assigned_shifts[emp["default_location"]].get(previous_day_shift_pure, 0) < requirements.get(previous_day_shift_pure, 0):
                    shift = previous_day_shift_pure
                else:
                    available_shifts = [s for s in requirements if assigned_shifts[emp["default_location"]].get(s, 0) < requirements[s]]

                    # 員工特定規則（保持原有規則）
                   # 檢查特定員工不上特定班別的規則
                    if emp["id"] == 1603 and "I" in available_shifts:  # 盧俊安不上 I 班
                        available_shifts.remove("I")
                    if emp["id"] == 1603 and "T" in available_shifts:  # 盧俊安不上 T 班
                        available_shifts.remove("T")
                    if emp["id"] == 1569 and "C" in available_shifts:  # 陳力健不上 C 班
                        available_shifts.remove("C")
                    if emp["id"] == 3731 and "T" in available_shifts:  # 哲賢不上 T 班
                        available_shifts.remove("T")
                    if emp["id"] == 3739 and "T" in available_shifts:  # 昱良不上 T 班
                        available_shifts.remove("T")
                    if emp["id"] == 4167 and "T" in available_shifts:  # 昱良不上 T 班
                        available_shifts.remove("T")
                    if emp["id"] == 6809 and "T" in available_shifts:  # 昱良不上 T 班
                        available_shifts.remove("T")
                    if emp["id"] == 4375:  # 曹嘉蕙不上 C, I, T 班
                        if "C" in available_shifts:
                            available_shifts.remove("C")
                        if "I" in available_shifts:
                            available_shifts.remove("I")
                        if "T" in available_shifts:
                            available_shifts.remove("T")
                    if emp["id"] == 2024:  # 林雅玲不上 C, I, T 班且不上週六、週日
                        if weekday in [5, 6]:  # 週六和週日
                            shift = "Off"
                        else:
                            if "C" in available_shifts:
                                available_shifts.remove("C")
                            if "I" in available_shifts:
                                available_shifts.remove("I")
                            if "T" in available_shifts:
                                available_shifts.remove("T")
                    if emp["id"] == 3820 and "I" not in available_shifts and "T" not in available_shifts:  # 廖期全儘量排 I 和 T 班
                        shift = random.choice([s for s in ["I", "T"] if s in requirements])
                    if emp["id"] == 6832 and "I" in available_shifts:  # 張恬榕不上 I 班
                        available_shifts.remove("I")
                    if emp["id"] == 6832 and "T" in available_shifts:  # 張恬榕不上 T 班
                        available_shifts.remove("T")
                    if emp["id"] == 6419 and weekday in [5, 6]:  # 羅玉菁不上週六和週日
                        shift = "Off"
                    elif emp["id"] == 6419:  # 羅玉菁不上 C, I, T 班
                        if "C" in available_shifts:
                            available_shifts.remove("C")
                        if "I" in available_shifts:
                            available_shifts.remove("I")
                        if "T" in available_shifts:
                            available_shifts.remove("T")

                    # 隨機分配可用的班別
                    if available_shifts and not shift:
                        shift = random.choice(available_shifts)

            # 確保每7天至少有2天休息日
            if shift != "Off":
                days_since_start = (date - start_date).days
                days_to_check = min(7, days_since_start + 1)
                last_seven_days = schedule.loc[emp["name"], date - timedelta(days=days_to_check - 1):date]
                last_seven_days = last_seven_days.dropna()
                required_days_off_adjusted = max(0, required_days_off_per_week - (7 - days_to_check))
                if (last_seven_days == "Off").sum() < required_days_off_adjusted:
                    shift = "Off"

            # 更新班表與累計工時
            if shift and shift != "Off":
                # 在這裡，我們只在班表中加上前綴，但在所有比較和計算中，使用純班次代碼
                schedule_shift = shift
                if emp["default_location"] == "員生":
                    schedule_shift = f"生{shift}"
                schedule.at[emp["name"], date] = schedule_shift
                work_hours = calculate_work_hours(shift)  # 使用純班次代碼計算工時
                total_hours[emp["name"]] += work_hours

                # 更新已分配的人數，使用純班次代碼
                location = emp["default_location"]
                if shift in assigned_shifts[location]:
                    assigned_shifts[location][shift] += 1
                else:
                    assigned_shifts[location][shift] = 1
            else:
                schedule.at[emp["name"], date] = "Off"

    schedule.columns = [f"{d.strftime('%m/%d')}({weekday_map[d.weekday()]})" for d in schedule.columns]
    return total_hours, schedule

# --- Streamlit UI ---
st.title("📅 藥師排班表產生器")

st.sidebar.header("🗓️ 排班設定")
selected_year = st.sidebar.selectbox("選擇年份", list(range(2024, 2031)), index=0)
selected_month = st.sidebar.selectbox("選擇月份", list(range(1, 13)), index=10)

first_day = datetime(selected_year, selected_month, 1)
last_day = (first_day + pd.offsets.MonthEnd(0)).to_pydatetime()

dates = pd.date_range(start=first_day, end=last_day)
schedule = pd.DataFrame(index=[emp["name"] for emp in employees], columns=dates)

if st.sidebar.button("✨ 產生排班表"):
    total_hours, schedule = assign_shifts(schedule, dates, first_day)
    schedule['總工時'] = total_hours

    st.subheader("📝 排班結果")
    st.dataframe(schedule)

    @st.cache_data
    def convert_df(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=True)
        return output.getvalue()

    excel_data = convert_df(schedule)
    st.download_button(
        label="📥 下載排班表（Excel）",
        data=excel_data,
        file_name=f"{selected_year}-{selected_month:02d}-排班表.xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
else:
    st.info("請從左側設定年份與月份後，點擊產生排班表！")