import time
import urllib.request

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        return None

opener = urllib.request.build_opener(NoRedirect)

for i in range(10):
    time.sleep(6)
    try:
        req = urllib.request.Request('https://heliatech.online/templates/', headers={'User-Agent': 'Mozilla/5.0'})
        resp = opener.open(req)
        print(f"Attempt {i+1}: Status {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"Attempt {i+1}: Redirect {e.code} to {e.headers.get('Location')}")
        if e.code in (301, 302, 307, 308):
            print("SUCCESS! Cloudflare Edge redirect is active!")
            break
    except Exception as e:
        print(f"Attempt {i+1}: Error {e}")
