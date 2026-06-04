import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import ast
import PyPDF2
import io
import re

# Page config
st.set_page_config(
    page_title="SkillScope AI",
    page_icon="🎯",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    jobs = pd.read_csv("jobs_processed.csv")
    jobs["skills_found"] = jobs["skills_found"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else []
    )
    skills = pd.read_csv("skill_frequency.csv")
    return jobs, skills

jobs_df, skills_df = load_data()

with st.sidebar:
    st.markdown("## 🎯")
    st.title("SkillScope AI")
    st.markdown("---")
    st.markdown("**Data Stats**")
    st.write(f"📦 {len(jobs_df):,} jobs analyzed")
    st.write(f"🔧 {len(skills_df)} skills tracked")
    st.markdown("---")
    st.markdown("*Built for real-time job market intelligence*")

# Header
st.title("🎯 SkillScope AI")
st.markdown("*Real-Time Job Market Intelligence & Skill Analysis Platform*")
st.divider()

# KPI Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Jobs Analyzed", f"{len(jobs_df):,}")
col2.metric("Unique Skills Tracked", f"{len(skills_df)}")
col3.metric("Top Skill", skills_df.iloc[0]["skill"].title())
col4.metric("Avg Skills per Job", f"{jobs_df['skill_count'].mean():.1f}")

st.divider()

# Tab layout
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Overview", 
    "🔥 Skill Trends", 
    "🏢 Company Insights",
    "🔍 Resume Gap Analyzer",
    "📄 Resume Upload"
])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 20 In-Demand Skills")
        top20 = skills_df.head(20)
        fig = px.bar(
            top20, x="count", y="skill",
            orientation="h",
            color="count",
            color_continuous_scale="viridis",
            labels={"count": "Job Postings", "skill": "Skill"}
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Skill Cloud")
        skill_dict = dict(zip(skills_df["skill"], skills_df["count"]))
        wc = WordCloud(
            width=800, height=400,
            background_color="black",
            colormap="plasma"
        ).generate_from_frequencies(skill_dict)
        fig_wc, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig_wc)

with tab2:
    st.subheader("Skill Category Breakdown")
    
    categories = {
        "AI/ML": ["machine learning", "deep learning", "nlp", "tensorflow", "pytorch", 
                  "generative ai", "llm", "langchain"],
        "Cloud/DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd"],
        "Web Dev": ["react", "angular", "vue", "node.js", "django", "flask", "next.js"],
        "Data": ["sql", "pandas", "spark", "hadoop", "kafka", "power bi", "tableau"],
        "Languages": ["python", "java", "javascript", "typescript", "go", "rust"]
    }
    
    category_totals = {}
    for cat, cat_skills in categories.items():
        total = skills_df[skills_df["skill"].isin(cat_skills)]["count"].sum()
        category_totals[cat] = total
    
    fig_pie = px.pie(
        values=list(category_totals.values()),
        names=list(category_totals.keys()),
        title="Market Share by Skill Category",
        color_discrete_sequence=px.colors.sequential.Plasma_r
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.subheader("Skills Percentage in Job Postings")
    top15 = skills_df.head(15)
    fig2 = px.bar(
        top15, x="skill", y="percentage",
        color="percentage",
        color_continuous_scale="plasma",
        labels={"percentage": "% of Jobs Requiring This Skill", "skill": ""}
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("Top Hiring Companies")
    top_companies = jobs_df["company"].value_counts().head(15).reset_index()
    top_companies.columns = ["company", "openings"]
    fig3 = px.bar(
        top_companies, x="openings", y="company",
        orientation="h",
        color="openings",
        color_continuous_scale="teal"
    )
    fig3.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig3, use_container_width=True)
    
    st.subheader("Hiring by Location")
    top_locations = jobs_df["location"].value_counts().head(10).reset_index()
    top_locations.columns = ["location", "jobs"]
    fig4 = px.bar(top_locations, x="location", y="jobs", color="jobs",
                  color_continuous_scale="blues")
    st.plotly_chart(fig4, use_container_width=True)

with tab4:
    st.subheader("🔍 Resume Gap Analyzer")
    st.markdown("Enter your current skills and get a gap analysis against market demand.")
    
    user_input = st.text_area(
        "Paste your skills (comma separated):",
        placeholder="e.g. Python, React, SQL, Git, Machine Learning"
    )
    target_role = st.selectbox(
        "Target Role Category:",
        ["All Roles", "AI/ML", "Web Dev", "Cloud/DevOps", "Data"]
    )
    
    if st.button("Analyze My Gap", type="primary"):
        if user_input:
            user_skills = [s.strip().lower() for s in user_input.split(",")]
            
            if target_role == "All Roles":
                market_top = set(skills_df.head(30)["skill"].tolist())
            else:
                market_top = set(categories.get(target_role, []))
            
            missing = market_top - set(user_skills)
            present = market_top & set(user_skills)
            match_pct = len(present) / len(market_top) * 100 if market_top else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("✅ Skills You Have", len(present))
            col2.metric("❌ Skills Missing", len(missing))
            col3.metric("📈 Market Match", f"{match_pct:.0f}%")
            
            st.progress(int(match_pct))
            
            if missing:
                st.subheader("🎯 Recommended Skills to Learn")
                # Sort missing skills by market demand
                missing_with_counts = skills_df[
                    skills_df["skill"].isin(missing)
                ].sort_values("count", ascending=False)
                
                for _, row in missing_with_counts.iterrows():
                    st.markdown(f"**{row['skill'].title()}** — appears in {row['count']} job postings ({row['percentage']}% of market)")
            
            if present:
                st.subheader("✅ Your Marketable Skills")
                st.write(", ".join([s.title() for s in present]))
        else:
            st.warning("Please enter your skills first.")


with tab5:
    st.subheader("📄 Upload Your Resume")
    uploaded_file = st.file_uploader("Upload PDF resume", type=["pdf"])

    import re
    SKILLS_LOCAL = ["python","java","javascript","typescript","c++","c#","go","rust",
              "react","angular","vue","node.js","django","flask","fastapi",
              "machine learning","deep learning","nlp","tensorflow","pytorch",
              "scikit-learn","pandas","numpy","generative ai","llm","langchain",
              "aws","azure","gcp","docker","kubernetes","terraform","ci/cd",
              "sql","mysql","postgresql","mongodb","redis","elasticsearch",
              "power bi","tableau","spark","hadoop","kafka","git","linux"]

    def extract_skills_local(text):
        text_lower = text.lower()
        return [s for s in SKILLS_LOCAL if re.search(r'\b' + re.escape(s) + r'\b', text_lower)]

    if uploaded_file:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        resume_text = ""
        for page in pdf_reader.pages:
            resume_text += page.extract_text()

        resume_skills = extract_skills_local(resume_text)

        st.success(f"Found {len(resume_skills)} recognized skills in your resume")
        st.write("**Detected Skills:**", ", ".join([s.title() for s in resume_skills]))

        market_top30 = set(skills_df.head(30)["skill"].tolist())
        missing = market_top30 - set(resume_skills)
        match_pct = (len(market_top30) - len(missing)) / len(market_top30) * 100

        st.metric("Resume-Market Match Score", f"{match_pct:.0f}%")
        st.progress(int(match_pct))

        st.subheader("Top Skills to Add to Resume")
        priority_skills = skills_df[skills_df["skill"].isin(missing)].head(10)
        for _, row in priority_skills.iterrows():
            st.markdown(f"➕ **{row['skill'].title()}** — in demand in {row['percentage']}% of jobs")
