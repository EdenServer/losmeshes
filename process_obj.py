# Example usage for this test.
#  blender --background --factory-startup --python process_obj.py -- \
#           <obj-file-paths>
# Notice:
# '--factory-startup' is used to avoid the user default settings from
#                     interfering with automated scene generation.
#
# '--' causes blender to ignore all following arguments so python can use them.

#!/usr/bin/env python3

import bpy
import os

def backup_original(file_path):
    print(f"Original obj file will be stored in the 'original' subfolder.")
    original_dir = os.path.join(os.path.dirname(file_path), 'original')
    if not os.path.exists(original_dir):
        os.makedirs(original_dir)
    
    original_file = os.path.join(original_dir, os.path.basename(file_path))

    count = 0
    split = os.path.splitext(os.path.basename(file_path))
    while os.path.exists(original_file):
        count = count + 1
        original_file = os.path.join(original_dir, f'{split[0]}-{count}{"".join(split[1:])}')
    os.rename(file_path, original_file)

def process_obj(file_path):
    file_name = os.path.basename(file_path)
    print(f"Processing {file_name}.")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Import object and set it to be active
    imported_object = bpy.ops.import_scene.obj(filepath=file_path)
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]

    # Apply weld modifier first to ensure grid is connected properly
    bpy.ops.object.modifier_add(type='WELD')
    bpy.context.object.modifiers["Weld"].merge_threshold = 0.001
    bpy.ops.object.modifier_apply(modifier="Weld")

    bpy.ops.object.modifier_add(type='DECIMATE')
    bpy.context.object.modifiers["Decimate"].ratio = 0.2
    bpy.context.object.modifiers["Decimate"].use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier="Decimate")


    backup_original(file_path)
    processed_dir = os.path.join(os.path.dirname(file_path), 'processed')
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
    print(f"Exporting new obj file to 'processed' subfolder.")
    bpy.ops.export_scene.obj(filepath=os.path.join(processed_dir, file_name), use_triangles=True, use_mesh_modifiers=False, use_normals=False, use_uvs=False, use_materials=False)


def main():
    import sys       # to get command line args
    import argparse  # to parse options for us and print a nice help message

    # get the args passed to blender after "--", all of which are ignored by
    # blender so scripts may receive their own arguments
    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    # Parse filepaths as arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('files', metavar='N', type=str, nargs='*', help='obj files to process')
    
    args = parser.parse_args(argv)  # In this example we won't use the args

    if not argv:
        parser.print_help()
        return

    if not args.files:
        print("Error: expected obj files to be given as arguments.")
        parser.print_help()
        return

    # Run the example function
    for file in args.files:
        process_obj(file)

    print("Finished")


if __name__ == "__main__":
    main()
