#!/usr/bin/env python3
"""Selected CMYK repair regions, merging identical generic instantiations."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('coverage',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
data=json.loads(a.coverage.read_text())['data'][0];rows=[]
for label,symbol,limits in [('extended-output','KatanaXyzToRgbExtended',None),('alpha-selection','prepare_alpha_finalizer',None),('tetrahedral-selection','KatanaLut4x3',(196,217)),('extended-selection','katana_prepare_inverse_lut_rgb_xyz',(158,183))]:
 regions={}
 for function in data['functions']:
  if symbol not in function['name']:continue
  for region in function['regions']:
   if region[-1]!=0 or (limits and not(limits[0]<=region[0]<=region[2]<=limits[1])):continue
   key=tuple(region[:4]);regions[key]=max(regions.get(key,0),region[4])
 rows.append(dict(path=label,covered=sum(value>0 for value in regions.values()),required_regions=len(regions),uncovered=[list(key) for key,value in regions.items() if not value]))
 assert regions,label
result=json.dumps(rows,indent=2);a.output.write_text(result);print(result)
