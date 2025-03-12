import re

MASKING_RULES = [
    (re.compile(r"\b\d{2}:\d{2}:\d{2}\b"), "<TIME>"),  # Time format HH:MM:SS
    (re.compile(r"kafka-python-\d+\.\d+\.\d+-[0-9a-f]{8}-(?>[0-9a-f]{4}-){3}[0-9a-f]{12}", re.IGNORECASE), 
     "kafka-python-<VERSION>-<UUID>"),  # Kafka Consumer Member ID (uses atomic grouping for efficiency)
    (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-\b", re.IGNORECASE), "<UUID_PARTIAL>"),  # Partial UUIDs
    (re.compile(r"-(?>[a-f0-9]{4})-", re.IGNORECASE), "<UUID_SEGMENT>"),  # Isolated UUID segments (atomic group)
    (re.compile(r"\b[a-f0-9]{4,8}\b", re.IGNORECASE), "<HEX_SMALL>"),  # Small random hex strings
    (re.compile(
        r"SyncGroupRequest_v\d+\(group='(?>[^']{1,100})', generation_id=\d{1,10}, "
        r"member_id='(?>[^']{1,50})-[0-9a-f-]+', group_assignment=\[\]\)"
    ), "SyncGroupRequest_v<NUM>(group='<GROUP>', generation_id=<NUM>, member_id='<MEMBER>-<UUID>', group_assignment=[])")  # Kafka SyncGroupRequest (bounded group sizes)
]
