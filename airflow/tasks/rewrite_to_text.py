import os

def rewrite_to_text(records, output_path="data/processed"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for rec in records:
            text = rec["content"].strip()
            f.write(text + "\n")
    return output_path