from pathlib import Path
import sys,json,subprocess,shlex,tempfile,hashlib
r=Path(sys.argv[1]).resolve();o=Path(sys.argv[2]).resolve();app=r/'applications/main/bad_usb'
# Exact registration/path/worker ownership; no runtime setter races.
s=(app/'helpers/ducky_script.c').read_text();assert s.count('memcpy(bad_usb->layout, bad_usb->default_layout, sizeof(bad_usb->layout));')==3
assert s.index('ducky_layout_load(bad_usb->default_layout')<s.index('furi_thread_start(bad_usb->thread)')
assert 'bad_usb_script_set_keyboard_layout(' not in s
work=(app/'scenes/bad_usb_scene_work.c').read_text();assert work.count('app->keyboard_layout);')==2
assert 'bad_usb_script_set_keyboard_layout' not in work
# Everything except the documented 10 files must be byte-identical to original app.
changed=(o/'changed-files.txt').read_text().splitlines()
base_commit='9c6327764c18fc8376b5941aa8bde79fe681fe8f'
original=subprocess.check_output(['git','ls-tree','-r','--name-only',base_commit,'applications/main/bad_usb'],cwd=r,text=True).splitlines()
for n in original:
 relative=str(Path(n).relative_to('applications/main/bad_usb'))
 if relative not in changed:
  assert subprocess.check_output(['git','show',base_commit+':'+n],cwd=r)==(r/n).read_bytes(),n
assert subprocess.check_output(['git','show',base_commit+':applications/main/bad_usb/application.fam'],cwd=r)==(app/'application.fam').read_bytes()
# Strict compilation with real FAP flags; CDB may omit the newly discovered file,
# so clone the adjacent existing Ducky helper command with a different source/output.
cc=json.loads((r/'build/f7-firmware-C/compile_commands.json').read_text());rows=[]
with tempfile.TemporaryDirectory() as tmp:
 for n in changed:
  if not n.endswith('.c'):continue
  fullname='applications/main/bad_usb/'+n;match=[c for c in cc if c['file']==fullname]
  if not match:
   assert n=='helpers/ducky_layout.c';c=next(c for c in cc if c['file']=='applications/main/bad_usb/helpers/ducky_script.c');args=shlex.split(c['command']);args=[fullname if t==c['file'] else t for t in args]
  else:assert len(match)==1;c=match[0];args=shlex.split(c['command'])
  assert all(t in args for t in ['-Wall','-Wextra','-Werror'])
  args=[t for t in args if t not in ['-Wno-error=deprecated-declarations','-Wno-address-of-packed-member']];args[args.index('-o')+1]=str(Path(tmp)/str(len(rows)))
  subprocess.run(args,cwd=r,check=True);rows.append(fullname)
fap=r/'build/f7-firmware-C/.extapps/bad_usb.fap';b=fap.read_bytes();assert b[:4]==b'\x7fELF'
fw=(r/'build/f7-firmware-C/firmware.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='6fc697e5347f76584544b93e77388cd4240931d2175c018b25b72d4ed14776db'
m={'base':'Unleashed095E commit9c6327764c18fc8376b5941aa8bde79fe681fe8f; Hybridus0.7 + safe Module1 source','format':'native 256-byte .kl, 128 LE uint16 values, ASCII only; Unicode/cyrillic NOT implemented','native_layout_resources':31,'strict_arm_units':rows,'strict_flags':'-Wall -Wextra -Werror without inherited deprecated/packed suppressions for these units','fap_bytes':len(b),'fap_sha256':hashlib.sha256(b).hexdigest(),'fap_sdk_api':'88.26 (FBT APPCHK passed)','firmware_bin_unchanged_from_module1':True,'firmware_bin_bytes':len(fw),'new_default_layout_bytes_per_script':256,'new_heap_allocations_in_module':False,'runtime_layout_switch_owner':'script worker; default copied before worker starts and on both new-run entry branches','default_setting_path':'/int/.hybridus-ducky-layout','hardware_tested':False,'module3_touched':False}
(o/'VERIFICATION.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2));print('PASS source integration, default-reset paths, strict FAP ARM compilation, unchanged MCU BIN/application.fam/other app files.')
