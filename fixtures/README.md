# Host-test keyboard-layout fixtures

These are unmodified 256-byte native `.kl` keyboard-map files used only by the host-side layout-loader tests. They are not BadUSB scripts and are not installed as app assets.

The three maps are copied byte-for-byte from the Flipper Zero firmware 1.5.1 release source (`applications/main/bad_usb/resources/badusb/assets/layouts/`):

- https://github.com/flipperdevices/flipperzero-firmware/blob/1.5.1/applications/main/bad_usb/resources/badusb/assets/layouts/en-US.kl
- https://github.com/flipperdevices/flipperzero-firmware/blob/1.5.1/applications/main/bad_usb/resources/badusb/assets/layouts/de-DE.kl
- https://github.com/flipperdevices/flipperzero-firmware/blob/1.5.1/applications/main/bad_usb/resources/badusb/assets/layouts/fr-FR.kl

Each file was checked against the corresponding upstream URL by SHA-256. They are test fixtures and are distributed under the upstream firmware's GPL-3.0 license; see the repository `LICENSE` and `NOTICE`.
