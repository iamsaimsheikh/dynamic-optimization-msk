import re

MASKING_RULES = [
    (re.compile(r"\b\d+\b"), "<NUM>"),  # General numbers
    (re.compile(r"\b(?:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b", re.IGNORECASE), "<UUID>"),  # Full UUIDs
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "<IP>"),  # IPv4 Addresses
    (re.compile(r"\b(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b"), "<MAC>"),  # MAC Addresses
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "<EMAIL>"),  # Email Addresses
    (re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"), "<URL>"),  # URLs
    (re.compile(r"\b(?:[A-Fa-f0-9]{2}:){5}[A-Fa-f0-9]{2}\b"), "<MAC>"),  # MAC Addresses
    (re.compile(r"\b[A-Fa-f0-9]{12}\b"), "<HEX>"),  # 12-character Hexadecimal
    (re.compile(r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b"), "<TIMESTAMP>"),  # Datetime format YYYY-MM-DD HH:MM:SS
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), "<DATE>"),  # Date format YYYY-MM-DD
    (re.compile(r"\b\d{2}:\d{2}:\d{2}\b"), "<TIME>"),  # Time format HH:MM:SS
    (re.compile(r"kafka-python-\d+\.\d+\.\d+-[0-9a-f]+-[0-9a-f]+-[0-9a-f]+-[0-9a-f]+", re.IGNORECASE), "kafka-python-<VERSION>-<UUID>"),  # Kafka Consumer Member ID
    (re.compile(r"\b[a-f0-9]{8}-[a-f0-9]{4}-\b", re.IGNORECASE), "<UUID_PARTIAL>"),  # Partial UUIDs
    (re.compile(r"-[a-f0-9]{4}-", re.IGNORECASE), "<UUID_SEGMENT>"),  # Isolated UUID segments
    (re.compile(r"\b[a-f0-9]{4,8}\b", re.IGNORECASE), "<HEX_SMALL>"),  # Small random hex strings
    (re.compile(r"SyncGroupRequest_v\d+\(group='([^']+)', generation_id=\d+, member_id='([^']+)-[0-9a-f-]+', group_assignment=\[\]\)"), "SyncGroupRequest_v<NUM>(group='<GROUP>', generation_id=<NUM>, member_id='<MEMBER>-<UUID>', group_assignment=[])")  # Kafka SyncGroupRequest
]