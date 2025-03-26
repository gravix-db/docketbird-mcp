from mcp.server.fastmcp import FastMCP
import requests
import os
import json
from pathlib import Path

# Initialize FastMCP server with environment variables
mcp = FastMCP("docketbird")

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()

# API Configuration
BASE_URL = "https://api.docketbird.com"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('DOCKETBIRD_API_KEY')}"
}

# Helper function for making requests
def make_request(endpoint, params=None):
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()



@mcp.tool()
async def get_case_details(case_id: str) -> str:
    """Get comprehensive details about a case including all documents.
    
    Args:
        case_id: The DocketBird case ID to retrieve details for.
                Format: {court_id}-{district}:{year}-{type}-{number}
                Example: txnd-3:2007-cv-01697
                
                court_id: Court identifier from the list below:
                Federal Courts:
                - Circuit Courts of Appeals:
                  - ca1: 1st Circuit
                  - ca2: 2nd Circuit
                  - ca3: 3rd Circuit
                  - ca4: 4th Circuit
                  - ca5: 5th Circuit
                  - ca6: 6th Circuit
                  - ca7: 7th Circuit
                  - ca8: 8th Circuit
                  - ca9: 9th Circuit
                  - ca10: 10th Circuit
                  - ca11: 11th Circuit
                  - cadc: D.C. Circuit
                  - cafc: Federal Circuit

                - District Courts:
                  - cacd: Central District of California
                  - cand: Northern District of California
                  - nysd: Southern District of New York
                  - ilnd: Northern District of Illinois
                  - caed: Eastern District of California
                  - njd: District of New Jersey
                  - txed: Eastern District of Texas
                  - flsd: Southern District of Florida
                  - dcd: District of Columbia
                  - mied: Eastern District of Michigan

                - Bankruptcy Courts (partial list):
                  - txsb: Southern District of Texas
                  - deb: District of Delaware
                  - nvb: District of Nevada
                  - flsb: Southern District of Florida
                  - nysb: Southern District of New York
                  - cacb: Central District of California
                
                district: District number (e.g. 3, 1, 5)
                year: Year case was filed (e.g. 2007, 2023)
                type: Case type (e.g. cv for civil, wr for writ)
                number: Case number (e.g. 01697, 08028)
                For more information on courts, see list_courts_and_types tool

                

    Returns:
        A formatted string containing comprehensive case details including:
        - Basic case information (title, court, filing dates)
        - Party information
        - Document list with metadata
        - URLs and identifiers
    
    Example:
        >>> get_case_details("nysd-1:2023-cv-12345")
        === CASE DETAILS ===
        Title: Smith v. Company Inc
        Court: nysd
        Filed: 2023-01-15
        ...
    """
    # Get case details and documents
    case_details = make_request(f"/cases/{case_id}")
    docs_response = make_request(f"/documents?case_id={case_id}")
    
    if not case_details or not docs_response:
        return "Failed to retrieve case details or documents"
    
    # Get case data safely using .get()
    case = case_details.get('data', {}).get('case', {})
    
    # Format basic case info
    output = []
    output.append("=== CASE DETAILS ===")
    output.append(f"Title: {case.get('title', 'N/A')}")
    output.append(f"Court: {case.get('court_id', 'N/A')}")
    output.append(f"Filed: {case.get('date_filed', 'N/A')}")
    output.append(f"Closed: {case.get('date_closed', 'N/A')}")
    output.append(f"URL: {case.get('url', 'N/A')}")
    output.append(f"PACER Case ID: {case.get('pacer_case_id', 'N/A')}")
    output.append(f"Client Code: {case.get('client_code', 'N/A')}")
    
    # Add parties if available
    parties = case_details.get('data', {}).get('parties', [])
    if parties:
        output.append("\n=== PARTIES ===")
        for party in parties:
            output.append(f"- {party.get('name', 'N/A')} ({party.get('type', 'N/A')})")
    
    # Add documents if available
    documents = docs_response.get('data', {}).get('documents', [])
    if documents:
        output.append("\n=== DOCUMENTS ===")
        for idx, doc in enumerate(documents, 1):
            output.append(f"\nDocument #{idx}")
            output.append(f"Document ID: {doc.get('id', 'N/A')}")
            output.append(f"Title: {doc.get('title', 'N/A')}")
            output.append(f"Filed: {doc.get('filing_date', 'N/A')}")
            output.append(f"Restricted: {doc.get('restricted', 'N/A')}")
            output.append(f"Primary Docket Sheet Number: {doc.get('primary_docket_sheet_number', 'N/A')}")
            output.append(f"PACER Document URL: {doc.get('pacer_document_url', 'N/A')}")
            output.append(f"Downloaded: {doc.get('downloaded', 'N/A')}")
            output.append(f"DocketBird Document URL: {doc.get('docketbird_document_url', 'N/A')}")
            output.append(f"Custom Filename: {doc.get('custom_filename', 'N/A')}")
            if doc.get('description'):
                output.append(f"Description: {doc.get('description')}")
    
    return "\n".join(output)

