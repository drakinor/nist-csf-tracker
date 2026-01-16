import requests
r = requests.get('https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf')
print(f'Content-Type: {r.headers.get("content-type")}')
print(f'URL ends with .pdf: {r.url.endswith(".pdf")}')
print(f'First 20 bytes: {r.content[:20]}')
