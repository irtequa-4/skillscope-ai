import pandas as pd
import spacy
import re
from collections import Counter

nlp = spacy.load("en_core_web_sm")

# Master skill list — expand this as needed
SKILLS = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "kotlin", "swift",
    "r", "scala", "php", "ruby", "dart",
    # Web
    "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "html", "css",
    "next.js", "express",
    # Data & AI
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
    "keras", "scikit-learn", "pandas", "numpy", "data science", "llm", "generative ai",
    "langchain", "openai", "hugging face",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "ci/cd",
    "linux", "git", "github", "gitlab",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "firebase",
    # Other
    "power bi", "tableau", "excel", "spark", "hadoop", "kafka", "airflow",
    "blockchain", "web3", "solidity", "unity", "flutter", "android", "ios"
]

def extract_skills(text):
    if not isinstance(text, str):
        return []
    text_lower = text.lower()
    found = []
    for skill in SKILLS:
        # Use word boundary matching to avoid false positives
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)
    return found

def process_jobs(csv_path="jobs_raw.csv"):
    df = pd.read_csv(csv_path)
    print(f"Processing {len(df)} job listings...")
    
    df["skills_found"] = df["description"].apply(extract_skills)
    df["skill_count"] = df["skills_found"].apply(len)
    
    # Save processed data
    df.to_csv("jobs_processed.csv", index=False)
    
    # Create skill frequency dataframe
    all_skills = []
    for skills_list in df["skills_found"]:
        if isinstance(skills_list, list):
            all_skills.extend(skills_list)
    
    skill_counts = Counter(all_skills)
    skill_df = pd.DataFrame(skill_counts.items(), columns=["skill", "count"])
    skill_df = skill_df.sort_values("count", ascending=False)
    skill_df["percentage"] = (skill_df["count"] / len(df) * 100).round(2)
    skill_df.to_csv("skill_frequency.csv", index=False)
    
    print("Top 20 Skills:")
    print(skill_df.head(20).to_string())
    return df, skill_df

if __name__ == "__main__":
    process_jobs()