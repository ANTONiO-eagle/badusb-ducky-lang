# Host tests

These tests compile the production layout loader, DuckyScript command callbacks/parser and layout-default scene with small host-side Flipper API doubles. The layout test needs a firmware SDK/source tree path containing `targets/furi_hal_include/furi_hal_usb_hid.h`; its fixtures are the native `.kl` files in that tree. Example invocation used during development:

```sh
python3 tests/test_layouts.py /path/to/test-root
python3 tests/test_parser.py /path/to/test-root
python3 tests/test_default_ui.py /path/to/test-root
```

The test root has `applications/main/bad_usb/` containing this app, `targets/` from the SDK tree and `hid_usage_keyboard.h` at its root. These tests use test doubles for storage, FlipperFormat and HID; they are not device, USB/BLE or host end-to-end tests.
