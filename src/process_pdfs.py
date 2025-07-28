import pdfplumber
from pathlib import Path
import json
import re
from collections import defaultdict

def extract_title_and_headings(pdf_path):
    title = "Unknown Title"
    outline = []
    seen = set()
    line_frequency = defaultdict(int)
    heading_pattern = re.compile(r"^\d+(?:\.\d+)*\s+.+")
  # Matches: 1 Intro, 1.1 Scope, 2.3.1 Details

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)

            # --------- Title Detection (Largest Font on First Page) ---------
            first_page = pdf.pages[0]
            title_candidates = [
                (w["text"].strip(), w["size"])
                for w in first_page.extract_words(extra_attrs=["size"])
                if len(w["text"].strip()) > 10
            ]
            if title_candidates:
                title = max(title_candidates, key=lambda x: x[1])[0]

            # --------- Count Line Frequencies Across All Pages ---------
            for page in pdf.pages:
                words = page.extract_words(extra_attrs=["x0", "top", "bottom"])
                lines_by_y = {}

                for word in words:
                    y = round(word["top"])
                    lines_by_y.setdefault(y, []).append(word)

                for y, words_on_line in lines_by_y.items():
                    if y < 50 or y > page.height - 50:
                        line_text = " ".join(word["text"] for word in sorted(words_on_line, key=lambda w: w["x0"])).strip()
                        line_lower = line_text.lower()
                        if len(line_lower) > 3:
                            line_frequency[line_lower] += 1

            # --------- Actual Heading Extraction ---------
            for page_num, page in enumerate(pdf.pages, start=1):
                words = page.extract_words(extra_attrs=["x0", "top", "bottom", "size"])
                lines_by_y = {}

                for word in words:
                    y = round(word["top"])
                    lines_by_y.setdefault(y, []).append(word)

                for y, words_on_line in sorted(lines_by_y.items()):
                    if y < 50 or y > page.height - 50:
                        continue

                    line_text = " ".join(word["text"] for word in sorted(words_on_line, key=lambda w: w["x0"])).strip()
                    line_lower = line_text.lower()

                    # Skip if empty, too long, seen before, or frequent on most pages
                    if (
                        not line_text
                        or len(line_text) > 100
                        or line_lower in seen
                        or line_frequency[line_lower] > total_pages * 0.6  # appears on >60% of pages
                    ):
                        continue

                    if heading_pattern.match(line_text):
                        number_part = line_text.split()[0]
                        dot_count = number_part.count(".")

                        if dot_count == 0:
                            level = "H1"
                        elif dot_count == 1:
                            level = "H2"
                        else:
                            level = "H3"

                        outline.append({
                            "level": level,
                            "text": line_text,
                            "page": page_num
                        })
                        seen.add(line_lower)

    except Exception as e:
        print(f"❌ Error processing {pdf_path.name}: {e}")

    return {
        "title": title,
        "outline": outline
    }

def process_pdfs():
    input_dir = Path("sample_dataset/pdfs")
    output_dir = Path("sample_dataset/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    for pdf_file in input_dir.glob("*.pdf"):
        print(f"📄 Processing: {pdf_file.name}")
        result = extract_title_and_headings(pdf_file)
        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved to: {output_file}")

if __name__ == "__main__":
    process_pdfs()
