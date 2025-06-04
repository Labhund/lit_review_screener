import bibtexparser
import json

def parse_bibtex(input_file, output_file):
    with open(input_file, 'r') as bibfile:
        bib_database = bibtexparser.load(bibfile)

    references = []
    for entry in bib_database.entries:
        reference = {
            "bib_key": entry.get("ID"),
            "doi": entry.get("doi"),
            "pmid": entry.get("pmid"),
            "title": entry.get("title"),
            "author": entry.get("author"),
            "year": entry.get("year"),
            "journal": entry.get("journal"),
            "abstract": entry.get("abstract"),
            "status": "parsed"
        }
        references.append(reference)

    with open(output_file, 'w') as jsonfile:
        json.dump(references, jsonfile, indent=2)

if __name__ == "__main__":
    input_path = "data/input/example_search.bib"
    output_path = "data/output/references_parsed.json"
    parse_bibtex(input_path, output_path)