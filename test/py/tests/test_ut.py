# SPDX-License-Identifier: GPL-2.0
"""
Unit-test runner

Provides a test_ut() function which is used by conftest.py to run each unit
test one at a time, as well setting up some files needed by the tests.

# Copyright (c) 2016, NVIDIA CORPORATION. All rights reserved.
"""
import collections
import getpass
import gzip
import os
import os.path
import pytest

import u_boot_utils
# pylint: disable=E0611
from tests import fs_helper
from test_android import test_abootimg

def mkdir_cond(dirname):
    """Create a directory if it doesn't already exist

    Args:
        dirname (str): Name of directory to create
    """
    if not os.path.exists(dirname):
        os.mkdir(dirname)

def setup_image(cons, devnum, part_type, second_part=False, basename='mmc'):
    """Create a 20MB disk image with a single partition

    Args:
        cons (ConsoleBase): Console to use
        devnum (int): Device number to use, e.g. 1
        part_type (int): Partition type, e.g. 0xc for FAT32
        second_part (bool): True to contain a small second partition
        basename (str): Base name to use in the filename, e.g. 'mmc'

    Returns:
        tuple:
            str: Filename of MMC image
            str: Directory name of 'mnt' directory
    """
    fname = os.path.join(cons.config.source_dir, f'{basename}{devnum}.img')
    mnt = os.path.join(cons.config.persistent_data_dir, 'mnt')
    mkdir_cond(mnt)

    spec = f'type={part_type:x}, size=18M, bootable'
    if second_part:
        spec += '\ntype=c'

    u_boot_utils.run_and_log(cons, f'qemu-img create {fname} 20M')
    u_boot_utils.run_and_log(cons, f'sudo sfdisk {fname}',
                             stdin=spec.encode('utf-8'))
    return fname, mnt

def mount_image(cons, fname, mnt, fstype):
    """Create a filesystem and mount it on partition 1

    Args:
        cons (ConsoleBase): Console to use
        fname (str): Filename of MMC image
        mnt (str): Directory name of 'mnt' directory
        fstype (str): Filesystem type ('vfat' or 'ext4')

    Returns:
        str: Name of loop device used
    """
    out = u_boot_utils.run_and_log(cons, f'sudo losetup --show -f -P {fname}')
    loop = out.strip()
    part = f'{loop}p1'
    u_boot_utils.run_and_log(cons, f'sudo mkfs.{fstype} {part}')
    opts = ''
    if fstype == 'vfat':
        opts += f' -o uid={os.getuid()},gid={os.getgid()}'
    u_boot_utils.run_and_log(cons, f'sudo mount -o loop {part} {mnt}{opts}')
    u_boot_utils.run_and_log(cons, f'sudo chown {getpass.getuser()} {mnt}')
    return loop

def copy_prepared_image(cons, devnum, fname, basename='mmc'):
    """Use a prepared image since we cannot create one

    Args:
        cons (ConsoleBase): Console touse
        devnum (int): device number
        fname (str): Filename of MMC image
        basename (str): Base name to use in the filename, e.g. 'mmc'
    """
    infname = os.path.join(cons.config.source_dir,
                           f'test/py/tests/bootstd/{basename}{devnum}.img.xz')
    u_boot_utils.run_and_log(cons, ['sh', '-c', f'xz -dc {infname} >{fname}'])

