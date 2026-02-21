import requests
from datetime import datetime
from typing import List
from scripts.daily_ai.models import PaperItem
from scripts.daily_ai.fetchers.base import BaseFetcher

class ArxivFetcher(BaseFetcher):
    def fetch(self, max_results: int = 20) -> List[PaperItem]:
        papers = []
        # cs.CL (Computation and Language), cs.AI, cs.LG, cs.CV
        query = "cat:cs.CL OR cat:cs.AI OR cat:cs.LG OR cat:cs.CV"
        url = f"http://export.arxiv.org/api/query?search_query={query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
        
        try:
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                ns = {'arxiv': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('arxiv:entry', ns):
                    title = entry.find('arxiv:title', ns).text.strip() if entry.find('arxiv:title', ns) is not None else ""
                    title = " ".join(title.split())
                    
                    summary = entry.find('arxiv:summary', ns).text.strip() if entry.find('arxiv:summary', ns) is not None else ""
                    summary = " ".join(summary.split())
                    
                    link = ""
                    for link_elem in entry.findall('arxiv:link', ns):
                        if link_elem.attrib.get('title') == 'pdf':
                            link = link_elem.attrib.get('href', '')
                            break
                        if not link and link_elem.attrib.get('rel') == 'alternate':
                            link = link_elem.attrib.get('href', '')
                            
                    published = entry.find('arxiv:published', ns).text if entry.find('arxiv:published', ns) is not None else ""
                    
                    authors = []
                    for author in entry.findall('arxiv:author', ns):
                        name = author.find('arxiv:name', ns).text if author.find('arxiv:name', ns) is not None else ""
                        if name: authors.append(name)
                        
                    papers.append(PaperItem(
                        title=title,
                        url=link,
                        source="arXiv",
                        description=summary,
                        published_date=published,
                        authors=authors
                    ))
        except Exception as e:
            print(f"[ERROR] arXiv 抓取失败: {e}")
            
        return papers
