import yaml
def load_rules(path): 
    with open(path,'r') as f: return yaml.safe_load(f) or {}
def _redact_inplace(doc, parts):
    if not parts: return
    head, *tail = parts
    if isinstance(doc, dict):
        if head.endswith(']'):
            field, rest = head.split('[',1); rest=rest.rstrip(']')
            if field in doc and isinstance(doc[field], list):
                if rest=='*':
                    for item in doc[field]: _redact_inplace(item, tail)
        else:
            if head in doc:
                if tail: _redact_inplace(doc[head], tail)
                else: del doc[head]
    elif isinstance(doc, list) and head in ('*',''):
        for item in doc: _redact_inplace(item, tail)
def apply_policy(event, rules):
    t=event.get('type')
    deny=set(rules.get('deny_event_types',[]))
    allow=set(rules.get('allow_event_types',[])) if rules.get('allow_event_types') else None
    if t in deny: return None
    if allow is not None and t not in allow: return None
    for path in rules.get('redact_fields',[]):
        parts=[p for p in path.replace(']','].').split('.') if p]
        _redact_inplace(event, parts)
    return event