def setup_bootmenu_image(cons):
    """Create a 20MB disk image with a single ext4 partition

    This is modelled on Armbian 22.08 Jammy
    """
    mmc_dev = 4
    fname, mnt = setup_image(cons, mmc_dev, 0x83)

    loop = None
    mounted = False
    complete = False
    try:
        loop = mount_image(cons, fname, mnt, 'ext4')
        mounted = True

        script = '''# DO NOT EDIT THIS FILE
#
# Please edit /boot/armbianEnv.txt to set supported parameters
#

setenv load_addr "0x9000000"
setenv overlay_error "false"
# default values
setenv rootdev "/dev/mmcblk%dp1"
setenv verbosity "1"
setenv console "both"
setenv bootlogo "false"
setenv rootfstype "ext4"
setenv docker_optimizations "on"
setenv earlycon "off"

echo "Boot script loaded from ${devtype} ${devnum}"

if test -e ${devtype} ${devnum} ${prefix}armbianEnv.txt; then
	load ${devtype} ${devnum} ${load_addr} ${prefix}armbianEnv.txt
	env import -t ${load_addr} ${filesize}
fi

if test "${logo}" = "disabled"; then setenv logo "logo.nologo"; fi

if test "${console}" = "display" || test "${console}" = "both"; then setenv consoleargs "console=tty1"; fi
if test "${console}" = "serial" || test "${console}" = "both"; then setenv consoleargs "console=ttyS2,1500000 ${consoleargs}"; fi
if test "${earlycon}" = "on"; then setenv consoleargs "earlycon ${consoleargs}"; fi
if test "${bootlogo}" = "true"; then setenv consoleargs "bootsplash.bootfile=bootsplash.armbian ${consoleargs}"; fi

# get PARTUUID of first partition on SD/eMMC the boot script was loaded from
if test "${devtype}" = "mmc"; then part uuid mmc ${devnum}:1 partuuid; fi

setenv bootargs "root=${rootdev} rootwait rootfstype=${rootfstype} ${consoleargs} consoleblank=0 loglevel=${verbosity} ubootpart=${partuuid} usb-storage.quirks=${usbstoragequirks} ${extraargs} ${extraboardargs}"

if test "${docker_optimizations}" = "on"; then setenv bootargs "${bootargs} cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory swapaccount=1"; fi

load ${devtype} ${devnum} ${ramdisk_addr_r} ${prefix}uInitrd
load ${devtype} ${devnum} ${kernel_addr_r} ${prefix}Image

load ${devtype} ${devnum} ${fdt_addr_r} ${prefix}dtb/${fdtfile}
fdt addr ${fdt_addr_r}
fdt resize 65536
for overlay_file in ${overlays}; do
	if load ${devtype} ${devnum} ${load_addr} ${prefix}dtb/rockchip/overlay/${overlay_prefix}-${overlay_file}.dtbo; then
		echo "Applying kernel provided DT overlay ${overlay_prefix}-${overlay_file}.dtbo"
		fdt apply ${load_addr} || setenv overlay_error "true"
	fi
done
for overlay_file in ${user_overlays}; do
	if load ${devtype} ${devnum} ${load_addr} ${prefix}overlay-user/${overlay_file}.dtbo; then
		echo "Applying user provided DT overlay ${overlay_file}.dtbo"
		fdt apply ${load_addr} || setenv overlay_error "true"
	fi
done
if test "${overlay_error}" = "true"; then
	echo "Error applying DT overlays, restoring original DT"
	load ${devtype} ${devnum} ${fdt_addr_r} ${prefix}dtb/${fdtfile}
else
	if load ${devtype} ${devnum} ${load_addr} ${prefix}dtb/rockchip/overlay/${overlay_prefix}-fixup.scr; then
		echo "Applying kernel provided DT fixup script (${overlay_prefix}-fixup.scr)"
		source ${load_addr}
	fi
	if test -e ${devtype} ${devnum} ${prefix}fixup.scr; then
		load ${devtype} ${devnum} ${load_addr} ${prefix}fixup.scr
		echo "Applying user provided fixup script (fixup.scr)"
		source ${load_addr}
	fi
fi
booti ${kernel_addr_r} ${ramdisk_addr_r} ${fdt_addr_r}

# Recompile with:
# mkimage -C none -A arm -T script -d /boot/boot.cmd /boot/boot.scr
'''
        bootdir = os.path.join(mnt, 'boot')
        mkdir_cond(bootdir)
        cmd_fname = os.path.join(bootdir, 'boot.cmd')
        scr_fname = os.path.join(bootdir, 'boot.scr')
        with open(cmd_fname, 'w', encoding='ascii') as outf:
            print(script, file=outf)

        infname = os.path.join(cons.config.source_dir,
                               'test/py/tests/bootstd/armbian.bmp.xz')
        bmp_file = os.path.join(bootdir, 'boot.bmp')
        u_boot_utils.run_and_log(
            cons,
            ['sh', '-c', f'xz -dc {infname} >{bmp_file}'])

        u_boot_utils.run_and_log(
            cons, f'mkimage -C none -A arm -T script -d {cmd_fname} {scr_fname}')

        kernel = 'vmlinuz-5.15.63-rockchip64'
        target = os.path.join(bootdir, kernel)
        with open(target, 'wb') as outf:
            print('kernel', outf)

        symlink = os.path.join(bootdir, 'Image')
        if os.path.exists(symlink):
            os.remove(symlink)
        u_boot_utils.run_and_log(
            cons, f'echo here {kernel} {symlink}')
        os.symlink(kernel, symlink)

        complete = True

    except ValueError as exc:
        print(f'Falled to create image, failing back to prepared copy: {exc}')
    finally:
        if mounted:
            u_boot_utils.run_and_log(cons, f'sudo umount --lazy {mnt}')
        if loop:
            u_boot_utils.run_and_log(cons, f'sudo losetup -d {loop}')

    if not complete:
        copy_prepared_image(cons, mmc_dev, fname)

