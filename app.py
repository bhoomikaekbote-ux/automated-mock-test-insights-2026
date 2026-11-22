import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Mock Test Insights Engine",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Automated Mock Test Insights Engine")
st.write("Analyze mock test results and discover your strengths and weaknesses.")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choose Page",
    ["Dashboard", "Student Analysis", "Insights"]
)

uploaded_file = st.file_uploader(
    "Upload Mock Test Dataset",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    required_columns = [
        "Student", "Test", "Subject",
        "Total Questions", "Correct",
        "Wrong", "Unattempted", "Time (min)"
    ]

    if all(column in df.columns for column in required_columns):

        df["Attempted"] = df["Correct"] + df["Wrong"]

        df["Accuracy"] = (
            df["Correct"] /
            df["Attempted"].replace(0, 1)
        ) * 100

        df["Score Percentage"] = (
            df["Correct"] /
            df["Total Questions"].replace(0, 1)
        ) * 100

        df["Completion Rate"] = (
            df["Attempted"] /
            df["Total Questions"].replace(0, 1)
        ) * 100

        if page == "Dashboard":

            st.header("Performance Dashboard")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Students",
                df["Student"].nunique()
            )

            col2.metric(
                "Average Score",
                f"{df['Score Percentage'].mean():.1f}%"
            )

            col3.metric(
                "Average Accuracy",
                f"{df['Accuracy'].mean():.1f}%"
            )

            col4.metric(
                "Total Questions",
                int(df["Total Questions"].sum())
            )

            st.subheader("Subject Performance")

            subject_data = df.groupby(
                "Subject"
            )["Score Percentage"].mean().reset_index()

            fig = px.bar(
                subject_data,
                x="Subject",
                y="Score Percentage",
                color="Subject",
                title="Average Subject-wise Score"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Answer Distribution")

            answers = pd.DataFrame({
                "Answer Type": ["Correct", "Wrong", "Unattempted"],
                "Count": [
                    df["Correct"].sum(),
                    df["Wrong"].sum(),
                    df["Unattempted"].sum()
                ]
            })

            fig2 = px.pie(
                answers,
                names="Answer Type",
                values="Count",
                title="Question Answer Distribution"
            )

            st.plotly_chart(fig2, use_container_width=True)

            st.subheader("Dataset")

            st.dataframe(df, use_container_width=True)

        elif page == "Student Analysis":

            st.header("Individual Student Analysis")

            student = st.selectbox(
                "Select Student",
                df["Student"].unique()
            )

            student_df = df[df["Student"] == student]

            st.write("Student Name:", student)

            st.metric(
                "Average Score",
                f"{student_df['Score Percentage'].mean():.2f}%"
            )

            st.metric(
                "Accuracy",
                f"{student_df['Accuracy'].mean():.2f}%"
            )

            fig = px.bar(
                student_df,
                x="Subject",
                y="Score Percentage",
                color="Subject",
                title=f"{student}'s Subject Performance"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(student_df)

        elif page == "Insights":

            st.header("Automated Performance Insights")

            accuracy = df["Accuracy"].mean()
            completion = df["Completion Rate"].mean()

            if accuracy >= 90:
                st.success("Excellent accuracy! Keep practicing.")
            elif accuracy >= 75:
                st.info("Good accuracy. Focus on improving speed.")
            else:
                st.warning("Accuracy needs improvement.")

            if completion < 70:
                st.warning(
                    "You are leaving many questions unattempted. "
                    "Practice time management."
                )
            else:
                st.success("Good question completion rate.")

            subject_scores = df.groupby(
                "Subject"
            )["Score Percentage"].mean()

            strongest = subject_scores.idxmax()
            weakest = subject_scores.idxmin()

            st.success(f"Strongest Subject: {strongest}")
            st.warning(f"Weakest Subject: {weakest}")

            st.subheader("Recommendations")

            st.write(
                f"Focus more on {weakest} to improve your overall performance."
            )

            st.write(
                f"Maintain your performance in {strongest}."
            )

            st.write(
                "Practice timed mock tests regularly."
            )

        st.download_button(
            "Download Results",
            df.to_csv(index=False),
            file_name="mock_test_analysis.csv",
            mime="text/csv"
        )

    else:

        st.error(
            "Dataset columns are incorrect. "
            "Please upload the correct dataset."
        )

else:

    st.info("Upload a CSV dataset to start analysis.")