@mcp.tool()
async def search_case_documents(case_id: str, search_term: str) -> str:
    """Search for specific documents within a case using a search term.
    
    Args:
        case_id: The DocketBird case ID to search in
        search_term: Term to search for in document titles and descriptions
    """
    docs_response = make_request(f"/documents?case_id={case_id}")
    
    if not docs_response:
        return "Failed to retrieve case documents"
    
    documents = docs_response.get('data', {}).get('documents', [])
    if not documents:
        return "No documents found for this case"
    
    # Search through documents
    search_term = search_term.lower()
    matching_docs = []
    
    for doc in documents:
        title = doc.get('title', '').lower()
        desc = doc.get('description', '').lower()
        
        if search_term in title or search_term in desc:
            doc_info = [
                f"\nDocument ID: {doc.get('id', 'N/A')}",
                f"Title: {doc.get('title', 'N/A')}",
                f"Filed: {doc.get('filing_date', 'N/A')}",
                f"DocketBird URL: {doc.get('docketbird_document_url', 'N/A')}"
            ]
            if doc.get('description'):
                doc_info.append(f"Description: {doc.get('description')}")
            matching_docs.append("\n".join(doc_info))
    
    if not matching_docs:
        return f"No documents found matching search term: {search_term}"
    
    output = [f"Found {len(matching_docs)} matching documents:"]
    output.extend(matching_docs)
    return "\n".join(output)

@mcp.tool()
async def download_available_files(case_id: str, save_path: str) -> str:
    """Download all available S3 documents for a specific case.
    
    Args:
        case_id: The DocketBird case ID to download documents from
        save_path: Absolute path where files should be saved. It should be a folder path.
    """
    # Get documents for the case
    docs_response = make_request(f"/documents?case_id={case_id}")
    
    if not docs_response:
        return "Failed to retrieve case documents"
    
    documents = docs_response.get('data', {}).get('documents', [])
    if not documents:
        return "No documents found for this case"
    
    # Track download results
    download_results = []
    
    for doc in documents:
        doc_id = doc.get('id', 'N/A')
        doc_title = doc.get('title', 'N/A')
        s3_url = doc.get('docketbird_document_url')
        
        if s3_url:
            result = download_s3_document(s3_url, save_path)
            download_results.append(f"Document: {doc_title} (ID: {doc_id})\nStatus: {result}\n")
    
    # Prepare result message
    result = []
    result.append(f"\nDownload Results for Case {case_id}:")
    result.append(f"Save Location: {save_path}\n")
    result.append("=== Individual File Results ===")
    result.extend(download_results if download_results else ["No documents were available for download"])
    
    return "\n".join(result)

@mcp.tool()
async def download_document_by_id(document_id: str, save_path: str) -> str:
    """Download a specific document by its docketbird ID if an S3 link is available.
    
    Args:
        document_id: The DocketBird document ID to download
        save_path: Absolute path where the file should be saved. It should be a folder path.
    """
    # Get document details
    doc_response = make_request(f"/documents/{document_id}")
    
    if not doc_response:
        return f"Failed to retrieve document with ID: {document_id}"
    
    document = doc_response.get('data', {}).get('document', {})
    if not document:
        return f"Document with ID {document_id} not found"
    
    doc_title = document.get('title', 'N/A')
    s3_url = document.get('docketbird_document_url')
    
    if not s3_url:
        return f"No downloadable S3 link available for document: {doc_title} (ID: {document_id})"
    
    # Download the document
    result = download_s3_document(s3_url, save_path)
    
    return f"Document: {doc_title} (ID: {document_id})\nStatus: {result}"

@mcp.tool()
async def list_cases(scope: str) -> str:
    """Get a list of cases belonging to an account.
    
    Args:
        scope: Either "company" or "user" to specify whose cases to retrieve
    """
    # Validate scope parameter
    if scope not in ["company", "user"]:
        return "Error: scope must be either 'company' or 'user'"
    
    # Make request to /cases endpoint with scope parameter
    response = make_request(f"/cases?scope={scope}")
    
    if not response:
        return "Failed to retrieve cases"
    
    cases = response.get('data', {}).get('cases', [])
    if not cases:
        return f"No cases found for {scope} scope"
    
    # Format output
    output = []
    output.append(f"\n=== {scope.upper()} CASES ===\n")
    
    for case in cases:
        output.append(f"ID: {case.get('id', 'N/A')}")
        output.append(f"Title: {case.get('title', 'N/A')}")
        output.append(f"Court: {case.get('court_id', 'N/A')}")
        output.append(f"Case Number: {case.get('case_number', 'N/A')}")
        output.append(f"Date Filed: {case.get('date_filed', 'N/A')}")
        output.append("")  # Empty line between cases
    
    return "\n".join(output)

