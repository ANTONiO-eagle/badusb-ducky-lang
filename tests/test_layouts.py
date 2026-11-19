from pathlib import Path
import subprocess,tempfile,sys
r=Path(sys.argv[1]).resolve();o=Path(__file__).resolve().parents[1]
def strip(s):return '\n'.join(l for l in s.splitlines() if not l.startswith('#include') and l!='#pragma once')
header=(r/'targets/furi_hal_include/furi_hal_usb_hid.h').read_text();start=header.index('static const uint16_t hid_asciimap[]');end=header.index('\n};',start)+3
# Native hid map uses only literals and KEY_MOD constants, preserve real table.
code=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include "hid_usage_keyboard.h"
#define EXT_PATH(p) "/ext/" p
#define INT_PATH(p) "/int/" p
#define RECORD_STORAGE "storage"
#define furi_check assert
#define MIN(a,b) ((a)<(b)?(a):(b))
#define KEY_MOD_LEFT_SHIFT (1<<9)
#define KEY_MOD_RIGHT_ALT (1<<14)
#define HID_KEYBOARD_NONE 0
#define FURI_LOG_W(...) warning(__VA_ARGS__)
static unsigned warnings,records,allocs;
static void warning(const char*tag,const char*fmt,...){(void)tag;(void)fmt;warnings++;}
static void* furi_record_open(const char*s){assert(!strcmp(s,"storage"));records++;return (void*)1;}
static void furi_record_close(const char*s){(void)s;assert(records);records--;}
typedef struct{}Storage;
typedef struct{FILE*fp;}File;
enum{FSAM_READ,FSOM_OPEN_EXISTING};
static char root[1024];static bool fail_read;
static File* storage_file_alloc(Storage*s){(void)s;allocs++;return calloc(1,sizeof(File));}
static bool storage_file_open(File*f,const char*p,int a,int m){assert(a==FSAM_READ&&m==FSOM_OPEN_EXISTING);assert(strncmp(p,"/ext/badusb/assets/layouts/",26)==0);char q[2048];snprintf(q,sizeof(q),"%s/%s",root,strrchr(p,'/')+1);f->fp=fopen(q,"rb");return f->fp!=NULL;}
static size_t storage_file_size(File*f){long pos=ftell(f->fp);fseek(f->fp,0,SEEK_END);long n=ftell(f->fp);fseek(f->fp,pos,SEEK_SET);return n;}
static size_t storage_file_read(File*f,void*p,size_t n){return fail_read?0:fread(p,1,n,f->fp);}
static void storage_file_close(File*f){if(f->fp){fclose(f->fp);f->fp=NULL;}}
static void storage_file_free(File*f){free(f);allocs--;}
typedef struct{char data[256];}FuriString;
typedef struct{bool writing;int field;}FlipperFormat;
static bool pref_exists,pref_open=true,pref_header=true,pref_read=true,pref_write=true;
static uint32_t pref_version=1;static char pref_type[128]="Hybridus Ducky Layout",pref_path[256];
static FlipperFormat* flipper_format_file_alloc(Storage*s){(void)s;allocs++;return calloc(1,sizeof(FlipperFormat));}
static bool flipper_format_file_open_existing(FlipperFormat*f,const char*p){(void)f;assert(!strcmp(p,"/int/.hybridus-ducky-layout"));return pref_exists&&pref_open;}
static bool flipper_format_file_open_always(FlipperFormat*f,const char*p){(void)p;f->writing=true;return pref_open;}
static bool flipper_format_read_header(FlipperFormat*f,FuriString*s,uint32_t*v){(void)f;strcpy(s->data,pref_type);*v=pref_version;return pref_header;}
static bool flipper_format_read_string(FlipperFormat*f,const char*k,FuriString*s){(void)f;assert(!strcmp(k,"path"));strcpy(s->data,pref_path);return pref_read;}
static bool flipper_format_write_header_cstr(FlipperFormat*f,const char*s,uint32_t v){assert(f->writing);if(pref_write){strcpy(pref_type,s);pref_version=v;}return pref_write;}
static bool flipper_format_write_string_cstr(FlipperFormat*f,const char*k,const char*s){assert(f->writing&&!strcmp(k,"path"));if(pref_write){strcpy(pref_path,s);pref_exists=true;}return pref_write;}
static void flipper_format_free(FlipperFormat*f){free(f);allocs--;}
static FuriString* furi_string_alloc(void){allocs++;return calloc(1,sizeof(FuriString));}
static void furi_string_free(FuriString*s){free(s);allocs--;}
static const char* furi_string_get_cstr(const FuriString*s){return s->data;}
static int furi_string_cmp_str(const FuriString*s,const char*t){return strcmp(s->data,t);}
static void furi_string_set(FuriString*s,const FuriString*t){*s=*t;}
static void furi_string_set_str(FuriString*s,const char*t){strcpy(s->data,t);}
#define furi_string_set(s,t) _Generic((t),FuriString*: furi_string_set,const FuriString*: furi_string_set,default:furi_string_set_str)((s),(t))
'''
code+=header[start:end]+'\n'+strip((r/'applications/main/bad_usb/helpers/ducky_layout.h').read_text())+'\n'+strip((r/'applications/main/bad_usb/helpers/ducky_layout.c').read_text())
code+=r'''
static void baseline(uint16_t*a){memcpy(a,hid_asciimap,256);}
static void assert_us(uint16_t*a){assert(!memcmp(a,hid_asciimap,256));}
static void expected(uint16_t*a,const char*file){char q[2048];snprintf(q,sizeof(q),"%s/%s",root,file);FILE*f=fopen(q,"rb");assert(f);uint8_t b[256];assert(fread(b,1,256,f)==256);fclose(f);for(unsigned i=0;i<128;i++)assert(a[i]==(uint16_t)(b[2*i]|b[2*i+1]<<8));}
int main(int argc,char**argv){assert(argc==2);strcpy(root,argv[1]);uint16_t a[128];
 assert(ducky_layout_language(a,"de"));expected(a,"de-DE.kl");assert(ducky_layout_language(a,"fr-FR \r\n"));expected(a,"fr-FR.kl");assert(ducky_layout_language(a,"en"));expected(a,"en-US.kl");
 const char*bad[]={"ru","../de-DE","","de extra","de/DE","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","de-DE.kl"};for(size_t i=0;i<sizeof(bad)/sizeof(bad[0]);i++){assert(ducky_layout_language(a,"de"));unsigned w=warnings;assert(!ducky_layout_language(a,bad[i]));assert_us(a);assert(warnings>w);}
 assert(!ducky_layout_load(a,"/ext/elsewhere/de-DE.kl"));assert_us(a);
 assert(!ducky_layout_load(a,"/ext/badusb/assets/layouts/../de-DE.kl"));assert_us(a);
 assert(!ducky_layout_language(a,"short"));assert_us(a);assert(!ducky_layout_language(a,"long"));assert_us(a);
 fail_read=true;assert(!ducky_layout_language(a,"de"));assert_us(a);fail_read=false;
 assert(ducky_layout_load(a,NULL));assert_us(a);
 assert(ducky_layout_ascii_string("Hello Az09!\n"));assert(!ducky_layout_ascii_string("\xd0\xaf"));assert(!ducky_layout_ascii_string("\xc3\xa9"));assert(!ducky_layout_ascii_string("\xff"));
 // Physical modifier bits survive decoding, including Right Alt.
 assert(ducky_layout_language(a,"de"));bool alt=false,shift=false;for(unsigned i=0;i<128;i++){alt|=(a[i]&0x4000)!=0;shift|=(a[i]&0x0200)!=0;}assert(alt&&shift);
 FuriString path={"/ext/badusb/assets/layouts/fr-FR.kl"};ducky_layout_default_load(&path);assert(strstr(path.data,"fr-FR")); // missing preference retains legacy selection
 assert(ducky_layout_default_save(&path));strcpy(path.data,"legacy");ducky_layout_default_load(&path);assert(strstr(path.data,"fr-FR"));
 pref_version=99;ducky_layout_default_load(&path);assert(strstr(path.data,"en-US"));pref_version=1;strcpy(pref_path,"../../escape.kl");ducky_layout_default_load(&path);assert(strstr(path.data,"en-US"));
 strcpy(path.data,"/ext/badusb/assets/layouts/de-DE.kl");pref_write=false;assert(!ducky_layout_default_save(&path));pref_write=true;
 strcpy(path.data,"/ext/elsewhere/a.kl");assert(!ducky_layout_default_save(&path));
 baseline(a);assert_us(a);assert(!records&&!allocs);puts("PASS real layout loader/language/default-pref helpers: stock en/de/fr fixtures, LE decoding/modifiers, malformed/short/oversize/missing/read-failure/path traversal fall back to built-in US with warning, strict ASCII guard, preference load/save/version/path/failure, all resource pairs balanced. File read real host files; storage/FlipperFormat are test doubles, no USB/BLE hardware.");
}
'''
with tempfile.TemporaryDirectory() as tmp:
 import shutil
 d=Path(tmp)
 for p in (o/'fixtures').glob('*.kl'):shutil.copyfile(p,d/p.name)
 (d/'short.kl').write_bytes(b'X'*255);(d/'long.kl').write_bytes(b'X'*257)
 p=d/'test.c';p.write_text(code);exe=d/'test'
 subprocess.run([sys.executable,'-m','ziglang','cc','-std=gnu11','-Wall','-Wextra','-Werror','-UNDEBUG','-I'+str(next(r.rglob('hid_usage_keyboard.h')).parent),str(p),'-o',str(exe)],check=True);subprocess.run([str(exe),str(d)],check=True)
