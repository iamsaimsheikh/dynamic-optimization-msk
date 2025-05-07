import re

MASKING_RULES = [
    # Mask Kafka message bytes to avoid JSON decode issues
    (re.compile(r"messages=b'[^']*'"), "messages=<BYTES>"),

    (re.compile(r"\b\d{2}:\d{2}:\d{2}\b"), "<TIME>"),
    (re.compile(r"kafka-python-\d+\.\d+\.\d+-[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}", re.IGNORECASE),
     "kafka-python-<VERSION>-<UUID>"),
    (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-\b", re.IGNORECASE), "<UUID_PARTIAL>"),
    (re.compile(r"-(?:[a-f0-9]{4})-", re.IGNORECASE), "<UUID_SEGMENT>"),
    (re.compile(r"\b[a-f0-9]{4,8}\b", re.IGNORECASE), "<HEX_SMALL>"),
    (re.compile(
        r"SyncGroupRequest_v\d+\(group='([^']{1,100})', generation_id=\d{1,10}, "
        r"member_id='([^']{1,50})-[0-9a-f-]+', group_assignment=\[\]\)"
    ),
     "SyncGroupRequest_v<NUM>(group='<GROUP>', generation_id=<NUM>, member_id='<MEMBER>-<UUID>', group_assignment=[])")
]
