#pragma once

#include <furi.h>
#include <stdint.h>
#include <stdbool.h>

#define DUCKY_LAYOUT_ROOT EXT_PATH("badusb/assets/layouts")
#define DUCKY_LAYOUT_KEYS 128

// Native 095E .kl: 128 little-endian uint16 HID usages/modifiers, no Unicode index.
// These loaders always leave a complete table: requested layout or built-in en-US.
bool ducky_layout_load(uint16_t layout[DUCKY_LAYOUT_KEYS], const char* path);
bool ducky_layout_language(uint16_t layout[DUCKY_LAYOUT_KEYS], const char* argument);
// This .kl format cannot encode non-ASCII Unicode; reject before typing a line.
bool ducky_layout_ascii_string(const char* text);
// New preference is in /int (mapped to SD on 095E), legacy default is preserved
// when no preference file exists. Called at app init / explicit UI selection.
void ducky_layout_default_load(FuriString* path);
bool ducky_layout_default_save(const FuriString* path);
