# lk_parser
![GitHub](https://img.shields.io/github/license/R0rt1z2/lk_parser)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/R0rt1z2/lk_parser?include_prereleases)

Parse MediaTek LK (_"Little-Kernel"_) Images (lk.bin).

## Requirements
This binary requires Python 3.9 or newer installed on your system. 
It currently supports Windows, Linux and MacOS architectures.

## Usage
```
lk_parser.py <input_file>
```
- `<input_file>` = input, lk.bin

## Example
This is a simple example on a Linux system: 
```
r0rt1z2@r0rt1z2: /lk_parser$ python3 lk_parser.py lk.bin

[?] Image size (from header) = 485476 bytes
[?] Image name (from header) = LK
[?] Command Line: console=tty0 console=ttyS0,921600n1 console=ttyMT3,921600n1 earlycon=uart8250,mmio32,0x11002000 root=/dev/ram vmalloc=496M androidboot.hardware=mt8163
[?] Platform: MT8163
[?] Needs unlock code: True
[?] Available OEM commands: ['fastboot oem idme', 'fastboot oem relock', 'fastboot oem flags', 'fastboot oem p2u', 'fastboot oem off-mode-charge']

r0rt1z2@r0rt1z2: /lk_parser$
```

## License
* This program is licensed under the GNU General Public License (v3). See `LICENSE` for details.