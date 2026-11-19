from pathlib import Path
import subprocess,tempfile,sys
r=Path(sys.argv[1]).resolve();s=(r/'applications/main/bad_usb/helpers/ducky_script.c').read_text();cmd=(r/'applications/main/bad_usb/helpers/ducky_script_commands.c').read_text()
def fn(text,signature):
 a=text.index(signature);i=text.index('{',a)+1;depth=1
 while depth:depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[a:i]
code=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#define UNUSED(v) ((void)v)
#define COUNT_OF(x) (sizeof(x)/sizeof((x)[0]))
#define SCRIPT_STATE_STRING_START (-5)
#define SCRIPT_STATE_CMD_UNKNOWN (-4)
#define HID_KEYBOARD_NONE 0
#define HID_KEYBOARD_RETURN 0x28
#define BADUSB_ASCII_TO_KEY(script,x) (((uint8_t)(x)<128)?((script)->layout[(uint8_t)(x)]):0)
typedef struct{char data[256];}FuriString;
typedef struct{bool(*kb_press)(void*,uint16_t);bool(*kb_release)(void*,uint16_t);}BadUsbHidApi;
typedef struct{uint16_t layout[128];const BadUsbHidApi*hid;void*hid_inst;uint32_t stringdelay,defstringdelay;FuriString*string_print;size_t string_print_pos;char error[128];}BadUsbScript;
static unsigned count;static uint16_t keys[512];static bool pressed;
static bool press(void*p,uint16_t k){(void)p;assert(!pressed);pressed=true;keys[count++]=k;return true;}
static bool release(void*p,uint16_t k){(void)p;assert(pressed&&keys[count-1]==k);pressed=false;return true;}
static size_t furi_string_size(FuriString*s){return strlen(s->data);}
static char furi_string_get_char(FuriString*s,size_t i){return s->data[i];}
static const char* furi_string_get_cstr(FuriString*s){return s->data;}
static void furi_string_set_str(FuriString*s,const char*t){strcpy(s->data,t);}
static void furi_string_cat(FuriString*s,const char*t){strcat(s->data,t);}
static bool ducky_layout_ascii_string(const char*s){for(;*s;s++)if((uint8_t)*s>=128)return false;return true;}
static char last_language[128];
static bool ducky_layout_language(uint16_t*a,const char*t){strcpy(last_language,t);for(unsigned i=0;i<128;i++)a[i]=(uint16_t)(0x4000+i);return true;}
static int32_t ducky_error(BadUsbScript*b,const char*t,...){strcpy(b->error,t);return -1;}
'''
for text,sig in [(s,'uint32_t ducky_get_command_len('),(s,'bool ducky_string('),(s,'static bool ducky_string_next('),(cmd,'static int32_t ducky_fnc_string('),(cmd,'static int32_t ducky_fnc_language(')]:code+=fn(text,sig)+'\n'
code+='typedef int32_t(*DuckyCmdCallback)(BadUsbScript*,const char*,int32_t);\ntypedef struct{const char*name;DuckyCmdCallback callback;int32_t param;}DuckyCmd;\nstatic const DuckyCmd ducky_commands[]={\n'
for line in cmd.splitlines():
 if any('"'+name+'"' in line for name in ['STRING','STRINGLN','DUCKY_LANG']):code+=line+'\n'
code+='};\n'+fn(cmd,'int32_t ducky_execute_cmd(')
code+=r'''
int main(void){BadUsbHidApi hid={press,release};FuriString text={0};BadUsbScript b={.hid=&hid,.string_print=&text};
 assert(ducky_execute_cmd(&b,"DUCKY_LANG de")==0&&!strcmp(last_language,"de")&&count==0);
 assert(ducky_execute_cmd(&b,"DUCKY_LANG")==0&&!last_language[0]);
 assert(ducky_execute_cmd(&b,"DUCKY_LANGX de")==SCRIPT_STATE_CMD_UNKNOWN);
 assert(ducky_execute_cmd(&b,"STRING Az")==0&&count==2&&keys[0]==(0x4000+'A')&&keys[1]==(0x4000+'z'));
 count=0;assert(ducky_execute_cmd(&b,"STRINGLN A")==0&&count==2&&keys[1]==HID_KEYBOARD_RETURN);
 count=0;b.stringdelay=10;assert(ducky_execute_cmd(&b,"STRINGLN Az")==SCRIPT_STATE_STRING_START&&count==0);b.string_print_pos=0;unsigned guard=0;while(!ducky_string_next(&b))assert(++guard<9);assert(count==3&&keys[0]==(0x4000+'A')&&keys[2]==HID_KEYBOARD_RETURN);
 count=0;b.stringdelay=0;b.defstringdelay=5;assert(ducky_execute_cmd(&b,"STRING A")==SCRIPT_STATE_STRING_START);b.string_print_pos=0;while(!ducky_string_next(&b)){}assert(count==1);
 count=0;assert(ducky_execute_cmd(&b,"STRING ascii\xd0\xaf")==-1&&count==0&&strstr(b.error,"not UTF-8"));assert(ducky_execute_cmd(&b,"STRINGLN caf\xc3\xa9")==-1&&count==0);
 assert(!pressed);puts("PASS production command callbacks/parser dispatch for STRING/STRINGLN/DUCKY_LANG, exact keyword, immediate and both delayed-string modes, Return and complete modifier bits, UTF-8 rejected before emitting any HID event. Layout loading separately tested on stock files; HID is a recorder, not USB/BLE hardware.");}
'''
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/'test.c';p.write_text(code);exe=p.with_suffix('');subprocess.run([sys.executable,'-m','ziglang','cc','-std=gnu11','-Wall','-Wextra','-Werror','-UNDEBUG',str(p),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
