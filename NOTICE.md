# Third-party code

## epomaker-driver-linux

`vendor/epomaker_driver/` is a copy of the `src/epomaker_driver` package from
[ramarivera/epomaker-driver-linux](https://github.com/ramarivera/epomaker-driver-linux),
commit `70ef1b23b51c3adaaa09d96996621bac080f203e` (2026-09-09).

- License: MIT, Copyright (c) 2026 Ramiro Rivera. The full text is in `vendor/LICENSE-epomaker-driver-linux`.
- It provides the packet codec and the magnetic-key / lighting logic this toolkit relies on.

### Changes made to the vendored copy

1. Every `Path.read_text()` call now passes `encoding="utf-8"`. On Windows the default codec (cp1252) cannot decode the package's JSON data files.

Nothing else in `vendor/` is modified. The Linux-only `fcntl` import in `transport.py` is satisfied at runtime by a stub in `winhid.py`, and the hidraw I/O class is replaced by a `hid.dll` one; neither change touches the vendored files.

This toolkit's own code (everything outside `vendor/`) is licensed under the root [LICENSE](LICENSE).
