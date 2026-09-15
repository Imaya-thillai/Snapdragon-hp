import requests

try:
    files = {'image': ('test.jpg', b'dummydata', 'image/jpeg')}
    data = {'claim_type': 'tree_planting'}
    res = requests.post("http://127.0.0.1:8000/api/verify_eco_claim", files=files, data=data)
    print("STATUS:", res.status_code)
    print("BODY:", res.text)
except Exception as e:
    print("FAILED:", e)
