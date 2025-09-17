from cloud.policy.engine import apply_policy

def test_redact():
    e={'type':'traffic_violation','location':{'lat':0,'lon':0},'payload':{'plates':[{'text':'ABC123'}]},'source':'edge','timestamp':0.0}
    r={'redact_fields':['payload.plates[*].text']}
    out=apply_policy(e,r)
    assert 'text' not in out['payload']['plates'][0]
