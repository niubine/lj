import requests

url = "https://api.tboxconf.com/api/disk/com/conf"
headers = {
  "X-Requested-With": "com.linkbox.app",
  "Accept-Encoding": "gzip",
  "Content-Type": "application/x-www-form-urlencoded",
  "Host": "api.tboxconf.com",
  "Connection": "Keep-Alive",
  "User-Agent": "okhttp/4.9.3"
}
data = """anm=oarplayer&request_data=xxxxxxaE08Pe6gsi5%2Fkz%0A&sign=ca93aba2979a794c2f01d3a958827421"""

res = requests.post(url, headers=headers, data=data)
print(res.text)


import base64, re
import hashlib

from Crypto.Cipher import AES

x = "rU18efAXUbdiaE7k"
# x = "Rz12efBXGbdiaE8k"
# x = "Rz18efBXUbdia07k"
# x = "Rz18efBXUbdiaE8k"
# x = "Rz18efBXUbdiaE7k"
# x = "Rz16efBXGEdiaZ9k"
KEY = x.encode()
IV = x.encode()
BLOCK = 16

def b64_decode_flexible(s: str) -> bytes:
    s = re.sub(r"\s+", "", s.strip()) 
    s = s.replace("-", "+").replace("_", "/")
    s += "=" * (-len(s) % 4)             
    return base64.b64decode(s)

def decrypt_linkbox_style(b64_cipher: str) -> bytes:
    raw = b64_decode_flexible(b64_cipher)
    print("decoded_len =", len(raw), "mod16 =", len(raw) % 16, "tail_byte =", hex(raw[-1]))

    if len(raw) % BLOCK != 0 and (len(raw) - 1) % BLOCK == 0:
        raw = raw[:-1]

    if len(raw) % BLOCK != 0:
        raise ValueError(f"{len(raw)}")

    pt = AES.new(KEY, AES.MODE_CBC, IV).decrypt(raw)
    return pt

b64 = """/NdVwnP1o81LUYRlMKxxxxxxxxxxxxxxx3nL4yqetnVswMVJr8IFwI04fZLo9
ftqCWubxu1jNuYwPweeq4xxxxxxxxxxxxxxxxxx/HkERgDAJNzxtNY6P/J94TV7qL9Zc5Bn0
yNWKAd1p8nOmBoAci5vzv2JT+c34fG++ei9te0kNqVyCCS1Zet1+u5CpwPK8cpQizaFy1LuqQqS1
kwPeTWU="""
pt = decrypt_linkbox_style(b64)
print(pt)
text = pt.rstrip(b"\x00").decode("utf-8", errors="replace")
print("plain(text) =", text)

h = """anm=oarplayer&request_data=/NdVwnP1o81LUYRlMKxxxxxxxxxxxxxxx3nL4yqetnVswMVJr8IFwI04fZLo9
ftqCWubxu1jNuYwPweeq4xxxxxxxxxxxxxxxxxx/HkERgDAJNzxtNY6P/J94TV7qL9Zc5Bn0
yNWKAd1p8nOmBoAci5vzv2JT+c34fG++ei9te0kNqVyCCS1Zet1+u5CpwPK8cpQizaFy1LuqQqS1
kwPeTWU=
&PM9GikcERfy2yi6f"""

print(hashlib.md5(h.encode()).hexdigest())  # sign=ca93aba2979a794c2f01d3a958827421

# anm=oarplayer&request_data=/NdVwnP1o81LUYRlMKxxxxxxxxxxxxxxx3nL4yqetnVswMVJr8IFwI04fZLo9
ftqCWubxu1jNuYwPweeq4xxxxxxxxxxxxxxxxxx/HkERgDAJNzxtNY6P/J94TV7qL9Zc5Bn0
yNWKAd1p8nOmBoAci5vzv2JT+c34fG++ei9te0kNqVyCCS1Zet1+u5CpwPK8cpQizaFy1LuqQqS1
kwPeTWU=&sign=ca93aba2979a794c2f01d3a958827421


