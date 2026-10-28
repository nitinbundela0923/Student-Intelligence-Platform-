import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from report_card import (create_report_card,row_to_student_data,SUBJECT_COLS)
from report_card import (create_report_card,row_to_student_data,SUBJECT_COLS)
import os
import zipfile
from sports_report_card import generate_sports_report
# ==========================
# SESSION STATE
# ==========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ==========================
# LOGIN PAGE
# ==========================
def login_page():

    
    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.subheader("🔐 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):

            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.rerun()

            elif username == "teacher" and password == "teacher123":
                st.session_state.logged_in = True
                st.session_state.role = "teacher"
                st.rerun()

            elif username == "sports" and password == "sports123":
                st.session_state.logged_in = True
                st.session_state.role = "sports"
                st.rerun()

            else:
                st.error("Invalid Username or Password")


# ==========================
# DASHBOARD
# ==========================
def dashboard():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATASETS = {
        "Class 9": os.path.join(BASE_DIR, "corrected_csvs/Class_9.csv"),
        "Class 10": os.path.join(BASE_DIR, "corrected_csvs/Class_10.csv"),
        "Class 11 PCM": os.path.join(BASE_DIR, "corrected_csvs/Class_11_PCM.csv"),
        "Class 11 PCB": os.path.join(BASE_DIR, "corrected_csvs/Class_11_PCB.csv"),
        "Class 11 Commerce": os.path.join(BASE_DIR, "corrected_csvs/Class_11_Commerce.csv"),
        "Class 12 PCM": os.path.join(BASE_DIR, "corrected_csvs/Class_12_PCM.csv"),
        "Class 12 PCB": os.path.join(BASE_DIR, "corrected_csvs/Class_12_PCB.csv"),
        "Class 12 Commerce": os.path.join(BASE_DIR, "corrected_csvs/Class_12_Commerce.csv")
    }

    all_data = []

    for class_name, file_path in DATASETS.items():

        try:
            temp = pd.read_csv(file_path)
            temp["Class"] = class_name
            all_data.append(temp)

        except Exception:
            pass

    if not all_data:
        st.error("No dataset files found.")
        st.stop()

    school_df = pd.concat(all_data, ignore_index=True)

    st.sidebar.title("🎓 Dashboard Menu")

    selected_class = st.sidebar.selectbox(
        "Select Class",
        ["School Overview"] + list(DATASETS.keys()),
        key="class_selector"
    )
    
    if st.session_state.role == "admin":

        st.sidebar.markdown("## Upload Dataset")

        uploaded_file = st.sidebar.file_uploader(
            "Upload CSV",
            type="csv"
        )

        if uploaded_file:

            save_path = DATASETS[selected_class]

            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
    
    if selected_class == "School Overview":
        df = school_df.copy()
    else:
        df = pd.read_csv(DATASETS[selected_class])
        df["Class"] = selected_class
    # ==========================================
    # 📄 Sidebar - Generate Report Cards
    # ==========================================

    if st.session_state.role == "admin":

        st.sidebar.markdown("---")
        st.sidebar.subheader(" Report Cards")

        if st.sidebar.button(" Generate & Download All Report Cards"):

            os.makedirs("Report_Cards", exist_ok=True)

            progress = st.sidebar.progress(0)

            total = len(df)

            class_key = selected_class.replace(" ", "_")

            if class_key == "School_Overview":
                class_key = None

            for i, (_, row) in enumerate(df.iterrows()):

                # Determine subject list
                if class_key is None:
                    current_key = row["Class"].replace(" ", "_")
                else:
                    current_key = class_key

                student_data = row_to_student_data(
                    row,
                    SUBJECT_COLS[current_key]
                )

                pdf = create_report_card(student_data)

                filename = os.path.join(
                    "Report_Cards",
                    f"{row['Student_Name']}.pdf"
                )

                with open(filename, "wb") as f:
                    f.write(pdf.getvalue())

                progress.progress((i + 1) / total)

            # Create ZIP
            zip_path = "Report_Cards.zip"

            with zipfile.ZipFile(zip_path, "w") as zipf:
                for file in os.listdir("Report_Cards"):
                    zipf.write(
                        os.path.join("Report_Cards", file),
                        arcname=file
                    )

            st.sidebar.success("✅ All Report Cards Generated")

            with open(zip_path, "rb") as f:
                st.sidebar.download_button(
                    "⬇ Download All Report Cards",
                    data=f,
                    file_name="Report_Cards.zip",
                    mime="application/zip",
                    use_container_width=True
                )
    if st.session_state.role == "teacher":

        st.sidebar.markdown("---")
        st.sidebar.subheader(" Report Cards")

        if st.sidebar.button(" Generate & Download All Report Cards"):

            os.makedirs("Report_Cards", exist_ok=True)

            progress = st.sidebar.progress(0)

            total = len(df)

            class_key = selected_class.replace(" ", "_")

            if class_key == "School_Overview":
                class_key = None

            for i, (_, row) in enumerate(df.iterrows()):

                # Determine subject list
                if class_key is None:
                    current_key = row["Class"].replace(" ", "_")
                else:
                    current_key = class_key

                student_data = row_to_student_data(
                    row,
                    SUBJECT_COLS[current_key]
                )

                pdf = create_report_card(student_data)

                filename = os.path.join(
                    "Report_Cards",
                    f"{row['Student_Name']}.pdf"
                )

                with open(filename, "wb") as f:
                    f.write(pdf.getvalue())

                progress.progress((i + 1) / total)

            # Create ZIP
            zip_path = "Report_Cards.zip"

            with zipfile.ZipFile(zip_path, "w") as zipf:
                for file in os.listdir("Report_Cards"):
                    zipf.write(
                        os.path.join("Report_Cards", file),
                        arcname=file
                    )

            st.sidebar.success("✅ All Report Cards Generated")

            with open(zip_path, "rb") as f:
                st.sidebar.download_button(
                    "⬇ Download All Report Cards",
                    data=f,
                    file_name="Report_Cards.zip",
                    mime="application/zip",
                    use_container_width=True
                )
    # Filters
    gender_filter = st.sidebar.multiselect(
        "Gender",
        df["Gender"].unique(),
        default=df["Gender"].unique()
    )

    section_filter = st.sidebar.multiselect(
        "Section",
        df["Section"].unique(),
        default=df["Section"].unique()
    )

    sports_filter = st.sidebar.multiselect(
        "Sports Participation",
        df["Sports_Participation"].unique(),
        default=df["Sports_Participation"].unique()
    )

    df = df[
        (df["Gender"].isin(gender_filter))
        & (df["Section"].isin(section_filter))
        & (df["Sports_Participation"].isin(sports_filter))
    ]

    st.set_page_config(
    page_title="School Student Analytics Dashboard",
    page_icon="🎓",
    layout="wide"
    )
    st.markdown("""
    <div style="
    background: linear-gradient(135deg,#00B4FF,#7C3AED);
    padding:35px;
    border-radius:25px;
    text-align:center;
    box-shadow:0 10px 30px rgba(0,0,0,0.3);
    margin-bottom:20px;
    ">
    <h1 style="
    color:white;
    font-size:48px;
    font-weight:800;
    margin-bottom:5px;
    ">
    🎓 Student Intelligence Platform
    </h1>

    <p style="
    color:#CBD5E1;
    font-size:18px;
    ">
    Academic • Attendance • Sports • Career Analytics • Risk Detection
    </p>
    </div>
    """, unsafe_allow_html=True)
    # KPI Cards
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Students", len(df))
    c2.metric("Average Percentage", f"{df['Percentage'].mean():.2f}%")
    c3.metric("Attendance", f"{df['Attendance_Percentage'].mean():.2f}%")
    c4.metric(
        "Sports %",
        f"{((df['Sports_Participation']=='Yes').mean()*100):.1f}%"
    )
    if st.session_state.role == "admin":
        st.info("Logged in as Admin")
        # =====================
        # Class Comparison
        # =====================
        col1, col2 = st.columns([4, 2])
        if selected_class == "School Overview":
            with col1:

                avg_marks = (
                    school_df.groupby("Class")["Percentage"]
                    .mean()
                    .reset_index()
                    .sort_values(by="Percentage", ascending=False)
                )

                fig = px.bar(
                    avg_marks,
                    x="Class",
                    y="Percentage",
                    text=avg_marks["Percentage"].round(1),
                    color="Percentage",
                    color_continuous_scale="Blues",  # Same as Section Chart
                    title="Average Class Percentage"
                )

                fig.update_traces(
                    textposition="outside"
                )

                fig.update_layout(
                    title={
                        "text": "Average Class Percentage",
                        "x": 0.5,
                        "xanchor": "center",
                        "font": dict(
                            size=35,
                            family="Arial Black"
                        )
                    },
                    template="plotly_dark",
                    height=450,
                    coloraxis_showscale=False,
                    hovermode="x unified"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )
        elif selected_class != "School Overview":
            with col1:

                section_avg = (
                    df.groupby("Section")["Percentage"]
                    .mean()
                    .reset_index()
                    .sort_values(by="Percentage", ascending=False)
                )

                fig = px.bar(
                    section_avg,
                    x="Section",
                    y="Percentage",
                    text=section_avg["Percentage"].round(1),
                    title="Average Percentage by Section",
                    color="Percentage",
                    color_continuous_scale="Blues"
                )

                fig.update_traces(
                    textposition="outside"
                )

                fig.update_layout(
                    title={
                        "text": "Average Percentage by Section",
                        "x": 0.5,
                        "xanchor": "center",
                        "font": dict(
                            size=35,
                            family="Arial Black",
                            color="white"
                        )
                    },
                    xaxis_title="Section",
                    yaxis_title="Average Percentage (%)",
                    height=500,
                    showlegend=False
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )
        # =====================
        # Top 10 Toppers
        # =====================
        with col2:

            st.markdown(
                """
                <h2 style="
                    text-align:left;
                    color:#ffffff;
                    font-size:25px;
                    font-family:Arial Black;
                    font-weight:bold;
                ">
                Top 10 Class Toppers
                </h2>
                """,
                unsafe_allow_html=True
            )

            top_students = (
                df.sort_values(
                    by="Percentage",
                    ascending=False
                )
                .head(10)
                .reset_index(drop=True)
            )

            medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]

            top_students["Rank"] = medals

            top_students = top_students[
                [
                    "Rank",
                    "Student_Name",
                    "Percentage"
                ]
            ]

            st.dataframe(
                top_students,
                use_container_width=True,
                height=420,
                hide_index=True
            )

        # =====================
        # Attendance Trend
        # =====================
        if selected_class == "School Overview":
            attendance_trend = (
            school_df.groupby("Class")["Attendance_Percentage"]
            .mean()
            .reset_index()
            .sort_values(
                by="Attendance_Percentage",
                ascending=True
            )
        )

            fig = px.bar(
                attendance_trend,
                x="Attendance_Percentage",
                y="Class",
                orientation="h",
                text=attendance_trend["Attendance_Percentage"].round(1),
                color="Attendance_Percentage",
                color_continuous_scale=[
                    "#D6F9FF",
                    "#A5F3FC",
                    "#67E8F9",
                    "#22D3EE",
                    "#06B6D4",
                    "#0891B2"
                ],
                title=" Average Attendance by Class"
            )

            fig.update_traces(
                textposition="outside",
                marker_line_color="white",
                marker_line_width=1.5
            )

            fig.update_layout(
                title={
                    "text": "Average Attendance by Class",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": dict(
                        size=35,
                        family="Arial Black",
                        color="white"
                    )
                },
                template="plotly_dark",
                height=650,
                xaxis_title="Average Attendance (%)",
                yaxis_title="Class",
                coloraxis_showscale=False,
                hovermode="y unified",

                # Transparent background
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",

                font=dict(
                    color="white",
                    size=14
                ),
                margin=dict(
                    l=20,
                    r=20,
                    t=70,
                    b=20
                )
            )

            fig.update_xaxes(
                showgrid=False,
                zeroline=False
            )

            fig.update_yaxes(
                showgrid=False,
                zeroline=False
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
        elif selected_class != "School Overview":
            filtered_section_df = df[
                df["Class"] == selected_class
            ]

            section_counts = (
                filtered_section_df["Section"]
                .value_counts()
                .reset_index()
            )

            section_counts.columns = ["Section", "Students"]

            fig = px.bar(
                section_counts,
                x="Students",
                y="Section",
                orientation="h",
                text="Students",
                color="Students",
                color_continuous_scale="Blues",
                title=f" Students by Section - {selected_class}"
            )

            fig.update_traces(
                textposition="outside"
            )
            fig.update_layout(
                title={
                    "text": f"Students by Section - {selected_class}",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": dict(
                        size=35,
                        family="Arial Black"
                    )
                },
                template="plotly_dark",
                height=650,
                xaxis_title="Number of Students",
                yaxis_title="Section",
                coloraxis_showscale=False,
                hovermode="y unified",
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # ==========================================
        # Subject Selection
        # ==========================================
        # ----------------------------------------
        # Subject list
        # ----------------------------------------

        if selected_class == "School Overview":

            subjects = [
                "Maths_Marks",
                "Science_Marks",
                "SocialScience_Marks",
                "Computer_Marks",
                "Physics_Marks",
                "Chemistry_Marks",
                "Biology_Marks",
                "Business_Marks",
                "Accountancy_Marks",
                "Economics_Marks",
                "English_Marks",
                "Hindi_Marks"
            ]

        elif selected_class in ["Class 9","Class 10"]:

            subjects = [
                "Maths_Marks",
                "Science_Marks",
                "SocialScience_Marks",
                "English_Marks",
                "Computer_Marks",
                "Hindi_Marks"
            ]

        elif selected_class in ["Class 11 PCM","Class 12 PCM"]:

            subjects = [
                "Maths_Marks",
                "Physics_Marks",
                "Chemistry_Marks",
                "English_Marks",
                "Physical_Education_Marks",
                "Hindi_Marks"
            ]

        elif selected_class in ["Class 11 PCB","Class 12 PCB"]:

            subjects = [
                "Biology_Marks",
                "Physics_Marks",
                "Chemistry_Marks",
                "English_Marks",
                "Physical_Education_Marks",
                "Hindi_Marks"
            ]

        else:

            subjects = [
                "Business_Marks",
                "Accountancy_Marks",
                "Economics_Marks",
                "English_Marks",
                "Physical_Education_Marks",
                "Hindi_Marks"
            ]

        subjects = [s for s in subjects if s in df.columns]

        # ----------------------------------------
        # School Average
        # ----------------------------------------

        school_avg = []

        for subject in subjects:
            school_avg.append(
                school_df[subject].dropna().mean()
            )

        # ----------------------------------------
        # Selected Class Average
        # ----------------------------------------

        class_avg = []

        for subject in subjects:

            if subject in df.columns:

                class_avg.append(
                    df[subject].dropna().mean()
                )

            else:

                class_avg.append(None)

        labels = [
            s.replace("_Marks","")
            .replace("_"," ")
            for s in subjects
        ]

        # Close Radar

        labels += [labels[0]]
        school_avg += [school_avg[0]]
        class_avg += [class_avg[0]]

        # ----------------------------------------
        # Radar Chart
        # ----------------------------------------

        fig = go.Figure()

        # School Average

        fig.add_trace(
            go.Scatterpolar(
                r=school_avg,
                theta=labels,
                fill="toself",
                name="School Average",
                line=dict(
                    color="#00E396",
                    width=3
                ),
                fillcolor="rgba(0,227,150,0.25)"
            )
        )

        # Selected Class

        if selected_class != "School Overview":

            fig.add_trace(
                go.Scatterpolar(
                    r=class_avg,
                    theta=labels,
                    fill="toself",
                    name=selected_class,
                    line=dict(
                        color="#00B9E8",
                        width=4
                    ),
                    fillcolor="rgba(0,185,232,0.35)"
                )
            )

        fig.update_layout(

            title=dict(
                text=f"Subject Performance Radar ({selected_class})",
                x=0.1,
                font=dict(
                    size=30,
                    family="Arial Black"
                )
            ),

            polar=dict(

                bgcolor="rgba(0,0,0,0)",

                radialaxis=dict(
                    visible=True,
                    range=[0,100],
                    tickfont=dict(size=13),
                    gridcolor="gray"
                ),

                angularaxis=dict(
                    tickfont=dict(
                        size=14,
                        color="white"
                    )
                )

            ),

            template="plotly_dark",

            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            legend=dict(
                orientation="h",
                y=1.12,
                x=0.5
            ),

            height=650
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
        col1, col2 = st.columns([4, 2])
        with col1:
            # ==========================================
            # 👨‍🎓 Student Type Distribution
            # ==========================================
            # ------------------------------------------
            # Create Student Category
            # ------------------------------------------

            temp_df = df.copy()

            temp_df["Student_Category"] = (
                temp_df["Student_Type"] + " - " + temp_df["Gender"]
            )

            # ------------------------------------------
            # Count Students
            # ------------------------------------------

            count_df = (
                temp_df.groupby("Student_Category")
                .size()
                .reset_index(name="Students")
            )

            # Keep order fixed
            order = [
                "Day Scholar - Male",
                "Day Scholar - Female",
                "Hosteler - Male",
                "Hosteler - Female"
            ]

            count_df["Student_Category"] = pd.Categorical(
                count_df["Student_Category"],
                categories=order,
                ordered=True
            )

            count_df = count_df.sort_values("Student_Category")

            # ------------------------------------------
            # Plot
            # ------------------------------------------

            fig = px.bar(

                count_df,

                x="Student_Category",
                y="Students",

                text="Students",

                color="Student_Category",

                color_discrete_map={

                    "Day Scholar - Male": "#00B9E8",
                    "Day Scholar - Female": "#66D9FF",

                    "Hosteler - Male": "#00E396",
                    "Hosteler - Female": "#7DFFB3"

                }

            )

            fig.update_traces(

                textposition="outside",

                marker_line_color="white",
                marker_line_width=2,

                width=0.55

            )

            fig.update_layout(

                title=dict(

                    text=f" Student Distribution ({selected_class})",

                    x=0.5,

                    xanchor="center",

                    font=dict(
                        size=30,
                        family="Arial Black",
                        color="white"
                    )

                ),

                template="plotly_dark",

                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",

                height=550,

                xaxis_title="Student Category",
                yaxis_title="Number of Students",

                showlegend=False,

                font=dict(
                    color="white",
                    size=14
                ),

                margin=dict(
                    l=20,
                    r=20,
                    t=70,
                    b=20
                )

            )

            fig.update_yaxes(

                showgrid=True,
                gridcolor="rgba(255,255,255,0.10)",
                zeroline=False

            )

            fig.update_xaxes(showgrid=False)

            st.plotly_chart(
                fig,
                use_container_width=True
            )
        with col2:
            # ==========================================
            # 👥 Gender Distribution
            # ==========================================
            # Count Gender
            gender_df = (
                df.groupby("Gender")
                .size()
                .reset_index(name="Students")
            )

            fig = px.pie(

                gender_df,

                names="Gender",

                values="Students",

                hole=0.55,

                color="Gender",

                color_discrete_map={

                    "Male": "#00B9E8",
                    "Female": "#FF5E7E"

                }

            )

            fig.update_traces(

                textposition="inside",

                textinfo="percent+label",

                textfont=dict(
                    size=16,
                    color="white"
                ),

                marker=dict(
                    line=dict(
                        color="white",
                        width=2
                    )
                ),

                pull=[0.04, 0.04],

                hovertemplate=
                "<b>%{label}</b><br>" +
                "Students: %{value}<br>" +
                "Percentage: %{percent}<extra></extra>"

            )

            fig.update_layout(

                title=dict(

                    text=f" Gender Distribution",

                    x=0.0,

                    font=dict(
                        size=30,
                        family="Arial Black",
                        color="white"
                    )

                ),

                template="plotly_dark",

                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",

                showlegend=True,

                legend=dict(

                    orientation="h",

                    x=0.35,

                    y=1.08,

                    font=dict(size=14)

                ),

                height=550,

                margin=dict(
                    l=20,
                    r=20,
                    t=70,
                    b=20
                )

            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # ==========================================
        # 🏠 Hostel Distribution - Lollipop Chart
        # ==========================================
        # Only hostel students
        hostel_df = df[df["Student_Type"] == "Hosteler"]

        # Count students in each hostel
        hostel_count = (
            hostel_df.groupby("Hostel_Name")
            .size()
            .reset_index(name="Students")
            .sort_values("Students", ascending=True)
        )

        fig = go.Figure()

        # ------------------------------------------
        # Draw one line for each hostel
        # ------------------------------------------

        for _, row in hostel_count.iterrows():

            fig.add_shape(
                type="line",
                x0=0,
                x1=row["Students"],
                y0=row["Hostel_Name"],
                y1=row["Hostel_Name"],
                line=dict(
                    color="#00B9E8",
                    width=5
                )
            )

        # ------------------------------------------
        # Draw lollipop heads
        # ------------------------------------------

        fig.add_trace(

            go.Scatter(

                x=hostel_count["Students"],
                y=hostel_count["Hostel_Name"],

                mode="markers+text",

                marker=dict(
                    size=20,
                    color="#00E396",
                    line=dict(
                        color="white",
                        width=2
                    )
                ),

                text=hostel_count["Students"],
                textposition="middle right",

                textfont=dict(
                    size=15,
                    color="white"
                ),

                hovertemplate=
                "<b>%{y}</b><br>" +
                "Students : %{x}<extra></extra>",

                showlegend=False

            )

        )

        # ------------------------------------------
        # Layout
        # ------------------------------------------

        fig.update_layout(

            title=dict(

                text=f" Hostel Distribution ({selected_class})",

                x=0.2,

                font=dict(
                    size=30,
                    family="Arial Black",
                    color="white"
                )

            ),

            template="plotly_dark",

            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            height=600,

            xaxis_title="Number of Students",
            yaxis_title="Hostel Name",

            font=dict(
                color="white",
                size=14
            ),

            margin=dict(
                l=30,
                r=30,
                t=70,
                b=30
            )

        )

        fig.update_xaxes(

            showgrid=True,

            gridcolor="rgba(255,255,255,0.10)",

            zeroline=False

        )

        fig.update_yaxes(

            showgrid=False,

            categoryorder="total ascending"

        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # Remove duplicate columns (safe for Plotly)
        df = df.loc[:, ~df.columns.duplicated()]

            # Check if the column exists
        if "Study_Hours_Per_Day" in df.columns:

                fig = px.histogram(

                    df,

                    x="Study_Hours_Per_Day",

                    nbins=10,

                    color_discrete_sequence=["#00B9E8"],

                    text_auto=True

                )

                fig.update_traces(

                    marker=dict(

                        line=dict(
                            color="white",
                            width=1.5
                        )

                    ),

                    opacity=0.9

                )

                fig.update_layout(

                    title=dict(

                        text=f"📚 Study Hours Distribution ({selected_class})",

                        x=0.5,

                        xanchor="center",

                        font=dict(
                            size=30,
                            family="Arial Black",
                            color="white"
                        )

                    ),

                    template="plotly_dark",

                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",

                    height=600,

                    xaxis_title="Study Hours Per Day",

                    yaxis_title="Number of Students",

                    bargap=0.08,

                    showlegend=False,

                    font=dict(
                        color="white",
                        size=14
                    ),

                    margin=dict(
                        l=20,
                        r=20,
                        t=70,
                        b=20
                    )

                )

                fig.update_xaxes(

                    showgrid=False,

                    zeroline=False

                )

                fig.update_yaxes(

                    showgrid=True,

                    gridcolor="rgba(255,255,255,0.10)",

                    zeroline=False

                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        else:
            st.warning("Study_Hours_Per_Day column not found.")


        #==========================================
        # 🎯 Career Goal Distribution
        #==========================================
        if "Career_Goal" in df.columns:

            career_df = (
                df["Career_Goal"]
                .value_counts()
                .reset_index()
            )

            career_df.columns = ["Career Goal", "Students"]

            fig = px.bar(

                career_df,

                x="Career Goal",
                y="Students",

                text="Students",

                color="Students",

                color_continuous_scale="Blues"

            )

            fig.update_traces(
                textposition="outside",
                marker_line_color="white",
                marker_line_width=2
            )

            fig.update_layout(

                title=dict(
                    text=" Career Goal Distribution",
                    x=0.3,
                    font=dict(
                        size=28,
                        family="Arial Black"
                    )
                ),

                template="plotly_dark",

                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",

                coloraxis_showscale=False,

                height=500,

                showlegend=False

            )

            st.plotly_chart(fig, use_container_width=True)
        #------------------------------
        # Insights Panel
        #------------------------------
        st.markdown("## 🤖 Insights Panel")

        with st.container(border=True):

            # School Average
            avg_percentage = df["Percentage"].mean()

            # Highest Percentage
            highest_percentage = df["Percentage"].max()

            # Top Student
            if "Student_Name" in df.columns:
                topper = df.loc[
                    df["Percentage"].idxmax(),
                    "Student_Name"
                ]
            elif "Name" in df.columns:
                topper = df.loc[
                    df["Percentage"].idxmax(),
                    "Name"
                ]
            else:
                topper = "Top Student"

            # Risk Students
            risk_students = len(
                df[df["Percentage"] < 40]
            )

            # Excellent Students
            excellent_students = len(
                df[df["Percentage"] >= 90]
            )

            # Average By Class
            class_avg = (
                df.groupby("Class")["Percentage"]
                .mean()
                .sort_values(ascending=False)
            )

            best_class = class_avg.index[0]
            best_class_avg = class_avg.iloc[0]

            lowest_class = class_avg.index[-1]
            lowest_class_avg = class_avg.iloc[-1]

            # Performance Categories
            above_80 = len(df[df["Percentage"] >= 80])
            between_60_80 = len(
                df[
                    (df["Percentage"] >= 60)
                    & (df["Percentage"] < 80)
                ]
            )
            below_60 = len(df[df["Percentage"] < 60])

            # ======================================
            # INSIGHTS
            # ======================================

            st.success(
                f"📈Average Percentage: "
                f"{avg_percentage:.1f}%"
            )

            st.success(
                f"🏆 Best Performing Class: "
                f"{best_class} "
                f"({best_class_avg:.1f}%)"
            )

            st.warning(
                f"📉 Lowest Performing Class: "
                f"{lowest_class} "
                f"({lowest_class_avg:.1f}%)"
            )

            st.info(
                f"🥇Topper: "
                f"{topper} "
                f"({highest_percentage:.1f}%)"
            )

            st.success(
                f"🎯 Students Above 90%: "
                f"{excellent_students}"
            )

            st.error(
                f"⚠️ Students Below 40%: "
                f"{risk_students}"
            )

            st.markdown("---")

            st.markdown("### 📊 Performance Breakdown")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "🌟 Above 80%",
                    above_80
                )

            with col2:
                st.metric(
                    "📚 60-80%",
                    between_60_80
                )

            with col3:
                st.metric(
                    "⚠️ Below 60%",
                    below_60
                )

            st.markdown("---")
        cols = pd.Series(df.columns)
        # ------------------------------
        # Search Student Records
        # ------------------------------

        st.markdown("""
        <h2 style="
            color:white;
            font-size:25px;
            font-family:Arial Black;
            margin:0;">
        🔍 Student Search Engine
        </h2>
        """, unsafe_allow_html=True)

        search = st.text_input(
            "Search Student",
            placeholder="Type Student Name, Percentage, Subject Marks..."
        )

        # Default dataframe
        filtered_df = df.copy()

        # Search
        if search:

            mask = (
                filtered_df
                .astype(str)
                .apply(lambda col: col.str.contains(search, case=False, na=False))
                .any(axis=1)
            )

            filtered_df = filtered_df[mask]

            st.success(f"✅ {len(filtered_df)} Student(s) Found")

        # Dynamic dataframe height
        rows = len(filtered_df)

        table_height = min(450, max(70, (rows + 1) * 35))

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            height=table_height
        )
        # ------------------------------
        # Download Report Card
        # ------------------------------

        if len(filtered_df) == 1:

            row = filtered_df.iloc[0]

            class_key = selected_class.replace(" ", "_")

            if class_key == "School_Overview":
                class_key = row["Class"].replace(" ", "_")

            student_data = row_to_student_data(
                row,
                SUBJECT_COLS[class_key]
            )

            pdf = create_report_card(student_data)

            st.download_button(
                " Download Report Card",
                data=pdf,
                file_name=f"{row['Student_Name']}_Report_Card.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        # ------------------------------
        # Download CSV
        # ------------------------------

        csv = filtered_df.to_csv(index=False)

        st.download_button(
            "⬇ Download CSV",
            data=csv,
            file_name="students.csv",
            mime="text/csv",
            use_container_width=True
        )
    elif st.session_state.role == "sports":
        st.info("Logged in as Sports Teacher")
        if selected_class == "School Overview":
            # ==========================================
            # 🏅 Sports Participation by Class
            # ==========================================

            sports_class = (
                school_df[school_df["Sports_Participation"] == "Yes"]
                .groupby("Class")
                .size()
                .reset_index(name="Students")
                .sort_values("Students", ascending=False)
            )

            fig = px.bar(

                sports_class,

                x="Class",
                y="Students",

                text="Students",

                color="Students",

                color_continuous_scale=[
                    "#ECFDF5",
                    "#D1FAE5",
                    "#A7F3D0",
                    "#6EE7B7",
                    "#34D399",
                    "#10B981",
                    "#059669",
                    "#047857"
                ]

            )

            fig.update_traces(

                textposition="outside",

                marker_line_color="white",

                marker_line_width=2,

                width=0.6

            )

            fig.update_layout(

                title=dict(

                    text="Sports Participation by Class",

                    x=0.5,

                    xanchor="center",

                    font=dict(
                        size=30,
                        family="Arial Black",
                        color="white"
                    )

                ),

                template="plotly_dark",

                paper_bgcolor="rgba(0,0,0,0)",

                plot_bgcolor="rgba(0,0,0,0)",

                coloraxis_showscale=False,

                height=600,

                xaxis_title="Class",

                yaxis_title="Number of Sports Students",

                hovermode="x unified",

                font=dict(
                    color="white",
                    size=14
                ),

                margin=dict(
                    l=20,
                    r=20,
                    t=70,
                    b=20
                )

            )

            fig.update_xaxes(
                showgrid=False,
                zeroline=False
            )

            fig.update_yaxes(
                showgrid=True,
                gridcolor="rgba(255,255,255,0.10)",
                zeroline=False
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
        elif selected_class != "School Overview":
            # ==========================================
            # 🏅 Sports Participation by Section
            # ==========================================

            sports_section = (
                df[df["Sports_Participation"] == "Yes"]
                .groupby("Section")
                .size()
                .reset_index(name="Students")
                .sort_values("Students", ascending=False)
            )

            fig = px.bar(

                sports_section,

                x="Section",
                y="Students",

                text="Students",

                color="Students",

                color_continuous_scale=[
                    "#E8FFF1",
                    "#CCFFD9",
                    "#99FFB3",
                    "#66FF8F",
                    "#33E86B",
                    "#00C853",
                    "#00A844",
                    "#007E33",
                    "#005F26"
                ]

            )

            fig.update_traces(

                textposition="outside",

                marker_line_color="white",

                marker_line_width=2,

                width=0.6

            )

            fig.update_layout(

                title=dict(

                    text=f" Sports Participation by Section ({selected_class})",

                    x=0.5,

                    xanchor="center",

                    font=dict(
                        size=30,
                        family="Arial Black",
                        color="white"
                    )

                ),

                template="plotly_dark",

                paper_bgcolor="rgba(0,0,0,0)",

                plot_bgcolor="rgba(0,0,0,0)",

                coloraxis_showscale=False,

                height=550,

                xaxis_title="Section",

                yaxis_title="Number of Sports Students",

                hovermode="x unified",

                font=dict(
                    color="white",
                    size=14
                ),

                margin=dict(
                    l=20,
                    r=20,
                    t=70,
                    b=20
                )

            )

            fig.update_xaxes(
                showgrid=False,
                zeroline=False
            )

            fig.update_yaxes(
                showgrid=True,
                gridcolor="rgba(255,255,255,0.10)",
                zeroline=False
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
        # ==========================================
        # 🏅 Favorite Sports Distribution
        # ==========================================

        if "Favorite_Sport" in df.columns:

            sports_df = (
                df["Favorite_Sport"]
                .value_counts()
                .reset_index()
            )

            sports_df.columns = ["Sport", "Students"]

            fig = px.bar(

                sports_df,

                x="Students",
                y="Sport",

                orientation="h",

                text="Students",

                color="Students",

                color_continuous_scale=[
                    "#F7FEE7",
                    "#ECFCCB",
                    "#D9F99D",
                    "#BEF264",
                    "#A3E635",
                    "#84CC16",
                    "#65A30D",
                    "#4D7C0F",
                    "#365314"
                ]

            )

            fig.update_traces(

                textposition="outside",

                marker_line_color="white",
                marker_line_width=2

            )

            fig.update_layout(

                title=dict(

                    text=f" Favorite Sports Distribution ({selected_class})",

                    x=0.5,

                    xanchor="center",

                    font=dict(
                        size=30,
                        family="Arial Black",
                        color="white"
                    )

                ),

                template="plotly_dark",

                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",

                coloraxis_showscale=False,

                height=600,

                xaxis_title="Number of Students",

                yaxis_title="Favorite Sport",

                font=dict(
                    color="white",
                    size=14
                ),

                margin=dict(
                    l=20,
                    r=20,
                    t=70,
                    b=20
                )

            )

            fig.update_xaxes(

                showgrid=True,

                gridcolor="rgba(255,255,255,0.10)",

                zeroline=False

            )

            fig.update_yaxes(

                showgrid=False,

                categoryorder="total ascending"

            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.warning("Favorite_Sport column not found.")
        col1, col2 = st.columns([4, 2])
        with col1:
            # ==========================================
            # Male vs Female Sports Participants
            # ==========================================

            sports_df = df.copy()

            sports_df["Sports_Participation"] = (
                sports_df["Sports_Participation"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            sports_df = sports_df[
                sports_df["Sports_Participation"] == "yes"
            ]

            if sports_df.empty:

                st.warning("No Sports Participants Found.")

            else:

                if selected_class == "School Overview":

                    sports_gender = (
                        sports_df
                        .groupby("Gender")
                        .size()
                        .reset_index(name="Students")
                    )

                    fig = px.bar(
                        sports_gender,
                        x="Gender",
                        y="Students",
                        text="Students",
                        color="Gender",
                        color_discrete_map={
                            "Male": "#00B9E8",
                            "Female": "#FF5E7E"
                        }
                    )

                    title = "Male vs Female Sports Participants"

                else:

                    sports_gender = (
                        sports_df
                        .groupby(["Section", "Gender"])
                        .size()
                        .reset_index(name="Students")
                    )

                    fig = px.bar(
                        sports_gender,
                        x="Section",
                        y="Students",
                        color="Gender",
                        barmode="group",
                        text="Students",
                        color_discrete_map={
                            "Male": "#00B9E8",
                            "Female": "#FF5E7E"
                        }
                    )

                    title = f"Male vs Female Sports Participants by Section"

                fig.update_traces(
                    textposition="outside",
                    marker_line_color="white",
                    marker_line_width=2
                )

                fig.update_layout(
                    title={
                        "text": title,
                        "x": 0.5,
                        "xanchor": "center",
                        "font": dict(
                            size=30,
                            family="Arial Black",
                            color="white"
                        )
                    },
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=550,
                    xaxis_title="Section" if selected_class != "School Overview" else "Gender",
                    yaxis_title="Number of Students",
                    font=dict(color="white", size=14)
                )

                st.plotly_chart(fig, use_container_width=True)
        with col2:
            sports_df = df.copy()

            sports_df["Sports_Participation"] = (
                sports_df["Sports_Participation"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            sports_df = sports_df[
                sports_df["Sports_Participation"] == "yes"
            ]

            if sports_df.empty:

                st.warning(f"No Sports Participants Found in {selected_class}")

            else:

                sports_gender = (
                    sports_df
                    .groupby("Gender")
                    .size()
                    .reset_index(name="Students")
                )

                fig = px.pie(
                    sports_gender,
                    names="Gender",
                    values="Students",
                    hole=0.60,
                    color="Gender",
                    color_discrete_map={
                        "Male": "#00B9E8",
                        "Female": "#FF5E7E"
                    }
                )

                fig.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    textfont=dict(
                        size=16,
                        color="white"
                    ),
                    marker=dict(
                        line=dict(
                            color="white",
                            width=2
                        )
                    ),
                    pull=[0.03, 0.03],
                    hovertemplate=
                    "<b>%{label}</b><br>" +
                    "Students: %{value}<br>" +
                    "Percentage: %{percent}<extra></extra>"
                )

                fig.update_layout(
                    title=dict(
                        text=f"Male vs  Female",
                        x=0.5,
                        xanchor="center",
                        font=dict(
                            size=30,
                            family="Arial Black",
                            color="white"
                        )
                    ),
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=550,
                    legend=dict(
                        orientation="h",
                        x=0.3,
                        y=1.08,
                        font=dict(size=14)
                    ),
                    margin=dict(
                        l=20,
                        r=20,
                        t=70,
                        b=20
                    )
                )

                st.plotly_chart(fig, use_container_width=True)
        # ==========================================
        # 📚 Study Hours & 🏃 Sports Hours Histogram
        # ==========================================


        sports_df = df.copy()

        sports_df["Sports_Participation"] = (
            sports_df["Sports_Participation"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        sports_df = sports_df[
            sports_df["Sports_Participation"] == "yes"
        ]

        required_columns = [
            "Study_Hours_Per_Day",
            "Sports_Hours_Per_Week"
        ]

        missing = [col for col in required_columns if col not in sports_df.columns]

        if sports_df.empty:

            st.warning("No Sports Participants Found.")

        elif missing:

            st.warning(f"Missing column(s): {', '.join(missing)}")

        else:

            # Change column ratio if needed
            col1, col2 = st.columns([1, 1], gap="large")

            # ==========================================
            # 📚 Study Hours Histogram
            # ==========================================

            with col1:

                fig1 = px.histogram(
                    sports_df,
                    x="Study_Hours_Per_Day",
                    nbins=10,
                    text_auto=True,
                    color_discrete_sequence=["#83E800"]
                )

                fig1.update_traces(
                    marker_line_color="white",
                    marker_line_width=1
                )

                fig1.update_layout(

                    width=600,          # Change Width Here
                    height=450,

                    title=dict(
                        text=" Study Hours",
                        x=0.5,
                        xanchor="center",
                        font=dict(
                            size=24,
                            family="Arial Black",
                            color="white"
                        )
                    ),

                    template="plotly_dark",

                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",

                    xaxis_title="Study Hours / Day",
                    yaxis_title="Number of Students",

                    showlegend=False,

                    margin=dict(
                        l=40,
                        r=40,
                        t=70,
                        b=40
                    )
                )

                st.plotly_chart(
                    fig1,
                    use_container_width=True
                )

            # ==========================================
            # Sports Hours Histogram
            # ==========================================

            with col2:

                fig2 = px.histogram(
                    sports_df,
                    x="Sports_Hours_Per_Week",
                    nbins=10,
                    text_auto=True,
                    color_discrete_sequence=["#5EFFC1"]
                )

                fig2.update_traces(
                    marker_line_color="white",
                    marker_line_width=1
                )

                fig2.update_layout(

                    width=600,          # Change Width Here
                    height=450,

                    title=dict(
                        text="Sports Hours",
                        x=0.5,
                        xanchor="center",
                        font=dict(
                            size=24,
                            family="Arial Black",
                            color="white"
                        )
                    ),

                    template="plotly_dark",

                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",

                    xaxis_title="Sports Hours / Week",
                    yaxis_title="Number of Students",

                    showlegend=False,

                    margin=dict(
                        l=40,
                        r=40,
                        t=70,
                        b=40
                    )
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )
        if selected_class == "School Overview":
            # ==========================================
            # 🎂 Age Distribution of Sports Students (Bar Chart)
            # ==========================================

            sports_df = df.copy()

            sports_df["Sports_Participation"] = (
                sports_df["Sports_Participation"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            sports_df = sports_df[
                sports_df["Sports_Participation"] == "yes"
            ]

            if sports_df.empty:

                st.warning("No Sports Participants Found.")

            elif "Age" not in sports_df.columns:

                st.warning("Age column not found.")

            else:

                # Convert Age to numeric
                sports_df["Age"] = pd.to_numeric(
                    sports_df["Age"],
                    errors="coerce"
                )

                sports_df = sports_df.dropna(subset=["Age"])

                # Count students by age
                age_df = (
                    sports_df.groupby("Age")
                    .size()
                    .reset_index(name="Students")
                    .sort_values("Age")
                )

                fig = px.bar(

                    age_df,

                    x="Age",
                    y="Students",

                    text="Students",

                    color="Students",

                    color_continuous_scale="Greens"

                )

                fig.update_traces(

                    textposition="outside",

                    marker_line_color="white",

                    marker_line_width=2

                )

                fig.update_layout(

                    title=dict(

                        text=f"🎂 Age Distribution of Sports Students ({selected_class})",

                        x=0.5,

                        xanchor="center",

                        font=dict(
                            size=30,
                            family="Arial Black",
                            color="white"
                        )

                    ),

                    template="plotly_dark",

                    paper_bgcolor="rgba(0,0,0,0)",

                    plot_bgcolor="rgba(0,0,0,0)",

                    height=550,

                    xaxis_title="Age (Years)",

                    yaxis_title="Number of Students",

                    coloraxis_showscale=False,

                    showlegend=False,

                    margin=dict(
                        l=20,
                        r=20,
                        t=70,
                        b=20
                    )

                )

                fig.update_xaxes(
                    dtick=1,
                    showgrid=False
                )

                fig.update_yaxes(
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.10)"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )
        col1, col2 = st.columns(2)
        with col1:
            # ==========================================
            # Hostel vs Day Scholar Sports Students
            # ==========================================

            sports_df = df.copy()

            # Keep only sports students
            sports_df["Sports_Participation"] = (
                sports_df["Sports_Participation"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            sports_df = sports_df[
                sports_df["Sports_Participation"] == "yes"
            ]

            if sports_df.empty:

                st.warning("No Sports Students Found.")

            else:

                hostel_df = (
                    sports_df
                    .groupby("Student_Type")
                    .size()
                    .reset_index(name="Students")
                )

                fig = px.pie(

                    hostel_df,

                    names="Student_Type",

                    values="Students",

                    hole=0.65,

                    color="Student_Type",

                    color_discrete_map={
                        "Hosteler": "#00FF3C",
                        "Day Scholar": "#68E8FF"
                    }

                )

                fig.update_traces(

                    textposition="inside",

                    textinfo="percent+label",

                    marker=dict(

                        line=dict(
                            color="white",
                            width=2
                        )

                    )

                )

                fig.update_layout(

                    title=dict(

                        text=f"Hosteler vs Day Scholar",

                        x=0.1,

                        font=dict(
                            size=30,
                            family="Arial Black",
                            color="white"
                        )

                    ),

                    template="plotly_dark",

                    paper_bgcolor="rgba(0,0,0,0)",

                    plot_bgcolor="rgba(0,0,0,0)",

                    height=550,

                    legend=dict(
                        orientation="h",
                        x=0.25,
                        y=1.08
                    )

                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )
        with col2:
            # ==========================================
            # Gender-wise Favorite Sports
            # ==========================================

            sports_df = df.copy()

            sports_df["Sports_Participation"] = (
                sports_df["Sports_Participation"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            sports_df = sports_df[
                sports_df["Sports_Participation"] == "yes"
            ]

            if sports_df.empty:

                st.warning("No Sports Participants Found.")

            elif "Favorite_Sport" not in sports_df.columns:

                st.warning("Favorite_Sport column not found.")

            else:

                gender_sport = (
                    sports_df
                    .groupby(["Favorite_Sport", "Gender"])
                    .size()
                    .reset_index(name="Students")
                )

                fig = px.bar(

                    gender_sport,

                    x="Favorite_Sport",

                    y="Students",

                    color="Gender",

                    barmode="group",

                    text="Students",

                    color_discrete_map={
                        "Male": "#00B9E8",
                        "Female": "#FF5E7E"
                    }

                )

                fig.update_traces(

                    textposition="outside",

                    marker_line_color="white",

                    marker_line_width=1.5

                )

                fig.update_layout(

                    title=dict(

                        text=f"Gender-wise Favorite Sports",

                        x=0.5,

                        xanchor="center",

                        font=dict(
                            size=30,
                            family="Arial Black",
                            color="white"
                        )

                    ),

                    template="plotly_dark",

                    paper_bgcolor="rgba(0,0,0,0)",

                    plot_bgcolor="rgba(0,0,0,0)",

                    height=600,

                    xaxis_title="Favorite Sport",

                    yaxis_title="Number of Students",

                    font=dict(
                        color="white",
                        size=14
                    ),

                    legend=dict(
                        orientation="h",
                        x=0.35,
                        y=1.08
                    ),

                    margin=dict(
                        l=20,
                        r=20,
                        t=70,
                        b=20
                    )

                )

                fig.update_xaxes(showgrid=False)

                fig.update_yaxes(
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.10)"
                )

                st.plotly_chart(fig, use_container_width=True)
        # ------------------------------
        # Search Student Records
        # ------------------------------

        st.markdown("""
        <h2 style="
            color:white;
            font-size:25px;
            font-family:Arial Black;
            margin:0;">
        🔍 Student Search Engine
        </h2>
        """, unsafe_allow_html=True)

        search = st.text_input(
            "Search Student",
            placeholder="Type Student Name, Percentage, Subject Marks..."
        )

        # Default dataframe
        filtered_df = df.copy()

        # Search
        if search:

            mask = (
                filtered_df
                .astype(str)
                .apply(lambda col: col.str.contains(search, case=False, na=False))
                .any(axis=1)
            )

            filtered_df = filtered_df[mask]

            st.success(f"✅ {len(filtered_df)} Student(s) Found")

        # Dynamic dataframe height
        rows = len(filtered_df)

        table_height = min(450, max(70, (rows + 1) * 35))

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            height=table_height
        )
        if len(filtered_df) == 1:

            row = filtered_df.iloc[0]

            student = row.to_dict()

            pdf_path = "Report/Sports_Report_Card.pdf"

            generate_sports_report(
                student,
                pdf_path
            )

            with open(pdf_path, "rb") as pdf:

                st.download_button(

                    "Download Sports Report Card",

                    data=pdf,

                    file_name=f"{row['Student_Name']}_Sports_Report.pdf",

                    mime="application/pdf",

                    use_container_width=True
                )
        # ------------------------------
        # Download CSV
        # ------------------------------

        csv = filtered_df.to_csv(index=False)

        st.download_button(
                "⬇ Download CSV",
                data=csv,
                file_name="students.csv",
                mime="text/csv",
                use_container_width=True
            )
    elif st.session_state.role == "teacher":
        st.info("Logged in as Teacher")
        # =====================
        # Class Comparison
        # =====================
        col1, col2 = st.columns([4, 2])
        if selected_class == "School Overview":
            with col1:

                avg_marks = (
                    school_df.groupby("Class")["Percentage"]
                    .mean()
                    .reset_index()
                    .sort_values(by="Percentage", ascending=False)
                )

                fig = px.bar(
                    avg_marks,
                    x="Class",
                    y="Percentage",
                    text=avg_marks["Percentage"].round(1),
                    color="Percentage",
                    color_continuous_scale="Blues",  # Same as Section Chart
                    title="Average Class Percentage"
                )

                fig.update_traces(
                    textposition="outside"
                )

                fig.update_layout(
                    title={
                        "text": "Average Class Percentage",
                        "x": 0.5,
                        "xanchor": "center",
                        "font": dict(
                            size=35,
                            family="Arial Black"
                        )
                    },
                    template="plotly_dark",
                    height=450,
                    coloraxis_showscale=False,
                    hovermode="x unified"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )
        elif selected_class != "School Overview":
            with col1:

                section_avg = (
                    df.groupby("Section")["Percentage"]
                    .mean()
                    .reset_index()
                    .sort_values(by="Percentage", ascending=False)
                )

                fig = px.bar(
                    section_avg,
                    x="Section",
                    y="Percentage",
                    text=section_avg["Percentage"].round(1),
                    title="Average Percentage by Section",
                    color="Percentage",
                    color_continuous_scale="Blues"
                )

                fig.update_traces(
                    textposition="outside"
                )

                fig.update_layout(
                    title={
                        "text": "Average Percentage by Section",
                        "x": 0.5,
                        "xanchor": "center",
                        "font": dict(
                            size=35,
                            family="Arial Black",
                            color="white"
                        )
                    },
                    xaxis_title="Section",
                    yaxis_title="Average Percentage (%)",
                    height=500,
                    showlegend=False
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )
        # =====================
        # Top 10 Toppers
        # =====================
        with col2:

            st.markdown(
                """
                <h2 style="
                    text-align:left;
                    color:#ffffff;
                    font-size:25px;
                    font-family:Arial Black;
                    font-weight:bold;
                ">
                Top 10 Class Toppers
                </h2>
                """,
                unsafe_allow_html=True
            )

            top_students = (
                df.sort_values(
                    by="Percentage",
                    ascending=False
                )
                .head(10)
                .reset_index(drop=True)
            )

            medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]

            top_students["Rank"] = medals

            top_students = top_students[
                [
                    "Rank",
                    "Student_Name",
                    "Percentage"
                ]
            ]

            st.dataframe(
                top_students,
                use_container_width=True,
                height=420,
                hide_index=True
            )

        # =====================
        # Attendance Trend
        # =====================
        if selected_class == "School Overview":
            attendance_trend = (
            school_df.groupby("Class")["Attendance_Percentage"]
            .mean()
            .reset_index()
            .sort_values(
                by="Attendance_Percentage",
                ascending=True
            )
        )

            fig = px.bar(
                attendance_trend,
                x="Attendance_Percentage",
                y="Class",
                orientation="h",
                text=attendance_trend["Attendance_Percentage"].round(1),
                color="Attendance_Percentage",
                color_continuous_scale=[
                    "#D6F9FF",
                    "#A5F3FC",
                    "#67E8F9",
                    "#22D3EE",
                    "#06B6D4",
                    "#0891B2"
                ],
                title=" Average Attendance by Class"
            )

            fig.update_traces(
                textposition="outside",
                marker_line_color="white",
                marker_line_width=1.5
            )

            fig.update_layout(
                title={
                    "text": "Average Attendance by Class",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": dict(
                        size=35,
                        family="Arial Black",
                        color="white"
                    )
                },
                template="plotly_dark",
                height=650,
                xaxis_title="Average Attendance (%)",
                yaxis_title="Class",
                coloraxis_showscale=False,
                hovermode="y unified",

                # Transparent background
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",

                font=dict(
                    color="white",
                    size=14
                ),
                margin=dict(
                    l=20,
                    r=20,
                    t=70,
                    b=20
                )
            )

            fig.update_xaxes(
                showgrid=False,
                zeroline=False
            )

            fig.update_yaxes(
                showgrid=False,
                zeroline=False
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
        elif selected_class != "School Overview":
            filtered_section_df = df[
                df["Class"] == selected_class
            ]

            section_counts = (
                filtered_section_df["Section"]
                .value_counts()
                .reset_index()
            )

            section_counts.columns = ["Section", "Students"]

            fig = px.bar(
                section_counts,
                x="Students",
                y="Section",
                orientation="h",
                text="Students",
                color="Students",
                color_continuous_scale="Blues",
                title=f" Students by Section - {selected_class}"
            )

            fig.update_traces(
                textposition="outside"
            )
            fig.update_layout(
                title={
                    "text": f"Students by Section - {selected_class}",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": dict(
                        size=35,
                        family="Arial Black"
                    )
                },
                template="plotly_dark",
                height=650,
                xaxis_title="Number of Students",
                yaxis_title="Section",
                coloraxis_showscale=False,
                hovermode="y unified",
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # ==========================================
        # Subject Selection
        # ==========================================
        # ----------------------------------------
        # Subject list
        # ----------------------------------------

        if selected_class == "School Overview":

            subjects = [
                "Maths_Marks",
                "Science_Marks",
                "SocialScience_Marks",
                "Computer_Marks",
                "Physics_Marks",
                "Chemistry_Marks",
                "Biology_Marks",
                "Business_Marks",
                "Accountancy_Marks",
                "Economics_Marks",
                "English_Marks",
                "Hindi_Marks"
            ]

        elif selected_class in ["Class 9","Class 10"]:

            subjects = [
                "Maths_Marks",
                "Science_Marks",
                "SocialScience_Marks",
                "English_Marks",
                "Computer_Marks",
                "Hindi_Marks"
            ]

        elif selected_class in ["Class 11 PCM","Class 12 PCM"]:

            subjects = [
                "Maths_Marks",
                "Physics_Marks",
                "Chemistry_Marks",
                "English_Marks",
                "Physical_Education_Marks",
                "Hindi_Marks"
            ]

        elif selected_class in ["Class 11 PCB","Class 12 PCB"]:

            subjects = [
                "Biology_Marks",
                "Physics_Marks",
                "Chemistry_Marks",
                "English_Marks",
                "Physical_Education_Marks",
                "Hindi_Marks"
            ]

        else:

            subjects = [
                "Business_Marks",
                "Accountancy_Marks",
                "Economics_Marks",
                "English_Marks",
                "Physical_Education_Marks",
                "Hindi_Marks"
            ]

        subjects = [s for s in subjects if s in df.columns]

        # ----------------------------------------
        # School Average
        # ----------------------------------------

        school_avg = []

        for subject in subjects:
            school_avg.append(
                school_df[subject].dropna().mean()
            )

        # ----------------------------------------
        # Selected Class Average
        # ----------------------------------------

        class_avg = []

        for subject in subjects:

            if subject in df.columns:

                class_avg.append(
                    df[subject].dropna().mean()
                )

            else:

                class_avg.append(None)

        labels = [
            s.replace("_Marks","")
            .replace("_"," ")
            for s in subjects
        ]

        # Close Radar

        labels += [labels[0]]
        school_avg += [school_avg[0]]
        class_avg += [class_avg[0]]

        # ----------------------------------------
        # Radar Chart
        # ----------------------------------------

        fig = go.Figure()

        # School Average

        fig.add_trace(
            go.Scatterpolar(
                r=school_avg,
                theta=labels,
                fill="toself",
                name="School Average",
                line=dict(
                    color="#00E396",
                    width=3
                ),
                fillcolor="rgba(0,227,150,0.25)"
            )
        )

        # Selected Class

        if selected_class != "School Overview":

            fig.add_trace(
                go.Scatterpolar(
                    r=class_avg,
                    theta=labels,
                    fill="toself",
                    name=selected_class,
                    line=dict(
                        color="#00B9E8",
                        width=4
                    ),
                    fillcolor="rgba(0,185,232,0.35)"
                )
            )

        fig.update_layout(

            title=dict(
                text=f"Subject Performance Radar ({selected_class})",
                x=0.1,
                font=dict(
                    size=30,
                    family="Arial Black"
                )
            ),

            polar=dict(

                bgcolor="rgba(0,0,0,0)",

                radialaxis=dict(
                    visible=True,
                    range=[0,100],
                    tickfont=dict(size=13),
                    gridcolor="gray"
                ),

                angularaxis=dict(
                    tickfont=dict(
                        size=14,
                        color="white"
                    )
                )

            ),

            template="plotly_dark",

            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            legend=dict(
                orientation="h",
                y=1.12,
                x=0.5
            ),

            height=650
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
        col1, col2 = st.columns([4, 2])
        with col1:
            # ==========================================
            # 👨‍🎓 Student Type Distribution
            # ==========================================
            # ------------------------------------------
            # Create Student Category
            # ------------------------------------------

            temp_df = df.copy()

            temp_df["Student_Category"] = (
                temp_df["Student_Type"] + " - " + temp_df["Gender"]
            )

            # ------------------------------------------
            # Count Students
            # ------------------------------------------

            count_df = (
                temp_df.groupby("Student_Category")
                .size()
                .reset_index(name="Students")
            )

            # Keep order fixed
            order = [
                "Day Scholar - Male",
                "Day Scholar - Female",
                "Hosteler - Male",
                "Hosteler - Female"
            ]

            count_df["Student_Category"] = pd.Categorical(
                count_df["Student_Category"],
                categories=order,
                ordered=True
            )

            count_df = count_df.sort_values("Student_Category")

            # ------------------------------------------
            # Plot
            # ------------------------------------------

            fig = px.bar(

                count_df,

                x="Student_Category",
                y="Students",

                text="Students",

                color="Student_Category",

                color_discrete_map={

                    "Day Scholar - Male": "#00B9E8",
                    "Day Scholar - Female": "#66D9FF",

                    "Hosteler - Male": "#00E396",
                    "Hosteler - Female": "#7DFFB3"

                }

            )

            fig.update_traces(

                textposition="outside",

                marker_line_color="white",
                marker_line_width=2,

                width=0.55

            )

            fig.update_layout(

                title=dict(

                    text=f" Student Distribution ({selected_class})",

                    x=0.5,

                    xanchor="center",

                    font=dict(
                        size=30,
                        family="Arial Black",
                        color="white"
                    )

                ),

                template="plotly_dark",

                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",

                height=550,

                xaxis_title="Student Category",
                yaxis_title="Number of Students",

                showlegend=False,

                font=dict(
                    color="white",
                    size=14
                ),

                margin=dict(
                    l=20,
                    r=20,
                    t=70,
                    b=20
                )

            )

            fig.update_yaxes(

                showgrid=True,
                gridcolor="rgba(255,255,255,0.10)",
                zeroline=False

            )

            fig.update_xaxes(showgrid=False)

            st.plotly_chart(
                fig,
                use_container_width=True
            )
        with col2:
            # ==========================================
            # 👥 Gender Distribution
            # ==========================================
            # Count Gender
            gender_df = (
                df.groupby("Gender")
                .size()
                .reset_index(name="Students")
            )

            fig = px.pie(

                gender_df,

                names="Gender",

                values="Students",

                hole=0.55,

                color="Gender",

                color_discrete_map={

                    "Male": "#00B9E8",
                    "Female": "#FF5E7E"

                }

            )

            fig.update_traces(

                textposition="inside",

                textinfo="percent+label",

                textfont=dict(
                    size=16,
                    color="white"
                ),

                marker=dict(
                    line=dict(
                        color="white",
                        width=2
                    )
                ),

                pull=[0.04, 0.04],

                hovertemplate=
                "<b>%{label}</b><br>" +
                "Students: %{value}<br>" +
                "Percentage: %{percent}<extra></extra>"

            )

            fig.update_layout(

                title=dict(

                    text=f" Gender Distribution",

                    x=0.0,

                    font=dict(
                        size=30,
                        family="Arial Black",
                        color="white"
                    )

                ),

                template="plotly_dark",

                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",

                showlegend=True,

                legend=dict(

                    orientation="h",

                    x=0.35,

                    y=1.08,

                    font=dict(size=14)

                ),

                height=550,

                margin=dict(
                    l=20,
                    r=20,
                    t=70,
                    b=20
                )

            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # ==========================================
        # 🏠 Hostel Distribution - Lollipop Chart
        # ==========================================
        # Only hostel students
        hostel_df = df[df["Student_Type"] == "Hosteler"]

        # Count students in each hostel
        hostel_count = (
            hostel_df.groupby("Hostel_Name")
            .size()
            .reset_index(name="Students")
            .sort_values("Students", ascending=True)
        )

        fig = go.Figure()

        # ------------------------------------------
        # Draw one line for each hostel
        # ------------------------------------------

        for _, row in hostel_count.iterrows():

            fig.add_shape(
                type="line",
                x0=0,
                x1=row["Students"],
                y0=row["Hostel_Name"],
                y1=row["Hostel_Name"],
                line=dict(
                    color="#00B9E8",
                    width=5
                )
            )

        # ------------------------------------------
        # Draw lollipop heads
        # ------------------------------------------

        fig.add_trace(

            go.Scatter(

                x=hostel_count["Students"],
                y=hostel_count["Hostel_Name"],

                mode="markers+text",

                marker=dict(
                    size=20,
                    color="#00E396",
                    line=dict(
                        color="white",
                        width=2
                    )
                ),

                text=hostel_count["Students"],
                textposition="middle right",

                textfont=dict(
                    size=15,
                    color="white"
                ),

                hovertemplate=
                "<b>%{y}</b><br>" +
                "Students : %{x}<extra></extra>",

                showlegend=False

            )

        )

        # ------------------------------------------
        # Layout
        # ------------------------------------------

        fig.update_layout(

            title=dict(

                text=f" Hostel Distribution ({selected_class})",

                x=0.2,

                font=dict(
                    size=30,
                    family="Arial Black",
                    color="white"
                )

            ),

            template="plotly_dark",

            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            height=600,

            xaxis_title="Number of Students",
            yaxis_title="Hostel Name",

            font=dict(
                color="white",
                size=14
            ),

            margin=dict(
                l=30,
                r=30,
                t=70,
                b=30
            )

        )

        fig.update_xaxes(

            showgrid=True,

            gridcolor="rgba(255,255,255,0.10)",

            zeroline=False

        )

        fig.update_yaxes(

            showgrid=False,

            categoryorder="total ascending"

        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # Remove duplicate columns (safe for Plotly)
        df = df.loc[:, ~df.columns.duplicated()]

            # Check if the column exists
        if "Study_Hours_Per_Day" in df.columns:

                fig = px.histogram(

                    df,

                    x="Study_Hours_Per_Day",

                    nbins=10,

                    color_discrete_sequence=["#00B9E8"],

                    text_auto=True

                )

                fig.update_traces(

                    marker=dict(

                        line=dict(
                            color="white",
                            width=1.5
                        )

                    ),

                    opacity=0.9

                )

                fig.update_layout(

                    title=dict(

                        text=f"📚 Study Hours Distribution ({selected_class})",

                        x=0.5,

                        xanchor="center",

                        font=dict(
                            size=30,
                            family="Arial Black",
                            color="white"
                        )

                    ),

                    template="plotly_dark",

                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",

                    height=600,

                    xaxis_title="Study Hours Per Day",

                    yaxis_title="Number of Students",

                    bargap=0.08,

                    showlegend=False,

                    font=dict(
                        color="white",
                        size=14
                    ),

                    margin=dict(
                        l=20,
                        r=20,
                        t=70,
                        b=20
                    )

                )

                fig.update_xaxes(

                    showgrid=False,

                    zeroline=False

                )

                fig.update_yaxes(

                    showgrid=True,

                    gridcolor="rgba(255,255,255,0.10)",

                    zeroline=False

                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        else:
            st.warning("Study_Hours_Per_Day column not found.")


        #==========================================
        # 🎯 Career Goal Distribution
        #==========================================
        if "Career_Goal" in df.columns:

            career_df = (
                df["Career_Goal"]
                .value_counts()
                .reset_index()
            )

            career_df.columns = ["Career Goal", "Students"]

            fig = px.bar(

                career_df,

                x="Career Goal",
                y="Students",

                text="Students",

                color="Students",

                color_continuous_scale="Blues"

            )

            fig.update_traces(
                textposition="outside",
                marker_line_color="white",
                marker_line_width=2
            )

            fig.update_layout(

                title=dict(
                    text=" Career Goal Distribution",
                    x=0.3,
                    font=dict(
                        size=28,
                        family="Arial Black"
                    )
                ),

                template="plotly_dark",

                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",

                coloraxis_showscale=False,

                height=500,

                showlegend=False

            )

            st.plotly_chart(fig, use_container_width=True)
        #------------------------------
        # Insights Panel
        #------------------------------
        st.markdown("## 🤖 Insights Panel")

        with st.container(border=True):

            # School Average
            avg_percentage = df["Percentage"].mean()

            # Highest Percentage
            highest_percentage = df["Percentage"].max()

            # Top Student
            if "Student_Name" in df.columns:
                topper = df.loc[
                    df["Percentage"].idxmax(),
                    "Student_Name"
                ]
            elif "Name" in df.columns:
                topper = df.loc[
                    df["Percentage"].idxmax(),
                    "Name"
                ]
            else:
                topper = "Top Student"

            # Risk Students
            risk_students = len(
                df[df["Percentage"] < 40]
            )

            # Excellent Students
            excellent_students = len(
                df[df["Percentage"] >= 90]
            )

            # Average By Class
            class_avg = (
                df.groupby("Class")["Percentage"]
                .mean()
                .sort_values(ascending=False)
            )

            best_class = class_avg.index[0]
            best_class_avg = class_avg.iloc[0]

            lowest_class = class_avg.index[-1]
            lowest_class_avg = class_avg.iloc[-1]

            # Performance Categories
            above_80 = len(df[df["Percentage"] >= 80])
            between_60_80 = len(
                df[
                    (df["Percentage"] >= 60)
                    & (df["Percentage"] < 80)
                ]
            )
            below_60 = len(df[df["Percentage"] < 60])

            # ======================================
            # INSIGHTS
            # ======================================

            st.success(
                f"📈Average Percentage: "
                f"{avg_percentage:.1f}%"
            )

            st.success(
                f"🏆 Best Performing Class: "
                f"{best_class} "
                f"({best_class_avg:.1f}%)"
            )

            st.warning(
                f"📉 Lowest Performing Class: "
                f"{lowest_class} "
                f"({lowest_class_avg:.1f}%)"
            )

            st.info(
                f"🥇Topper: "
                f"{topper} "
                f"({highest_percentage:.1f}%)"
            )

            st.success(
                f"🎯 Students Above 90%: "
                f"{excellent_students}"
            )

            st.error(
                f"⚠️ Students Below 40%: "
                f"{risk_students}"
            )

            st.markdown("---")

            st.markdown("### 📊 Performance Breakdown")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "🌟 Above 80%",
                    above_80
                )

            with col2:
                st.metric(
                    "📚 60-80%",
                    between_60_80
                )

            with col3:
                st.metric(
                    "⚠️ Below 60%",
                    below_60
                )

            st.markdown("---")
        cols = pd.Series(df.columns)
        # ------------------------------
        # Search Student Records
        # ------------------------------

        st.markdown("""
        <h2 style="
            color:white;
            font-size:25px;
            font-family:Arial Black;
            margin:0;">
        🔍 Student Search Engine
        </h2>
        """, unsafe_allow_html=True)

        search = st.text_input(
            "Search Student",
            placeholder="Type Student Name, Percentage, Subject Marks..."
        )

        # Default dataframe
        filtered_df = df.copy()

        # Search
        if search:

            mask = (
                filtered_df
                .astype(str)
                .apply(lambda col: col.str.contains(search, case=False, na=False))
                .any(axis=1)
            )

            filtered_df = filtered_df[mask]

            st.success(f"✅ {len(filtered_df)} Student(s) Found")

        # Dynamic dataframe height
        rows = len(filtered_df)

        table_height = min(450, max(70, (rows + 1) * 35))

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            height=table_height
        )
        # ------------------------------
        # Download Report Card
        # ------------------------------

        if len(filtered_df) == 1:

            row = filtered_df.iloc[0]

            class_key = selected_class.replace(" ", "_")

            if class_key == "School_Overview":
                class_key = row["Class"].replace(" ", "_")

            student_data = row_to_student_data(
                row,
                SUBJECT_COLS[class_key]
            )

            pdf = create_report_card(student_data)

            st.download_button(
                " Download Report Card",
                data=pdf,
                file_name=f"{row['Student_Name']}_Report_Card.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        # ------------------------------
        # Download CSV
        # ------------------------------

        csv = filtered_df.to_csv(index=False)

        st.download_button(
            "⬇ Download CSV",
            data=csv,
            file_name="students.csv",
            mime="text/csv",
            use_container_width=True
        )
# ==========================
# MAIN APP
# ==========================
if st.session_state.logged_in:
    dashboard()
else:
    login_page()