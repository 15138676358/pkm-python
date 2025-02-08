import requests
import time

def get_crossref_data(doi):
    """通过Crossref API获取文献基本信息及参考文献的DOI"""
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json().get("message", {})
        
        # 提取基本信息
        title = data.get("title", ["[Unknown Title]"])[0]
        authors = [f'{author.get("given", "")} {author.get("family", "")}'.strip() 
                   for author in data.get("author", [])]
        date_parts = data.get("published", {}).get("date-parts", [[None]])[0]
        year = date_parts[0] if date_parts else None
        journal = data.get("container-title", ["[Unknown Journal]"])[0]
        
        # 提取参考文献的DOI
        references = []
        for ref in data.get("reference", []):
            ref_doi = ref.get("DOI")
            ref_title = ref.get("article-title", "[Unknown Title]")
            references.append({"title": ref_title, "doi": ref_doi})
        
        return {
            "title": title,
            "doi": doi,
            "authors": authors,
            "year": year,
            "journal": journal,
            "references": references
        }
    except Exception as e:
        return {"error": f"Crossref API Error: {str(e)}"}

def get_citations(doi):
    """通过OpenAlex API获取被引文献信息"""
    url = f"https://api.openalex.org/works?filter=cites:{doi}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        citations = []
        for result in data.get("results", []):
            citation_doi = result.get("doi", "").split("/")[-1] if result.get("doi") else None
            citation_title = result.get("title", "[Unknown Title]")
            citations.append({"title": citation_title, "doi": citation_doi})
        return citations
    except Exception as e:
        return {"error": f"OpenAlex API Error: {str(e)}"}

def fetch_literature_info(doi):
    """整合Crossref和OpenAlex数据"""
    time.sleep(1)  # 避免请求速率过快
    crossref_data = get_crossref_data(doi)
    if "error" in crossref_data:
        return crossref_data
    
    citations = get_citations(doi)
    crossref_data["citations"] = citations
    return crossref_data

# 示例使用
if __name__ == "__main__":
    sample_doi = "10.1038/nature12373"    # 替换为你的DOI
    result = fetch_literature_info(sample_doi)
    print(result)