import logging
import yaml
from parse_bibtex import parse_bibtex
from fetch_abstracts import fetch_abstracts
from screen_papers import screen_papers
from utils import load_config, setup_logging

def main():
    # Load configuration
    config = load_config('config/config.yaml')

    # Setup logging
    setup_logging(config['paths']['log_file'])

    logging.info("Starting the literature review screening process.")

    # Step 1: Parse BibTeX file
    parsed_references = parse_bibtex(config['paths']['bibtex_input'])
    
    # Step 2: Fetch abstracts
    references_with_abstracts = fetch_abstracts(parsed_references)

    # Step 3: Screen papers
    screening_results = screen_papers(references_with_abstracts, config['paths']['criteria_file'])

    logging.info("Literature review screening process completed.")
    logging.info(f"Results saved to {config['paths']['results_output']}.")

if __name__ == "__main__":
    main()