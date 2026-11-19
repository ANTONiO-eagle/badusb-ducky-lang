# BadUSB DUCKY_LANG for Flipper Zero

A Flipper Zero external app based on the BadUSB app in the official Flipper Zero firmware. It adds a persistent default keyboard-layout setting and a DuckyScript `DUCKY_LANG` directive for switching the active layout while a script runs.

## What the UI labels mean

- **Default layout (USB/BLE)** is a settings row. Choosing it opens the ordinary `.kl` layout-file picker; that picker lists the available language/layout files. `Default layout` is not a separate keyboard-layout file.
- **`DUCKY_LANG`** is a line in a DuckyScript text file, not an app menu item or a layout-file name. For example, a script may contain `DUCKY_LANG de` to select the German layout for subsequent text in that run. Supported short aliases are `en`, `de`, and `fr`; other valid names map to existing `.kl` files.
- A script's `DUCKY_LANG` selection is temporary. The saved default is restored at the next script start.

The implementation consumes the native 256-byte `.kl` format (128 little-endian 16-bit HID entries). This is not Unicode keyboard support: non-ASCII UTF-8 text is rejected before that `STRING` line emits keys. The operating system's active keyboard layout must match the selected Flipper layout. The app expects the standard layout assets at `/ext/badusb/assets/layouts`, as provided by compatible firmware installations.

## Build

Install uFBT, then run from this directory:

```sh
ufbt fap_badusb_ducky_lang
```

The source was built with uFBT against Flipper firmware release 1.5.1 / API 88.2 and passed `APPCHK`. Host tests exercise the production layout loader/parser/UI code with test doubles; they do not prove USB/BLE behavior on hardware. Hardware installation and end-to-end host testing have not been confirmed.

## Safety and scope

This repository contains the app source, not example keystroke payloads. BadUSB scripts send keyboard/mouse input to the connected host. Only use scripts on computers and accounts you own or are expressly authorized to test; inspect a script before running it and use a harmless test target.

## License and origin

GPL-3.0-or-later; see `LICENSE` and `NOTICE`. The app derives from Flipper Zero firmware BadUSB sources and includes changes for standalone uFBT builds. It is an independent community app and is not an official Flipper Devices release.
