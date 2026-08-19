#!/usr/bin/env python3
#
# remove.py
#
# Copyright (C) 2013-2014 Ashwin Menon <ashwin.menon@gmail.com>
# Copyright (C) 2015-2024 Track Master Steve <trackmastersteve@gmail.com>
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Alienfx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with alienfx.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#

"""
AlienFX Uninstaller
This script removes the AlienFX application and all its files from a Linux system.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")

def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")

def remove_file(filepath):
    """Remove a single file."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print_success(f"Removed: {filepath}")
            return True
        else:
            print_warning(f"Not found: {filepath}")
            return False
    except Exception as e:
        print_error(f"Failed to remove {filepath}: {e}")
        return False

def remove_directory(dirpath):
    """Remove a directory and all its contents."""
    try:
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)
            print_success(f"Removed directory: {dirpath}")
            return True
        else:
            print_warning(f"Directory not found: {dirpath}")
            return False
    except Exception as e:
        print_error(f"Failed to remove directory {dirpath}: {e}")
        return False

def get_python_site_packages():
    """Get the site-packages directory path."""
    try:
        import site
        site_packages = site.getsitepackages()
        return site_packages
    except Exception as e:
        print_warning(f"Could not determine site-packages location: {e}")
        return []

def uninstall_pip_package():
    """Attempt to uninstall via pip."""
    print_header("Attempting to uninstall via pip...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", "alienfx"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success("Successfully uninstalled via pip")
            return True
        else:
            print_warning("Package not found in pip or pip uninstall failed")
            return False
    except Exception as e:
        print_warning(f"Could not uninstall via pip: {e}")
        return False

def remove_data_files():
    """Remove data files installed by the application."""
    print_header("Removing data files...")
    
    # Define all data files and directories to remove
    data_files = [
        "/usr/share/applications/alienfx.desktop",
        "/usr/local/share/applications/alienfx.desktop",
        "/usr/share/icons/hicolor/scalable/apps/alienfx.svg",
        "/usr/local/share/icons/hicolor/scalable/apps/alienfx.svg",
        "/usr/share/icons/hicolor/48x48/apps/alienfx.png",
        "/usr/local/share/icons/hicolor/48x48/apps/alienfx.png",
        "/usr/share/pixmaps/alienfx.png",
        "/usr/local/share/pixmaps/alienfx.png",
        "/usr/share/man/man1/alienfx.1",
        "/usr/local/share/man/man1/alienfx.1",
        "/usr/share/man/man1/alienfx.1.gz",
        "/usr/local/share/man/man1/alienfx.1.gz",
        "~/.config/alienfx",
    ]
    
    removed_count = 0
    for filepath in data_files:
        if remove_file(filepath):
            removed_count += 1
    
    return removed_count

def remove_udev_rules():
    """Remove udev rules file."""
    print_header("Removing udev rules...")
    
    udev_file = "/etc/udev/rules.d/10-alienfx.rules"
    if remove_file(udev_file):
        # Reload udev rules
        try:
            subprocess.run(["udevadm", "control", "--reload-rules"], check=False)
            subprocess.run(["udevadm", "trigger"], check=False)
            print_success("Reloaded udev rules")
        except Exception as e:
            print_warning(f"Could not reload udev rules: {e}")
        return True
    return False

def remove_executables():
    """Remove executable scripts."""
    print_header("Removing executable scripts...")
    
    executables = [
        "/usr/bin/alienfx",
        "/usr/local/bin/alienfx",
        "/usr/bin/alienfx-gtk",
        "/usr/local/bin/alienfx-gtk",
    ]
    
    removed_count = 0
    for exe in executables:
        if remove_file(exe):
            removed_count += 1
    
    return removed_count

def remove_package_files():
    """Remove Python package files."""
    print_header("Removing Python package files...")
    
    removed_count = 0
    site_packages_dirs = get_python_site_packages()
    
    # Also check common locations
    site_packages_dirs.extend([
        "/usr/lib/python3/dist-packages",
        "/usr/local/lib/python3/dist-packages",
    ])
    
    for site_dir in site_packages_dirs:
        if not os.path.exists(site_dir):
            continue
            
        # Remove alienfx package directory
        alienfx_dir = os.path.join(site_dir, "alienfx")
        if remove_directory(alienfx_dir):
            removed_count += 1
        
        # Remove egg-info directory
        for item in Path(site_dir).glob("alienfx-*.egg-info"):
            if remove_directory(str(item)):
                removed_count += 1
        
        # Remove dist-info directory
        for item in Path(site_dir).glob("alienfx-*.dist-info"):
            if remove_directory(str(item)):
                removed_count += 1
    
    return removed_count

def update_desktop_database():
    """Update desktop database and icon cache."""
    print_header("Updating system caches...")
    
    try:
        # Update desktop database
        subprocess.run(
            ["update-desktop-database", "/usr/share/applications"],
            stderr=subprocess.DEVNULL,
            check=False
        )
        subprocess.run(
            ["update-desktop-database", "/usr/local/share/applications"],
            stderr=subprocess.DEVNULL,
            check=False
        )
        print_success("Updated desktop database")
    except Exception as e:
        print_warning(f"Could not update desktop database: {e}")
    
    try:
        # Update icon cache
        subprocess.run(
            ["gtk-update-icon-cache", "/usr/share/icons/hicolor"],
            stderr=subprocess.DEVNULL,
            check=False
        )
        print_success("Updated icon cache")
    except Exception as e:
        print_warning(f"Could not update icon cache: {e}")

def check_permissions():
    """Check if script is run with sufficient permissions."""
    if os.geteuid() != 0:
        print_warning("This script is not running as root.")
        print_info("Some files may require root privileges to remove.")
        response = input("Continue anyway? [y/N]: ")
        if response.lower() != 'y':
            print_info("Uninstallation cancelled.")
            sys.exit(0)

def main():
    """Main uninstaller function."""
    print_header("═" * 60)
    print_header("AlienFX Uninstaller")
    print_header("═" * 60)
    
    # Check permissions
    check_permissions()
    
    # Confirm uninstallation
    print_info("\nThis will remove AlienFX and all its files from your system.")
    response = input("Do you want to continue? [y/N]: ")
    if response.lower() != 'y':
        print_info("Uninstallation cancelled.")
        sys.exit(0)
    
    # Perform uninstallation steps
    total_removed = 0
    
    # Try pip uninstall first
    if uninstall_pip_package():
        total_removed += 1
    
    # Remove package files manually
    total_removed += remove_package_files()
    
    # Remove executables
    total_removed += remove_executables()
    
    # Remove data files
    total_removed += remove_data_files()
    
    # Remove udev rules
    if remove_udev_rules():
        total_removed += 1
    
    # Update system caches
    update_desktop_database()
    
    # Final summary
    print_header("═" * 60)
    if total_removed > 0:
        print_success(f"\nUninstallation complete! Removed {total_removed} items.")
    else:
        print_warning("\nNo AlienFX files were found on the system.")
    print_header("═" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\nUninstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        sys.exit(1)
