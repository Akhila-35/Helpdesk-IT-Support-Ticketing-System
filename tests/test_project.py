def login(c,email,password,form=False):
    r=c.post('/auth/login',data={'username':email,'password':password}) if form else c.post('/auth/login/json',json={'email':email,'password':password})
    assert r.status_code==200;return r.json()['access_token']
def h(t):return {'Authorization':f'Bearer {t}'}
def test_auth_json_and_swagger_form(client):
    assert login(client,'admin@example.com','AdminPass123!');assert login(client,'admin@example.com','AdminPass123!',True)
def test_high_sla_and_assignment_and_comments(client):
    req=login(client,'requester@example.com','RequesterPass123!');admin=login(client,'admin@example.com','AdminPass123!');eng=login(client,'engineer@example.com','EngineerPass123!')
    r=client.post('/tickets',headers=h(req),json={'title':'VPN down','description':'Cannot connect','priority':'high','category_id':1});assert r.status_code==201;t=r.json();assert t['status']=='open'
    from datetime import datetime
    delta=(datetime.fromisoformat(t['sla_breach_deadline'])-datetime.fromisoformat(t['created_at'])).total_seconds();assert 14399<=delta<=14401
    r=client.post(f"/tickets/{t['id']}/assign",headers=h(admin),json={'engineer_id':2});assert r.status_code==200
    r=client.post(f"/tickets/{t['id']}/comments",headers=h(eng),json={'body':'Working on it'});assert r.status_code==201
    r=client.patch(f"/tickets/{t['id']}/status",headers=h(eng),json={'status':'in_progress'});assert r.status_code==200
    r=client.patch(f"/tickets/{t['id']}/status",headers=h(eng),json={'status':'resolved'});assert r.status_code==200
    r=client.patch(f"/tickets/{t['id']}/status",headers=h(req),json={'status':'closed'});assert r.status_code==200
