import requests

base_url = 'http://127.0.0.1:8000'
exceptions = []
skip = 0
page_size = 100
while True:
    exceptions_response = requests.get(
        f'{base_url}/reconciliation/exceptions',
        params={'skip': skip, 'limit': page_size},
        timeout=30,
    )
    exceptions_response.raise_for_status()
    page = exceptions_response.json()
    exceptions.extend(page)
    if len(page) < page_size:
        break
    skip += page_size

print(f'Found {len(exceptions)} exceptions')

for exception in exceptions:
    exc_id = exception['id']
    resp = requests.post(f'{base_url}/exceptions/{exc_id}/investigate', timeout=120)
    print(f'Exception {exc_id}: {resp.status_code}')
    if resp.status_code == 200:
        d = resp.json()
        print('  Status:', d.get('status'))
        print('  Classification:', d.get('classification'))
        print('  Confidence:', d.get('confidence'))
        explanation = d.get('explanation') or ''
        print('  Explanation:', explanation[:100] + ('...' if len(explanation) > 100 else ''))
    else:
        print('Error:', resp.text)
    print()