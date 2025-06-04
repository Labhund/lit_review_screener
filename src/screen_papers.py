import json
import logging
from utils import query_ollama, load_config

def screen_papers(references_file, criteria_file, ollama_url, model_name):
    # Load references with abstracts
    with open(references_file, 'r') as f:
        references = json.load(f)

    # Load screening criteria
    with open(criteria_file, 'r') as f:
        criteria = f.read()

    results = []

    for reference in references:
        if 'abstract' in reference and reference['abstract']:
            prompt = f"{criteria}\n\n**Abstract:**\n{reference['abstract']}\n\n**JSON Response:**\n{{\"include\": null, \"confidence\": null, \"reasoning\": null, \"summary\": null}}"
            try:
                response = query_ollama(prompt, ollama_url, model_name)
                results.append({
                    'bib_key': reference['bib_key'],
                    'doi': reference.get('doi', ''),
                    'title': reference.get('title', ''),
                    'llm_include_decision': response.get('include'),
                    'llm_confidence': response.get('confidence'),
                    'llm_reasoning': response.get('reasoning'),
                    'llm_summary': response.get('summary'),
                    'screening_status': 'screened'
                })
            except Exception as e:
                logging.error(f"Error screening {reference['bib_key']}: {e}")
                results.append({
                    'bib_key': reference['bib_key'],
                    'doi': reference.get('doi', ''),
                    'title': reference.get('title', ''),
                    'llm_include_decision': None,
                    'llm_confidence': None,
                    'llm_reasoning': None,
                    'llm_summary': None,
                    'screening_status': 'screening_error'
                })

    # Save results to CSV
    with open('data/output/screening_results.csv', 'w') as f:
        f.write('bib_key,doi,title,llm_include_decision,llm_confidence,llm_reasoning,llm_summary,screening_status\n')
        for result in results:
            f.write(f"{result['bib_key']},{result['doi']},{result['title']},{result['llm_include_decision']},{result['llm_confidence']},{result['llm_reasoning']},{result['llm_summary']},{result['screening_status']}\n")

if __name__ == "__main__":
    config = load_config('config/config.yaml')
    screen_papers(config['paths']['abstracts_output'], config['paths']['criteria_file'], config['ollama']['url'], config['ollama']['model'])