def setup_bootflow_image(cons):
    """Create a 20MB disk image with a single FAT partition"""
    mmc_dev = 1
    fname, mnt = setup_image(cons, mmc_dev, 0xc, second_part=True)

    loop = None
    mounted = False
    complete = False
    try:
        loop = mount_image(cons, fname, mnt, 'vfat')
        mounted = True

        vmlinux = 'vmlinuz-5.3.7-301.fc31.armv7hl'
        initrd = 'initramfs-5.3.7-301.fc31.armv7hl.img'
        dtbdir = 'dtb-5.3.7-301.fc31.armv7hl'
        script = '''# extlinux.conf generated by appliance-creator
ui menu.c32
menu autoboot Welcome to Fedora-Workstation-armhfp-31-1.9. Automatic boot in # second{,s}. Press a key for options.
menu title Fedora-Workstation-armhfp-31-1.9 Boot Options.
menu hidden
timeout 20
totaltimeout 600

label Fedora-Workstation-armhfp-31-1.9 (5.3.7-301.fc31.armv7hl)
        kernel /%s
        append ro root=UUID=9732b35b-4cd5-458b-9b91-80f7047e0b8a rhgb quiet LANG=en_US.UTF-8 cma=192MB cma=256MB
        fdtdir /%s/
        initrd /%s''' % (vmlinux, dtbdir, initrd)
        ext = os.path.join(mnt, 'extlinux')
        mkdir_cond(ext)

        conf = os.path.join(ext, 'extlinux.conf')
        with open(conf, 'w', encoding='ascii') as fd:
            print(script, file=fd)

        inf = os.path.join(cons.config.persistent_data_dir, 'inf')
        with open(inf, 'wb') as fd:
            fd.write(gzip.compress(b'vmlinux'))
        u_boot_utils.run_and_log(
            cons, f'mkimage -f auto -d {inf} {os.path.join(mnt, vmlinux)}')

        with open(os.path.join(mnt, initrd), 'w', encoding='ascii') as fd:
            print('initrd', file=fd)

        mkdir_cond(os.path.join(mnt, dtbdir))

        dtb_file = os.path.join(mnt, f'{dtbdir}/sandbox.dtb')
        u_boot_utils.run_and_log(
            cons, f'dtc -o {dtb_file}', stdin=b'/dts-v1/; / {};')
        complete = True
    except ValueError as exc:
        print(f'Falled to create image, failing back to prepared copy: {exc}')
    finally:
        if mounted:
            u_boot_utils.run_and_log(cons, f'sudo umount --lazy {mnt}')
        if loop:
            u_boot_utils.run_and_log(cons, f'sudo losetup -d {loop}')

    if not complete:
        copy_prepared_image(cons, mmc_dev, fname)