@mcp.tool()
async def list_courts_and_types() -> str:
    """Get a comprehensive list of all available courts and case types.
    
    Returns:
        A formatted string containing:
        - All available courts grouped by type (Circuit, District, Bankruptcy, etc.)
        - Common case types and their descriptions with example case numbers
    
    Example:
        >>> list_courts_and_types()
        === COURTS ===
        Circuit Courts:
        - ca1: 1st Circuit Court of Appeals
        ...
        
        District Courts:
        - cacd: Central District of California
        ...
        
        === CASE TYPES ===
        - cv: Civil Case
        - cr: Criminal Case
        - mc: Miscellaneous Case
        ...
    """
    
    try:
        # Read courts from courts.json using relative path
        courts_path = SCRIPT_DIR / 'courts.json'
        case_types_path = SCRIPT_DIR / 'case_types.json'
        
        with open(courts_path, 'r') as f:
            courts_data = json.load(f)
            
        # Read case types from case_types.json
        with open(case_types_path, 'r') as f:
            case_types_data = json.load(f)
            
        # Initialize court type categories
        circuit_courts = []
        district_courts = []
        bankruptcy_courts = []
        state_courts = []
        other_courts = []
        
        # Categorize courts
        for court in courts_data['courts']:
            name = court['court_name']
            code = court['value']
            entry = f"- {code}: {name}"
            
            if "Circuit Court" in name or "Circuit" in name and "District" not in name:
                circuit_courts.append(entry)
            elif "Bankruptcy" in name:
                bankruptcy_courts.append(entry)
            elif "District" in name and "Bankruptcy" not in name:
                district_courts.append(entry)
            elif any(state in name for state in ["Superior Court", "Supreme Court", "County Court"]):
                state_courts.append(entry)
            else:
                other_courts.append(entry)
        
        # Build output
        output = []
        output.append("=== COURTS ===\n")
        
        if circuit_courts:
            output.append("Circuit Courts:")
            output.extend(sorted(circuit_courts))
            output.append("")
            
        if district_courts:
            output.append("District Courts:")
            output.extend(sorted(district_courts))
            output.append("")
            
        if bankruptcy_courts:
            output.append("Bankruptcy Courts:")
            output.extend(sorted(bankruptcy_courts))
            output.append("")
            
        if state_courts:
            output.append("State Courts:")
            output.extend(sorted(state_courts))
            output.append("")
            
        if other_courts:
            output.append("Other Courts:")
            output.extend(sorted(other_courts))
            output.append("")
        
        # Add case types from case_types.json
        output.append("=== CASE TYPES ===")
        for case_type in case_types_data['case_types']:
            output.append(f"- {case_type['abbreviature']}: {case_type['name']}")
            output.append(f"  Example: {case_type['example']}")
            output.append("")
        
        return "\n".join(output)
        
    except FileNotFoundError as e:
        if 'courts.json' in str(e):
            return "Error: courts.json file not found"
        elif 'case_types.json' in str(e):
            return "Error: case_types.json file not found"
        return f"Error: {str(e)}"
    except json.JSONDecodeError:
        return "Error: Invalid JSON format in configuration files"
    except Exception as e:
        return f"Error: {str(e)}"

def download_s3_document(url: str, save_location: str) -> str:
    """Download a document from S3 using a pre-signed URL.

    Args:
        url: Pre-signed S3 URL for the document
        save_location: Directory path where the file should be saved (absolute path)

    Returns:
        str: Success message or error description
    """
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # Extract filename from S3 URL
            filename = url.split('/')[-1].split('?')[0]
            # Convert to absolute path if not already
            import os
            save_location = os.path.abspath(os.path.expanduser(save_location))
            full_path = os.path.join(save_location, filename)
            
            # Create directory if it doesn't exist
            os.makedirs(save_location, exist_ok=True)
            
            with open(full_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return f"Successfully downloaded to {full_path}"
        else:
            return f"HTTP Error {response.status_code}: Failed to download file"
    except Exception as e:
        return f"Error downloading file: {str(e)}"

if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv('DOCKETBIRD_API_KEY'):
        print("Error: DOCKETBIRD_API_KEY environment variable is required")
        print("Please set it using: export DOCKETBIRD_API_KEY=your_api_key")
        exit(1)
        
    # Run the MCP server
    mcp.run(transport='stdio') 