# lit_review_screener
local llama powered abstract screener

# Proposed structure:

Project Directory Structure
lit_review_screener/
├── data/
│   ├── input/              # Place your input BibTeX files here
│   │   └── example_search.bib
│   └── output/             # Processed data and results will go here
│       ├── references_parsed.json
│       ├── references_with_abstracts.json
│       └── screening_results.csv
├── src/
│   ├── __init__.py
│   ├── parse_bibtex.py     # Script to parse the initial BibTeX file
│   ├── fetch_abstracts.py  # Script to fetch abstracts using DOIs/PMIDs
│   ├── screen_papers.py    # Script to interact with Ollama for screening
│   ├── utils.py            # Helper functions (e.g., API interaction, logging)
│   └── main.py             # Main script to orchestrate the workflow
├── config/
│   ├── config.yaml         # Configuration file (API endpoints, model, paths)
│   └── screening_criteria.txt # File containing the inclusion/exclusion criteria prompt details
├── logs/                   # Log files for debugging
│   └── app.log
├── .gitignore              # Git ignore file
├── requirements.txt        # Python dependencies
└── README.md               # Project description, setup, and usage instructions

Python Script Requirements & Input/Output
Here's a breakdown of each key script in the src/ directory:

parse_bibtex.py

Purpose: Reads the input BibTeX file and converts it into a structured format, extracting key information.
Input:
Path to the input .bib file (e.g., data/input/example_search.bib).
Process:
Uses a library like bibtexparser.
Iterates through entries.
Extracts essential fields: a unique identifier for the script (can just be the BibTeX key initially), DOI, PMID (if available), title, author, year, journal, abstract (if present in the BibTeX).
Handles potential missing fields gracefully.
Output:
A structured data file (e.g., data/output/references_parsed.json). This could be a JSON list of dictionaries, where each dictionary represents a paper.
Example JSON structure:
[
  {
    "bib_key": "Author2023",
    "doi": "10.1234/example.doi",
    "pmid": "12345678",
    "title": "Example Paper Title",
    "abstract": "Abstract text if available...",
    "status": "parsed" // track processing stage
  },
  ...
]

fetch_abstracts.py

Purpose: Takes the parsed references and fetches missing abstracts using DOIs or PMIDs from external APIs.
Input:
Path to the parsed references file (e.g., data/output/references_parsed.json).
Configuration (e.g., your email for Crossref politeness header, from config/config.yaml).
Process:
Loads the parsed references.
Iterates through references. If abstract is missing or empty:
Try fetching using DOI via Crossref API (using functions possibly defined in utils.py).
If no DOI or Crossref fails, try fetching using PMID via PubMed E-utilities API (if PMID exists).
Adds the fetched abstract to the reference dictionary.
Includes error handling for API requests (timeouts, not found, rate limits).
Updates the status field (e.g., abstract_fetched, abstract_not_found).
Logs successes and failures (to logs/app.log).
Output:
An updated structured data file with abstracts filled in where possible (e.g., data/output/references_with_abstracts.json). Same format as input, but with abstracts added and status updated.

screen_papers.py

Purpose: Sends abstracts and screening criteria to the local Ollama instance for evaluation.
Input:
Path to the references file with abstracts (e.g., data/output/references_with_abstracts.json).
Path to the screening criteria file (config/screening_criteria.txt).
Ollama configuration (API URL, model name, e.g., phi3:14b-medium-instruct-q4_K_M, from config/config.yaml).
Process:
Loads references with abstracts.
Loads the screening criteria text.
Iterates through references that have an abstract:
Constructs a detailed prompt for Ollama, including:
The abstract text.
The screening criteria (inclusion/exclusion rules).
Clear instructions to evaluate the abstract against the criteria.
Crucially: Explicit instruction to return the result as a JSON object with specific keys (e.g., {"include": boolean, "confidence": float, "reasoning": "string", "summary": "string"}).
Sends the prompt to the Ollama API (using a helper function in utils.py).
Parses the JSON response from Ollama. Handles potential errors (invalid JSON, Ollama errors).
Stores the results (include/exclude decision, confidence, reasoning, summary) alongside the reference information.
Updates the status (e.g., screened, screening_error).
Logs progress and any errors.
Output:
A results file, likely CSV for easy review (e.g., data/output/screening_results.csv).
Example CSV columns: bib_key, doi, title, llm_include_decision, llm_confidence, llm_reasoning, llm_summary, screening_status.

main.py

Purpose: Acts as the main entry point and orchestrator for the pipeline.
Input: Command-line arguments or reads from config/config.yaml to get file paths, model names, etc.
Process:
Initializes logging.
Loads configuration.
Calls the main function/class from parse_bibtex.py.
Calls the main function/class from fetch_abstracts.py, passing the output path from the previous step.
Calls the main function/class from screen_papers.py, passing the output path from the abstract fetching step.
Prints status updates or summary information to the console.
Output: Console messages indicating progress and completion. The final results file (screening_results.csv) is generated by screen_papers.py.

utils.py

Purpose: Contains reusable helper functions used by other scripts.
Functions:
load_config(config_path): Reads the YAML config file.
setup_logging(): Configures logging to file and console.
query_crossref(doi, email): Handles interaction with the Crossref API.
query_pubmed(pmid): Handles interaction with PubMed E-utilities.
query_ollama(prompt, ollama_url, model_name): Sends prompt to Ollama, gets response, handles basic errors.
parse_ollama_json(response_text): Safely parses JSON from Ollama's potentially messy output string.

Configuration Files
config/config.yaml:
paths:
  bibtex_input: "data/input/example_search.bib"
  parsed_output: "data/output/references_parsed.json"
  abstracts_output: "data/output/references_with_abstracts.json"
  results_output: "data/output/screening_results.csv"
  log_file: "logs/app.log"
  criteria_file: "config/screening_criteria.txt"

api:
  crossref_email: "your_email@domain.com" # For politeness policy

ollama:
  url: "http://localhost:11434/api/generate" # Default Ollama API endpoint
  model: "phi3:14b-medium-instruct-q4_K_M" # Your chosen model
  # Add any specific Ollama parameters if needed (temperature, etc.)

config/screening_criteria.txt:
You are an expert research assistant screening abstracts based on specific criteria.
Analyze the following abstract based *only* on the text provided.

**Inclusion Criteria:**
- Must involve [Specific Topic A, e.g., ecdysone receptor].
- Must use [Specific Method B, e.g., molecular dynamics simulation].
- Must focus on [Specific Organism/System C, e.g., insects].

**Exclusion Criteria:**
- Primarily a review paper.
- Focuses only on [Related but Excluded Topic D, e.g., synthesis methods].
- Study conducted in [Excluded System E, e.g., mammals].

**Task:**
Evaluate the abstract against these criteria. Respond *only* with a single, valid JSON object containing the following keys:
- "include": boolean (true if it meets inclusion criteria and avoids exclusion criteria, false otherwise)
- "confidence": float (your estimated confidence in the decision, 0.0 to 1.0)
- "reasoning": string (a brief explanation for your decision, citing criteria)
- "summary": string (a one-sentence summary of the abstract's key finding relevant to the criteria)

**Abstract:**
{abstract_placeholder} 

**JSON Response:**
{
  "include": null,
  "confidence": null,
  "reasoning": null,
  "summary": null
}

This structure provides modularity, making it easier to develop, test, and debug each part of the process. Remember to install necessary libraries (pip install bibtexparser requests pyyaml) and list them in requirements.txt.