def setup_cros_image(cons):
    """Create a 20MB disk image with ChromiumOS partitions"""
    Partition = collections.namedtuple('part', 'start,size,name')
    parts = {}
    disk_data = None

    def pack_kernel(cons, arch, kern, dummy):
        """Pack a kernel containing some fake data

        Args:
            cons (ConsoleBase): Console to use
            arch (str): Architecture to use ('x86' or 'arm')
            kern (str): Filename containing kernel
            dummy (str): Dummy filename to use for config and bootloader

        Return:
            bytes: Packed-kernel data
        """
        kern_part = os.path.join(cons.config.result_dir,
                                 f'kern-part-{arch}.bin')
        u_boot_utils.run_and_log(
            cons,
            f'futility vbutil_kernel --pack {kern_part} '
            '--keyblock doc/chromium/files/devkeys/kernel.keyblock '
            '--signprivate doc/chromium/files/devkeys/kernel_data_key.vbprivk '
            f'--version 1  --config {dummy} --bootloader {dummy} '
            f'--vmlinuz {kern}')

        with open(kern_part, 'rb') as inf:
            kern_part_data = inf.read()
        return kern_part_data

    def set_part_data(partnum, data):
        """Set the contents of a disk partition

        This updates disk_data by putting data in the right place

        Args:
            partnum (int): Partition number to set
            data (bytes): Data for that partition
        """
        nonlocal disk_data

        start = parts[partnum].start * sect_size
        disk_data = disk_data[:start] + data + disk_data[start + len(data):]

    mmc_dev = 5
    fname = os.path.join(cons.config.source_dir, f'mmc{mmc_dev}.img')
    u_boot_utils.run_and_log(cons, f'qemu-img create {fname} 20M')
    #mnt = os.path.join(cons.config.persistent_data_dir, 'mnt')
    #mkdir_cond(mnt)
    u_boot_utils.run_and_log(cons, f'cgpt create {fname}')

    uuid_state = 'ebd0a0a2-b9e5-4433-87c0-68b6b72699c7'
    uuid_kern = 'fe3a2a5d-4f32-41a7-b725-accc3285a309'
    uuid_root = '3cb8e202-3b7e-47dd-8a3c-7ff2a13cfcec'
    uuid_rwfw = 'cab6e88e-abf3-4102-a07a-d4bb9be3c1d3'
    uuid_reserved = '2e0a753d-9e48-43b0-8337-b15192cb1b5e'
    uuid_efi = 'c12a7328-f81f-11d2-ba4b-00a0c93ec93b'

    ptr = 40

    # Number of sectors in 1MB
    sect_size = 512
    sect_1mb = (1 << 20) // sect_size

    required_parts = [
        {'num': 0xb, 'label':'RWFW', 'type': uuid_rwfw, 'size': '1'},
        {'num': 6, 'label':'KERN_C', 'type': uuid_kern, 'size': '1'},
        {'num': 7, 'label':'ROOT_C', 'type': uuid_root, 'size': '1'},
        {'num': 9, 'label':'reserved', 'type': uuid_reserved, 'size': '1'},
        {'num': 0xa, 'label':'reserved', 'type': uuid_reserved, 'size': '1'},

        {'num': 2, 'label':'KERN_A', 'type': uuid_kern, 'size': '1M'},
        {'num': 4, 'label':'KERN_B', 'type': uuid_kern, 'size': '1M'},

        {'num': 8, 'label':'OEM', 'type': uuid_state, 'size': '1M'},
        {'num': 0xc, 'label':'EFI-SYSTEM', 'type': uuid_efi, 'size': '1M'},

        {'num': 5, 'label':'ROOT_B', 'type': uuid_root, 'size': '1'},
        {'num': 3, 'label':'ROOT_A', 'type': uuid_root, 'size': '1'},
        {'num': 1, 'label':'STATE', 'type': uuid_state, 'size': '1M'},
        ]

    for part in required_parts:
        size_str = part['size']
        if 'M' in size_str:
            size = int(size_str[:-1]) * sect_1mb
        else:
            size = int(size_str)
        u_boot_utils.run_and_log(
            cons,
            f"cgpt add -i {part['num']} -b {ptr} -s {size} -t {part['type']} {fname}")
        ptr += size

    u_boot_utils.run_and_log(cons, f'cgpt boot -p {fname}')
    out = u_boot_utils.run_and_log(cons, f'cgpt show -q {fname}')

    # We expect something like this:
    #   8239        2048       1  Basic data
    #     45        2048       2  ChromeOS kernel
    #   8238           1       3  ChromeOS rootfs
    #   2093        2048       4  ChromeOS kernel
    #   8237           1       5  ChromeOS rootfs
    #     41           1       6  ChromeOS kernel
    #     42           1       7  ChromeOS rootfs
    #   4141        2048       8  Basic data
    #     43           1       9  ChromeOS reserved
    #     44           1      10  ChromeOS reserved
    #     40           1      11  ChromeOS firmware
    #   6189        2048      12  EFI System Partition

    # Create a dict (indexed by partition number) containing the above info
    for line in out.splitlines():
        start, size, num, name = line.split(maxsplit=3)
        parts[int(num)] = Partition(int(start), int(size), name)

    dummy = os.path.join(cons.config.result_dir, 'dummy.txt')
    with open(dummy, 'wb') as outf:
        outf.write(b'dummy\n')

    # For now we just use dummy kernels. This limits testing to just detecting
    # a signed kernel. We could add support for the x86 data structures so that
    # testing could cover getting the cmdline, setup.bin and other pieces.
    kern = os.path.join(cons.config.result_dir, 'kern.bin')
    with open(kern, 'wb') as outf:
        outf.write(b'kernel\n')

    with open(fname, 'rb') as inf:
        disk_data = inf.read()

    # put x86 kernel in partition 2 and arm one in partition 4
    set_part_data(2, pack_kernel(cons, 'x86', kern, dummy))
    set_part_data(4, pack_kernel(cons, 'arm', kern, dummy))

    with open(fname, 'wb') as outf:
        outf.write(disk_data)

    return fname

