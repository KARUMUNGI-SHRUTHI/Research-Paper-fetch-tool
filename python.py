import requests
import csv
import re
import argparse

def fetch_pubmed_papers(query: str, debug: bool = False):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmode=json"
    response = requests.get(url)
    if debug:
        print("PubMed API Response:", response.json())
    return response.json().get("esearchresult", {}).get("idlist", [])

def fetch_paper_details(pubmed_id: str, debug: bool = False):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pubmed_id}&retmode=json"
    response = requests.get(url)
    if debug:
        print(f"Details for {pubmed_id}:", response.json())
    return response.json()

def is_non_academic(author_info: str):
    biotech_keywords = ["pharma", "biotech", "laboratories", "inc", "ltd"]
    return any(re.search(rf"\b{word}\b", author_info, re.IGNORECASE) for word in biotech_keywords)

def save_to_csv(results, filename="results.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["PubmedID", "Title", "Publication Date", "Non-academic Author(s)", "Company Affiliation(s)"])
        for row in results:
            writer.writerow(row)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Fetch research papers from PubMed.")
    parser.add_argument("query", type=str, help="Search query for PubMed")
    parser.add_argument("-f", "--file", type=str, help="Filename to save results (optional)")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    return parser.parse_args()

def main():
    args = parse_arguments()
    pubmed_ids = fetch_pubmed_papers(args.query, args.debug)
    
    results = []
    for pubmed_id in pubmed_ids:
        details = fetch_paper_details(pubmed_id, args.debug)
        title = details.get("result", {}).get(pubmed_id, {}).get("title", "N/A")
        pub_date = details.get("result", {}).get(pubmed_id, {}).get("pubdate", "N/A")

        results.append([pubmed_id, title, pub_date])

    filename = args.file if args.file else "results.csv"
    save_to_csv(results, filename)
    print(f"Results saved to {filename}")

if __name__ == "__main__":
    main()