# Build and test notes

- uFBT SDK selected current Flipper firmware release 1.5.1 (API 88.2).
- `ufbt fap_badusb_ducky_lang`: success; generated `badusb_ducky_lang.fap`; FAP check (`APPCHK`) passed.
- Production-code host tests `test_layouts.py`, `test_parser.py`, and `test_default_ui.py`: passed against the current app copy and SDK keyboard map.
- No physical Flipper device, USB/BLE HID host interaction, or qFlipper screenshot was available for this verification.
- Separately, a distinct pre-existing Hybridus/Unleashed build used API 88.27; that artifact is not built from this external-app package.
