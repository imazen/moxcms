#!/usr/bin/env python3
"""Selected CMYK repair regions, merging identical generic instantiations."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('coverage',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
data=json.loads(a.coverage.read_text())['data'][0];rows=[]
root=Path(__file__).resolve().parents[1]
def bounds(name,start,end):
 text=(root/name).read_text();left=text.index(start);right=text.index(end,left)
 return text[:left].count('\n')+1,text[:right].count('\n')
tetra=bounds('src/conversions/lut4.rs','if !T::FINITE && self.interpolation_method','// Preserve the default PCS')
extended=bounds('src/conversions/katana/xyz_rgb.rs','if !T::FINITE','let gamma_map_r')
for label,symbol,limits in [('extended-output','KatanaXyzToRgbExtended',None),('alpha-selection','prepare_alpha_finalizer',None),('tetrahedral-selection','KatanaLut4x3',tetra),('extended-selection','katana_prepare_inverse_lut_rgb_xyz',extended)]:
 regions={}
 for function in data['functions']:
  if symbol not in function['name']:continue
  for region in function['regions']:
   if region[-1]!=0 or (limits and not(limits[0]<=region[0]<=region[2]<=limits[1])):continue
   key=tuple(region[:4]);regions[key]=max(regions.get(key,0),region[4])
 rows.append(dict(path=label,covered=sum(value>0 for value in regions.values()),required_regions=len(regions),uncovered=[list(key) for key,value in regions.items() if not value]))
 assert regions,label
result=json.dumps(rows,indent=2);a.output.write_text(result);print(result)
