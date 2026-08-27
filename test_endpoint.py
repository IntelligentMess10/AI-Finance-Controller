import requests

for exc_id in [1, 2, 3, 4]:
    resp = requests.post(f'http://127.0.0.1:8000/exceptions/{exc_id}/investigate')
    print(f'Exception {exc_id}: {resp.status_code}')
    if resp.status_code == 200:
        d = resp.json()
        print('  Status:', d.get('status'))
        print('  Classification:', d.get('classification'))
        print('  Confidence:', d.get('confidence'))
        print('  Explanation:', d.get('explanation')[:100] + '...')
    else:
        print('Error:', resp.text)
    print()