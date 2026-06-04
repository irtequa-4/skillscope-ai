import pandas as pd

def load_kaggle_jobs(csv_path="postings.csv"):
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} jobs")
    print("Columns:", df.columns.tolist())
    
    # Keep only useful columns (adjust names after checking above output)
    df = df[["title", "company_name", "location", "description"]].copy()
    df.columns = ["title", "company", "location", "description"]
    
    # Drop rows with no description
    df = df.dropna(subset=["description"])
    df.to_csv("jobs_raw.csv", index=False)
    print(f"Saved {len(df)} clean jobs to jobs_raw.csv")
    return df

if __name__ == "__main__":
    load_kaggle_jobs()