def setup_android_image(cons):
    """Create a 20MB disk image with Android partitions"""
    Partition = collections.namedtuple('part', 'start,size,name')
    parts = {}
    disk_data = None

    def set_part_data(partnum, data):
        """Set the contents of a disk partition

        This updates disk_data by putting data in the right place

        Args:
            partnum (int): Partition number to set
            data (bytes): Data for that partition
        """
        nonlocal disk_data

        start = parts[partnum].start * sect_size
        disk_data = disk_data[:start] + data + disk_data[start + len(data):]

    mmc_dev = 7
    fname = os.path.join(cons.config.source_dir, f'mmc{mmc_dev}.img')
    u_boot_utils.run_and_log(cons, f'qemu-img create {fname} 20M')
    u_boot_utils.run_and_log(cons, f'cgpt create {fname}')

    ptr = 40

    # Number of sectors in 1MB
    sect_size = 512
    sect_1mb = (1 << 20) // sect_size

    required_parts = [
        {'num': 1, 'label':'misc', 'size': '1M'},
        {'num': 2, 'label':'boot_a', 'size': '4M'},
        {'num': 3, 'label':'boot_b', 'size': '4M'},
        {'num': 4, 'label':'vendor_boot_a', 'size': '4M'},
        {'num': 5, 'label':'vendor_boot_b', 'size': '4M'},
    ]

    for part in required_parts:
        size_str = part['size']
        if 'M' in size_str:
            size = int(size_str[:-1]) * sect_1mb
        else:
            size = int(size_str)
        u_boot_utils.run_and_log(
            cons,
            f"cgpt add -i {part['num']} -b {ptr} -s {size} -l {part['label']} -t basicdata {fname}")
        ptr += size

    u_boot_utils.run_and_log(cons, f'cgpt boot -p {fname}')
    out = u_boot_utils.run_and_log(cons, f'cgpt show -q {fname}')

    # Create a dict (indexed by partition number) containing the above info
    for line in out.splitlines():
        start, size, num, name = line.split(maxsplit=3)
        parts[int(num)] = Partition(int(start), int(size), name)

    with open(fname, 'rb') as inf:
        disk_data = inf.read()

    test_abootimg.AbootimgTestDiskImage(cons, 'bootv4.img', test_abootimg.boot_img_hex)
    boot_img = os.path.join(cons.config.result_dir, 'bootv4.img')
    with open(boot_img, 'rb') as inf:
        set_part_data(2, inf.read())

    test_abootimg.AbootimgTestDiskImage(cons, 'vendor_boot.img', test_abootimg.vboot_img_hex)
    vendor_boot_img = os.path.join(cons.config.result_dir, 'vendor_boot.img')
    with open(vendor_boot_img, 'rb') as inf:
        set_part_data(4, inf.read())

    with open(fname, 'wb') as outf:
        outf.write(disk_data)

    print(f'wrote to {fname}')

    return fname

def setup_cedit_file(cons):
    """Set up a .dtb file for use with testing expo and configuration editor"""
    infname = os.path.join(cons.config.source_dir,
                           'test/boot/files/expo_layout.dts')
    inhname = os.path.join(cons.config.source_dir,
                           'test/boot/files/expo_ids.h')
    expo_tool = os.path.join(cons.config.source_dir, 'tools/expo.py')
    outfname = 'cedit.dtb'
    u_boot_utils.run_and_log(
        cons, f'{expo_tool} -e {inhname} -l {infname} -o {outfname}')

