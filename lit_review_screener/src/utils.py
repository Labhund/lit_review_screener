def load_config(config_path):
    import yaml
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def setup_logging(log_file):
    import logging
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def query_crossref(doi, email):
    import requests
    headers = {'User-Agent': email}
    response = requests.get(f'https://api.crossref.org/works/{doi}/transform/application/x-bibtex', headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None

def query_pubmed(pmid):
    import requests
    response = requests.get(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=xml')
    if response.status_code == 200:
        return response.text
    else:
        return None

def query_ollama(prompt, ollama_url, model_name):
    import requests
    response = requests.post(ollama_url, json={'prompt': prompt, 'model': model_name})
    if response.status_code == 200:
        return response.json()
    else:
        return None

def parse_ollama_json(response_text):
    import json
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return None