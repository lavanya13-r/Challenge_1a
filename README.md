# PDF Outline Extractor for Adobe India Hackathon 2025

## Overview
This solution addresses Challenge 1a of the Adobe India Hackathon 2025. It processes PDF files to extract the title and hierarchical headings (H1, H2, H3) with their respective page numbers, outputting the results as JSON files. The solution is containerized using Docker and optimized for the challenge constraints.

## Approach
- **Library Used**: `pdfplumber` (open-source, <200MB) for PDF text extraction.
- **Title Extraction**: Identifies the largest font text on the first page as the title.
- **Heading Detection**: Uses font size thresholds to classify headings as H1, H2, or H3. Headings are identified by analyzing font sizes across the document and assigning levels based on relative size.
- **Output**: Generates JSON files conforming to the provided `output_schema.json`.
- **Optimization**: Processes PDFs efficiently to meet the 10-second execution time for 50-page PDFs, using CPU-only processing and minimal memory.

## Libraries and Models
- **pdfplumber**: For PDF parsing and text extraction.
- **No ML models**: The solution relies on heuristic-based font size analysis, keeping it lightweight (<200MB).
- All dependencies are open-source and installed within the Docker container.

## How to Build and Run
1. **Build the Docker Image**:
   ```bash
   docker build --platform linux/amd64 -t pdf-processor .