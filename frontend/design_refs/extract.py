import re, json, gzip, base64, os
fname = [n for n in os.listdir(".") if n.endswith(".html")][0]
src = open(fname, encoding="utf-8", errors="replace").read()
m = re.search(r'<script type="__bundler/manifest">(.*?)</script>', src, re.S)
manifest = json.loads(m.group(1))
order = json.loads(re.search(r'<script type="__bundler/page_order">(.*?)</script>', src, re.S).group(1))
out = r"C:\Users\HP\AppData\Local\Temp\opencode\design_pages"
os.makedirs(out, exist_ok=True)
print("pages", len(order), "manifest", len(manifest))
for i, uid in enumerate(order):
    e = manifest.get(uid)
    if not e: continue
    data = base64.b64decode(e["data"])
    if e.get("compressed"): data = gzip.decompress(data)
    text = data.decode("utf-8", errors="replace")
    open(os.path.join(out, f"{i:02d}_{uid}.html"), "w", encoding="utf-8").write(text)
print("done")