@pytest.mark.buildconfigspec('ut_dm')
def test_ut_dm_init(u_boot_console):
    """Initialize data for ut dm tests."""

    fn = u_boot_console.config.source_dir + '/testflash.bin'
    if not os.path.exists(fn):
        data = b'this is a test'
        data += b'\x00' * ((4 * 1024 * 1024) - len(data))
        with open(fn, 'wb') as fh:
            fh.write(data)

    fn = u_boot_console.config.source_dir + '/spi.bin'
    if not os.path.exists(fn):
        data = b'\x00' * (2 * 1024 * 1024)
        with open(fn, 'wb') as fh:
            fh.write(data)

    # Create a file with a single partition
    fn = u_boot_console.config.source_dir + '/scsi.img'
    if not os.path.exists(fn):
        data = b'\x00' * (2 * 1024 * 1024)
        with open(fn, 'wb') as fh:
            fh.write(data)
        u_boot_utils.run_and_log(
            u_boot_console, f'sfdisk {fn}', stdin=b'type=83')

    fs_helper.mk_fs(u_boot_console.config, 'ext2', 0x200000, '2MB')
    fs_helper.mk_fs(u_boot_console.config, 'fat32', 0x100000, '1MB')

    mmc_dev = 6
    fn = os.path.join(u_boot_console.config.source_dir, f'mmc{mmc_dev}.img')
    data = b'\x00' * (12 * 1024 * 1024)
    with open(fn, 'wb') as fh:
        fh.write(data)


def setup_efi_image(cons):
    """Create a 20MB disk image with an EFI app on it"""
    devnum = 1
    basename = 'flash'
    fname, mnt = setup_image(cons, devnum, 0xc, second_part=True,
                             basename=basename)

    loop = None
    mounted = False
    complete = False
    try:
        loop = mount_image(cons, fname, mnt, 'ext4')
        mounted = True
        efi_dir = os.path.join(mnt, 'EFI')
        mkdir_cond(efi_dir)
        bootdir = os.path.join(efi_dir, 'BOOT')
        mkdir_cond(bootdir)
        efi_src = os.path.join(cons.config.build_dir,
                               f'lib/efi_loader/testapp.efi')
        efi_dst = os.path.join(bootdir, 'BOOTSBOX.EFI')
        with open(efi_src, 'rb') as inf:
            with open(efi_dst, 'wb') as outf:
                outf.write(inf.read())
        complete = True
    except ValueError as exc:
        print(f'Falled to create image, failing back to prepared copy: {exc}')

    finally:
        if mounted:
            u_boot_utils.run_and_log(cons, 'sudo umount --lazy %s' % mnt)
        if loop:
            u_boot_utils.run_and_log(cons, 'sudo losetup -d %s' % loop)

    if not complete:
        copy_prepared_image(cons, devnum, fname, basename)


@pytest.mark.buildconfigspec('cmd_bootflow')
@pytest.mark.buildconfigspec('sandbox')
def test_ut_dm_init_bootstd(u_boot_console):
    """Initialise data for bootflow tests"""

    setup_bootflow_image(u_boot_console)
    setup_bootmenu_image(u_boot_console)
    setup_cedit_file(u_boot_console)
    setup_cros_image(u_boot_console)
    setup_android_image(u_boot_console)
    setup_efi_image(u_boot_console)

    # Restart so that the new mmc1.img is picked up
    u_boot_console.restart_uboot()


def test_ut(u_boot_console, ut_subtest):
    """Execute a "ut" subtest.

    The subtests are collected in function generate_ut_subtest() from linker
    generated lists by applying a regular expression to the lines of file
    u-boot.sym. The list entries are created using the C macro UNIT_TEST().

    Strict naming conventions have to be followed to match the regular
    expression. Use UNIT_TEST(foo_test_bar, _flags, foo_test) for a test bar in
    test suite foo that can be executed via command 'ut foo bar' and is
    implemented in C function foo_test_bar().

    Args:
        u_boot_console (ConsoleBase): U-Boot console
        ut_subtest (str): test to be executed via command ut, e.g 'foo bar' to
            execute command 'ut foo bar'
    """

    if ut_subtest == 'hush hush_test_simple_dollar':
        # ut hush hush_test_simple_dollar prints "Unknown command" on purpose.
        with u_boot_console.disable_check('unknown_command'):
            output = u_boot_console.run_command('ut ' + ut_subtest)
        assert 'Unknown command \'quux\' - try \'help\'' in output
    else:
        output = u_boot_console.run_command('ut ' + ut_subtest)
    assert output.endswith('Failures: 0')
