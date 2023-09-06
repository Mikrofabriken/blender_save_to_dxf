
import bpy
import sys
import importlib
import subprocess
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "save-as-dxf",
    "author" : "Ulrik Holmén",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 0),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

# Blender's Python executable
pybin = sys.executable

def add_user_site():
    # Locate users site-packages (writable)
    user_site = subprocess.check_output([pybin, "-m", "site", "--user-site"])
    user_site = user_site.decode("utf8").rstrip("\n")   # Convert to string and remove line-break
    # Add user packages to sys.path (if it exits)
    user_site_exists = user_site is not None
    if user_site not in sys.path and user_site_exists:
        sys.path.append(user_site)
    return user_site_exists

def enable_pip():
    if importlib.util.find_spec("pip") is None:
        subprocess.check_call([pybin, "-m", "ensurepip", "--user"])
        subprocess.check_call([pybin, "-m", "pip", "install", "--upgrade", "pip", "--user"])
    
def install_module(module : str):
    if importlib.util.find_spec(module) is None:
        subprocess.check_call([pybin, "-m", "pip", "install", module, "--user"])

user_site_added = add_user_site()
enable_pip()
# All the modules you need, that don't come shipped with Blender
modules = ["ezdxf"] 
for module in modules:
    print("Installing module {}".format(module))
    install_module(module)
# If there was no user-site before...
if not user_site_added:
    add_user_site()

from . import auto_load

auto_load.init()

def register():
    auto_load.register()

def unregister():
    auto_load.unregister()


