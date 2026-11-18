#!/usr/bin/env python3
"""Compare CPU-model test startup with the unchanged CMS baseline and candidate."""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('qemu',type=Path);p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);p.add_argument('--toolchain',default='nightly');a=p.parse_args();a.output.mkdir(exist_ok=False)
flags='-C target-feature=+sse4.1,-avx,-avx2,-fma';env=dict(os.environ,RUSTFLAGS=flags,CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_RUNNER=str(a.qemu)+' -cpu Nehalem')
records=[]
def run(name,command,environment=None):
 with (a.output/(name+'.log')).open('x') as f:r=subprocess.run(list(map(str,command)),stdout=f,stderr=subprocess.STDOUT,env=environment)
 records.append(dict(case=name,command=list(map(str,command)),exit_code=r.returncode));return r.returncode
binary=a.output/'process-probe';assert run('compile',['rustc','+'+a.toolchain,'--test','tools/cpu_process_probe.rs','-C','target-feature=+sse4.1,-avx,-avx2,-fma','-o',binary])==0
run('minimal',[a.qemu,'-cpu','Nehalem',binary,'test_process_startup','--exact'])
for label,manifest in [('baseline',a.baseline/'Cargo.toml'),('candidate',Path.cwd()/'Cargo.toml')]:
 target=Path(os.environ['TMPDIR']).parent/('mox-cpu-'+label+'-target')
 run(label,['cargo','+'+a.toolchain,'test','--manifest-path',manifest,'-p','moxcms','--lib','cicp::tests::test_to_xyz_using_absolute_coordinates','--','--exact'],dict(env,CARGO_TARGET_DIR=str(target)))
(a.output/'results.json').write_text(json.dumps(dict(rustc=subprocess.check_output(['rustc','+'+a.toolchain,'--version'],text=True).strip(),qemu=subprocess.check_output([a.qemu,'--version'],text=True).strip(),qemu_sha256=hashlib.sha256(a.qemu.read_bytes()).hexdigest(),records=records),indent=2));print(json.dumps(records,indent=2))
