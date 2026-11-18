#!/usr/bin/env python3
"""Verify that CMS lint maintenance changes only fixed-array iteration syntax."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('base');p.add_argument('output',type=Path);a=p.parse_args()
names=subprocess.check_output(['git','diff','--name-only',a.base,'--','src'],text=True).splitlines()
def normalize(text):
 text=re.sub(r'\s+','',text)
 text=re.sub(r'\.as_chunks_mut::<\{?(\w+)\}?>\(\)\.0(?:\.iter_mut\(\))?',r'.chunks_exact_mut(\1)',text)
 return re.sub(r'\.as_chunks::<\{?(\w+)\}?>\(\)\.0(?:\.iter\(\))?',r'.chunks_exact(\1)',text)
rows=[]
for name in names:
 old=subprocess.check_output(['git','show',a.base+':'+name],text=True);new=Path(name).read_text()
 assert normalize(old)==normalize(new),name
 rows.append(dict(path=name,old_sha256=hashlib.sha256(old.encode()).hexdigest(),new_sha256=hashlib.sha256(new.encode()).hexdigest()))
assert rows,'no changed sources'
a.output.write_text(json.dumps(dict(base=a.base,files=rows),indent=2));print('array iteration normalization matches every changed source')
