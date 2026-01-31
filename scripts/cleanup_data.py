import json
from pathlib import Path

DATA_DIR = Path("data")
EXCLUDED_FIELDS = {
    "testBodies", "testDescriptions", "testInfo", 
    "fullCodeOutput", "stdOutput", "codeOutput", 
    "lastTestcase", "expectedOutput", 
    "totalCorrect", "totalTestcases", 
    "runtimeDistribution", "memoryDistribution",
    "userAvatar", "avatar", "profileUrl",
    "codeSnippets"
}

def clean_data(data):
    if isinstance(data, dict):
        return {
            k: clean_data(v) 
            for k, v in data.items() 
            if k not in EXCLUDED_FIELDS
        }
    elif isinstance(data, list):
        return [clean_data(item) for item in data]
    else:
        return data

def main():
    print("Cleaning up existing JSON files...")
    count = 0
    for file_path in DATA_DIR.glob("**/*.json"):
        if "raw" in str(file_path): continue
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            cleaned = clean_data(data)
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(cleaned, f, indent=2, ensure_ascii=False)
            
            count += 1
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    print(f"Cleaned {count} files.")

if __name__ == "__main__":
    main()