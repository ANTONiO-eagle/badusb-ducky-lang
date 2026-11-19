from pathlib import Path
import subprocess,tempfile,sys
r=Path(sys.argv[1]).resolve();s=(r/'applications/main/bad_usb/scenes/bad_usb_scene_config_layout.c').read_text();a=s.index('void bad_usb_scene_config_layout_on_enter(');i=s.index('{',a)+1;dep=1
while dep:dep+=(s[i]=='{')-(s[i]=='}');i+=1
fn=s[a:i]
code=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
typedef struct{char path[128];}FuriString;
typedef struct{FuriString*keyboard_layout;void*dialogs;void*scene_manager;}BadUsbApp;
static int scenario,allocs,saves,errors,backs;
static FuriString* furi_string_alloc_set(FuriString*p){allocs++;FuriString*q=malloc(sizeof(*q));*q=*p;return q;}
static void furi_string_free(FuriString*p){allocs--;free(p);}
static int furi_string_cmp(FuriString*a,FuriString*b){return strcmp(a->path,b->path);}
static void furi_string_set(FuriString*a,FuriString*b){*a=*b;}
static bool bad_usb_layout_select(BadUsbApp*a){if(scenario==0)return false;if(scenario==1)return true;strcpy(a->keyboard_layout->path,"new.kl");return true;}
static bool ducky_layout_default_save(FuriString*p){assert(!strcmp(p->path,"new.kl"));saves++;return scenario!=3;}
static void dialog_message_show_storage_error(void*d,const char*s){(void)d;assert(strstr(s,"not saved"));errors++;}
static void scene_manager_previous_scene(void*m){(void)m;backs++;}
'''+fn+r'''
int main(void){for(scenario=0;scenario<4;scenario++){FuriString path={"old.kl"};BadUsbApp a={.keyboard_layout=&path};saves=errors=backs=0;bad_usb_scene_config_layout_on_enter(&a);assert(!allocs&&backs==1);if(scenario<2){assert(!saves&&!errors&&!strcmp(path.path,"old.kl"));}else if(scenario==2){assert(saves==1&&!errors&&!strcmp(path.path,"new.kl"));}else{assert(saves==1&&errors==1&&!strcmp(path.path,"old.kl"));}}puts("PASS production layout-default UI on_enter: cancel/unchanged=no write; changed=save; failed save restores previous RAM selection, error shown; temporary string freed, return to config. Browser/storage are test doubles.");}
'''
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/'test.c';p.write_text(code);exe=p.with_suffix('');subprocess.run([sys.executable,'-m','ziglang','cc','-std=gnu11','-Wall','-Wextra','-Werror','-UNDEBUG',str(p),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
