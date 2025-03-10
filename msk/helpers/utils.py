import re

MASKING_RULES = [
    # General numbers (restrict to prevent excessive matching)
    (re.compile(r"\b\d{1,15}\b"), "<NUM>"),  
    
    # Full UUIDs (Added atomic grouping for safety)
    (re.compile(r"\b(?>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b", re.IGNORECASE), "<UUID>"),  
    
    # IPv4 Addresses (Prevent overly broad matches)
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b(?!\.\d)"), "<IP>"),  
    
    # MAC Addresses (Improved efficiency)
    (re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b"), "<MAC>"),  
    
    # Email Addresses (Restricted username & domain)
    (re.compile(r"\b[a-zA-Z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,255}\.[A-Za-z]{2,10}\b"), "<EMAIL>"),  
    
    # URLs (Use non-greedy matching to prevent runaway behavior)
    (re.compile(r"https?://(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,10}(?:/\S*)?", re.IGNORECASE), "<URL>"),  
    
    # 12-character Hexadecimal (Avoid partial MAC conflict)
    (re.compile(r"\b[A-Fa-f0-9]{12}\b"), "<HEX>"),  
    
    # Datetime format YYYY-MM-DD HH:MM:SS (Prevent excessive backtracking)
    (re.compile(r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b(?!\d)"), "<TIMESTAMP>"),  
    
    # Date format YYYY-MM-DD
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\b(?!\d)"), "<DATE>"),  
    
    # Time format HH:MM:SS
    (re.compile(r"\b\d{2}:\d{2}:\d{2}\b(?!\d)"), "<TIME>"),  
    
    # Kafka Consumer Member ID (Ensuring proper segmentation)
    (re.compile(r"kafka-python-\d+\.\d+\.\d+-[0-9a-f]+(?:-[0-9a-f]+){3}", re.IGNORECASE), "kafka-python-<VERSION>-<UUID>"),  
    
    # Partial UUIDs (Avoid ambiguous matches)
    (re.compile(r"\b[a-f0-9]{8}-[a-f0-9]{4}-\b", re.IGNORECASE), "<UUID_PARTIAL>"),  
    
    # Isolated UUID segments
    (re.compile(r"-[a-f0-9]{4}-", re.IGNORECASE), "<UUID_SEGMENT>"),  
    
    # Small random hex strings (Limited range to prevent excessive matches)
    (re.compile(r"\b[a-f0-9]{4,8}\b", re.IGNORECASE), "<HEX_SMALL>"),  
    
    # Kafka SyncGroupRequest (Adjusted grouping to prevent runaway processing)
    (re.compile(
        r"SyncGroupRequest_v\d+\(group='([^']{1,100})', generation_id=\d+, member_id='([^']{1,50})-[0-9a-f-]+', group_assignment=\[\]\)", 
        re.IGNORECASE
    ), 
    "SyncGroupRequest_v<NUM>(group='<GROUP>', generation_id=<NUM>, member_id='<MEMBER>-<UUID>', group_assignment=[])")
]
