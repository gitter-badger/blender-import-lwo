import os
import sys
import re
import time
import zipfile
import shutil
import bpy

def mkdir_p(outfile):
    dirname = os.path.dirname(outfile).split("/")
    for i in range(len(dirname)):
        new_path = "/".join(dirname[0:i+1])
        if not os.path.isdir(new_path):
            os.mkdir(new_path)

def zip_addon(addon):
    bpy_module = re.sub(".py", "", os.path.basename(os.path.realpath(addon)))
    zfile = os.path.realpath(bpy_module + ".zip")

    print(f"Zipping addon - {bpy_module}")

    zf = zipfile.ZipFile(zfile, "w")
    if os.path.isdir(addon):
        for dirname, subdirs, files in os.walk(addon):
            zf.write(dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename))
    else:
        zf.write(addon)
    zf.close()
    return (bpy_module, zfile)


def copy_addon(bpy_module, zfile):
    print(f"Copying addon - {bpy_module}")

    bpy.ops.wm.addon_install(overwrite=True, filepath=zfile)
    bpy.ops.wm.addon_enable(module=bpy_module)


def cleanup(addon, bpy_module):
    print(f"Cleaning up - {bpy_module}")
    bpy.ops.wm.addon_disable(module=bpy_module)

    # addon_remove does not work correctly in CLI
    # bpy.ops.wm.addon_remove(bpy_module=bpy_module)
    addon_dirs = bpy.utils.script_paths(subdir="addons")
    addon = os.path.join(addon_dirs[-1], addon)
    if os.path.isdir(addon):
        time.sleep(0.1)  # give some time for the disable to take effect
        shutil.rmtree(addon)
    else:
        os.remove(addon)

class SetupAddon(object):
    def __init__(self, addon):
        self.addon = addon

    def configure(self):
        (self.bpy_module, self.zfile) = zip_addon(self.addon)
        copy_addon(self.bpy_module, self.zfile)

    def unconfigure(self):
        cleanup(self.addon, self.bpy_module)

    def convert_lwo(self, infile, outfile=None):
        bpy.ops.import_scene.lwo(filepath=infile)
        
        if None == outfile:
            rev = f"{bpy.app.version[0]}.{bpy.app.version[1]}"
            new_path = f"ref_blend/{rev}"
            outfile = re.sub("src_lwo", new_path, infile + ".blend")
        
        mkdir_p(outfile)
                
        bpy.ops.wm.save_mainfile(filepath=outfile)

    def set_cycles(self):
        bpy.context.scene.render.engine = 'CYCLES'


def get_version(bpy_module):
    mod = sys.modules[bpy_module]
    return mod.bl_info.get("version", (-1, -1, -1))
