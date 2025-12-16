import urllib.request

url = 'https://github.com/gamijoam/ferreteria/releases/download/v1.0.46/update_ferreteria.zip'

try:
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    
    print(f'Testing URL: {url}')
    response = urllib.request.urlopen(req, timeout=10)
    
    print(f'✓ Status: {response.status}')
    print(f'✓ Size: {response.headers.get("Content-Length")} bytes')
    print('✓ URL is accessible!')
    
except urllib.error.HTTPError as e:
    print(f'✗ HTTP Error: {e.code} - {e.reason}')
except Exception as e:
    print(f'✗ Error: {e}')
