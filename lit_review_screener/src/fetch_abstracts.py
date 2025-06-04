import json
import requests
from utils import load_config, query_crossref, query_pubmed, setup_logging

def fetch_abstracts(parsed_references_path):
    # Load configuration
    config = load_config('config/config.yaml')
    crossref_email = config['api']['crossref_email']
    
    # Load parsed references
    with open(parsed_references_path, 'r') as f:
        references = json.load(f)

    for reference in references:
        if not reference.get('abstract'):
            doi = reference.get('doi')
            pmid = reference.get('pmid')
            abstract = None
            
            # Try fetching abstract using DOI
            if doi:
                abstract = query_crossref(doi, crossref_email)
            
            # If DOI fetching fails or is not available, try PMID
            if not abstract and pmid:
                abstract = query_pubmed(pmid)
            
            # Update reference with fetched abstract
            if abstract:
                reference['abstract'] = abstract
                reference['status'] = 'abstract_fetched'
            else:
                reference['status'] = 'abstract_not_found'

    # Save updated references with abstracts
    output_path = config['paths']['abstracts_output']
    with open(output_path, 'w') as f:
        json.dump(references, f, indent=2)

if __name__ == "__main__":
    setup_logging()
    fetch_abstracts('data/output/references_parsed.json')