import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Mock Test Insights Engine", layout="wide")

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose Page", ["Dashboard", "Student Analysis", "Insights"])

# --- Main Title ---
st.title("📊 Automated Mock Test Insights Engine")
st.write("Analyze mock test results and discover your strengths and weaknesses.")

# --- File Upload (always on top) ---
uploaded_file = st.file_uploader("Upload Mock Test Dataset", type=["csv"])

if uploaded_file is None:
    st.info("Upload a CSV dataset to start analysis.")
    st.stop()

# --- Load and Clean Data ---
df = pd.read_csv(uploaded_file)
df.columns = df.columns.str.strip()

# Make numeric columns safe
for col in ["Total Questions", "Correct", "Wrong", "Unattempted"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# Recalculate correctly
df["Attempted"] = df["Correct"] + df["Wrong"]
df["Score Percentage"] = df["Correct"] / df["Total Questions"].replace(0, pd.NA) * 100
df["Score Percentage"] = df["Score Percentage"].fillna(0)
df["Accuracy"] = df["Correct"] / df["Attempted"].replace(0, pd.NA) * 100
df["Accuracy"] = df["Accuracy"].fillna(0)

# ================= DASHBOARD =================
if page == "Dashboard":
    st.header("Performance Dashboard")

    total_students = df["Student"].nunique()
    avg_score = df["Score Percentage"].mean()
    avg_accuracy = df["Accuracy"].mean()
    total_questions = int(df["Total Questions"].sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students", total_students)
    c2.metric("Average Score", f"{avg_score:.1f}%")
    c3.metric("Average Accuracy", f"{avg_accuracy:.1f}%")
    c4.metric("Total Questions", total_questions)

    # FIX 1: Use AVERAGE, not sum
    st.subheader("Subject Performance")
    subject_avg = df.groupby("Subject", as_index=False)["Score Percentage"].mean()
    fig_bar = px.bar(subject_avg, x="Subject", y="Score Percentage", color="Subject",
                     title="Average Subject-wise Score")
    fig_bar.update_yaxes(range=[0, 100])
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Answer Distribution")
    total_correct = int(df["Correct"].sum())
    total_wrong = int(df["Wrong"].sum())
    total_unattempted = int(df["Unattempted"].sum())
    pie_df = pd.DataFrame({
        "Status": ["Correct", "Wrong", "Unattempted"],
        "Count": [total_correct, total_wrong, total_unattempted]
    })
    fig_pie = px.pie(pie_df, names="Status", values="Count",
                     title="Question Answer Distribution")
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Dataset")
    st.dataframe(df, use_container_width=True)
    st.download_button("Download Results", df.to_csv(index=False), "mock_test_results.csv", "text/csv")

# ================= STUDENT ANALYSIS =================
elif page == "Student Analysis":
    st.header("Individual Student Analysis")

    students = sorted(df["Student"].unique())
    selected = st.selectbox("Select Student", students)
    sdf = df[df["Student"] == selected]

    st.write(f"Student Name: {selected}")
    st.metric("Average Score", f"{sdf['Score Percentage'].mean():.2f}%")
    st.metric("Accuracy", f"{sdf['Accuracy'].mean():.2f}%")

    # FIX 2: This is the main fix - group by Subject and take mean
    st.subheader(f"{selected}'s Subject Performance")
    student_subject_avg = sdf.groupby("Subject", as_index=False)["Score Percentage"].mean()
    fig_student = px.bar(student_subject_avg, x="Subject", y="Score Percentage", color="Subject")
    fig_student.update_yaxes(range=[0, 100])
    st.plotly_chart(fig_student, use_container_width=True)

    st.dataframe(sdf, use_container_width=True)
    st.download_button("Download Results", sdf.to_csv(index=False), f"{selected}_results.csv", "text/csv")

# ================= INSIGHTS =================
else:
    st.header("Insights & Recommendations")

    subject_avg = df.groupby("Subject", as_index=False)["Score Percentage"].mean()
    strongest = subject_avg.loc[subject_avg["Score Percentage"].idxmax()]
    weakest = subject_avg.loc[subject_avg["Score Percentage"].idxmin()]

    avg_accuracy = df["Accuracy"].mean()
    completion_rate = df["Attempted"].sum() / df["Total Questions"].sum() * 100

    if avg_accuracy >= 85:
        st.success(f"Excellent accuracy: {avg_accuracy:.1f}%. Keep it up!")
    elif avg_accuracy >= 75:
        st.info("Good accuracy. Focus on improving speed.")
    else:
        st.warning(f"Accuracy is {avg_accuracy:.1f}%. Focus on accuracy first.")

    if completion_rate >= 90:
        st.success(f"Excellent completion rate: {completion_rate:.1f}%.")
    elif completion_rate >= 80:
        st.success("Good question completion rate.")
    else:
        st.warning(f"Completion rate is low: {completion_rate:.1f}%. Practice time management.")

    st.success(f"Strongest Subject: {strongest['Subject']}")
    st.warning(f"Weakest Subject: {weakest['Subject']}")

    st.subheader("Recommendations")
    st.write(f"Focus more on {weakest['Subject']} to improve your overall performance.")
    st.write(f"Maintain your performance in {strongest['Subject']}.")
    st.write("Practice timed mock tests regularly.")

    st.download_button("Download Results", df.to_csv(index=False), "mock_test_results.csv", "text/csv")
