#!/usr/bin/env python3
"""Retain CPU-model startup diagnostics before the unchanged full test loop."""
import argparse,json,os,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('cpu');p.add_argument('features');p.add_argument('output',type=Path);p.add_argument('--toolchain',default='nightly');a=p.parse_args();a.output.mkdir(exist_ok=False)
qemu='qemu-x86_64';flags='-C target-feature='+a.features;env=dict(os.environ,RUSTFLAGS=flags)
rows=[]
(a.output/'versions.json').write_text(json.dumps(dict(rustc=subprocess.check_output(['rustc','+'+a.toolchain,'--version','--verbose'],text=True),qemu=subprocess.check_output([qemu,'--version'],text=True),flags=flags),indent=2))
def run(name,command,environment=None):
 with (a.output/(name+'.log')).open('x')as out:r=subprocess.run(command,stdout=out,stderr=subprocess.STDOUT,env=environment)
 rows.append(dict(case=name,command=command,exit_code=r.returncode));return r.returncode
binary=a.output/'minimal-probe'
assert run('compile',['rustc','+'+a.toolchain,'--test','tools/cpu_process_probe.rs','-C','target-feature='+a.features,'-o',str(binary)])==0
run('minimal',[qemu,'-cpu',a.cpu,str(binary),'test_process_startup','--exact'])
command=['cargo','+'+a.toolchain,'test','--lib','--no-run','--message-format=json']
with (a.output/'build.jsonl').open('x')as out,(a.output/'build.log').open('x')as err:subprocess.run(command,stdout=out,stderr=err,env=env,check=True)
artifacts=[json.loads(line)for line in (a.output/'build.jsonl').read_text().splitlines()]
executable,=[r['executable']for r in artifacts if r.get('reason')=='compiler-artifact'and r.get('target',{}).get('name')=='moxcms'and r.get('executable')]
run('library',[qemu,'-cpu',a.cpu,'-d','in_asm','-D',str(a.output/'instructions.log'),executable,'cicp::tests::test_to_xyz_using_absolute_coordinates','--exact'])
(a.output/'results.json').write_text(json.dumps(rows,indent=2))
for row in rows:print(json.dumps(row))
for name in ['minimal.log','library.log','instructions.log']:
 lines=(a.output/name).read_text().splitlines();print(name+' final lines:\n'+'\n'.join(lines[-60:]))
# Diagnostics do not replace or suppress the following complete test loop.
