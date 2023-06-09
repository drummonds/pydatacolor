import urllib3
import numpy as np
import ssl
from time import sleep

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "http://10.0.0.178:8080/shot.jpg"

http = urllib3.PoolManager()
# sleep(1)
# print(f"Status: {resp.status}")  # Don't print in a sub process
for i in range(10):
    resp = http.request("GET", url)
    with open(f"test{i:2d}.jpg", "wb") as f:
        f.write(resp.data)
