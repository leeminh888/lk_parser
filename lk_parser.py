#!/usr/bin/env python3

         #====================================================#
         #              FILE: lk_parser.py                    #
         #              AUTHOR: R0rt1z2                       #
         #              DATE: 2021                            #
         #====================================================#

#   MediaTek Little-Kernel ("LK") parser.
#   "python3 lk-parser.py input_lk.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import io
import os
import re
import subprocess
import struct

HEADER_SEQ = b'\x88\x16\x88X'

if sys.version_info[1] < 9:
    raise RuntimeError("[!] Python 3.9+ is required.")

def parse_lk_product(lk : io.BufferedReader) -> str:
    """
    Reads and parses the product name from the provided LK image.
    :param lk: The image to be parsed.
    :return: The product name.
    """
    I = 0
    lk.seek(0)
    OFFSET = lk.read().find(b'product')

    if OFFSET == -1:
        return "N/A"

    lk.seek(OFFSET + len(b'product') + 1)

    while lk.read(1) != b'\x00':
        I += 1

    lk.seek(OFFSET + len(b'product') + 1)
    PRODUCT = lk.read(I).decode("utf-8")

    lk.seek(0)
    return PRODUCT

def parse_lk_platform(lk : io.BufferedReader) -> str:
    """
    Reads and parses the platform from the provided LK image.
    :param lk: The image to be parsed.
    :return: The platform.
    """
    CMDLINE = parse_lk_cmdline(lk)
    OFFSET = lk.read().find(b'platform/')
    lk.seek(OFFSET + len(b'platform/'))
   
    if CMDLINE.find("androidboot.hardware") != -1:
        PLATFORM = CMDLINE[CMDLINE.find('androidboot.hardware') + len('androidboot.hardware=') :len(CMDLINE)].upper()
    else:
        PLATFORM = lk.read(6).decode("utf-8").upper()
    
    lk.seek(0)
    return PLATFORM

def parse_lk_cmdline(lk : io.BufferedReader) -> str:
    """
    Reads and parses the boot command line ("cmdline") from the provided LK image.
    :param lk: The image to be parsed.
    :return: The command line.
    """
    I = 0
    lk.seek(0)
    OFFSET = lk.read().find(b'console=')
    
    if OFFSET == -1:
        return "N/A"
    
    lk.seek(OFFSET)
    
    while lk.read(1) != b'\x00':
        I += 1
    
    lk.seek(OFFSET)
    CMDLINE = lk.read(I).decode("utf-8")
    
    lk.seek(0)
    return CMDLINE
    
def parse_lk_oem_commands(lk : io.BufferedReader) -> list[str]:
    """
    Reads and parses all the "oem command" commands from the provided LK image.
    :param lk: The image to be parsed.
    :return: List with all oem commands.
    """
    OEM_OFFSETS = []
    TMP_COMMANDS = []
    FINAL_COMMANDS = []
    
    lk.seek(0)
    data = lk.read()

    for m in re.finditer(b'oem ', data):
        OEM_OFFSETS.append(m.start())

    for offset in OEM_OFFSETS:
        TMP_COMMANDS.append(data[offset:offset+3+100]) # offset, b'oem' length, inaccurate string length (fixme)

    for word in str(TMP_COMMANDS).split("oem "):
        param = ''
        for char in word:
            if char in ("\\", "[", "'", "\n", " ", ")", "("):
                break
            param += char

        if param:
            FINAL_COMMANDS.append(f"fastboot oem {param}")
    
    seen = set()
    UNIQ = []
    for x in FINAL_COMMANDS:
        if x not in seen:
            UNIQ.append(x)
            seen.add(x)

    lk.seek(0)
    return UNIQ

def main():
    if len(sys.argv) < 2:
        print(f"[?] Usage: {sys.argv[0]} <lk.bin>.")
        sys.exit(0)

    lk_bin_file = sys.argv[1]
    if not os.path.exists(lk_bin_file):
        print(f"[-] Couldn't open '{lk_bin_file}'.")
        sys.exit(1)

    with open(lk_bin_file, "rb") as fp:
        if fp.read(4) != HEADER_SEQ:
            print(f"[-] Invalid LK image.")
            sys.exit(1)

        HEADER_FILE_SIZE = struct.unpack("<I", fp.read(4))[0]
        print(f"[?] Image size (from header) = {HEADER_FILE_SIZE} bytes")

        IMAGE_NAME = fp.read(8).decode("utf-8")
        print(f"[?] Image name (from header) = {IMAGE_NAME}")

        CMDLINE = parse_lk_cmdline(fp)
        print(f"[?] Command Line: {CMDLINE}")

        print(f"[?] Platform: {parse_lk_platform(fp)}")
        print(f"[?] Product: {parse_lk_product(fp)}")
        
        NEEDS_UNLOCK_CODE = (fp.read().find(b'unlock code') != -1)
        print(f"[?] Needs unlock code: {NEEDS_UNLOCK_CODE}")
        fp.seek(0)

        USES_VERIFIED_BOOT = (fp.read().find(b'verified boot') != 1)
        print(f"[?] Uses verified boot: {USES_VERIFIED_BOOT}")
        fp.seek(0)
        
        print(f"[?] Available OEM commands: {parse_lk_oem_commands(fp)}")

if __name__ == "__main__":
    main()
