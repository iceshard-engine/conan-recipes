import filecmp
import os
import shutil

from conan.errors import ConanException
from conan.tools.files.copy_pattern import _filter_files, _copy_files_symlinked_to_folders

def _ice_copy(conanfile, pattern, src, dst, keep_path=True, excludes=None,
         ignore_case=True, overwrite_equal=False, resolve_symlinks=False):
    if src == dst:
        raise ConanException("copy() 'src' and 'dst' arguments must have different values")
    if pattern.startswith(".."):
        raise ConanException("copy() it is not possible to use relative patterns starting with '..'")
    if src is None:
        raise ConanException("copy() received 'src=None' argument")

    # This is necessary to add the trailing / so it is not reported as symlink
    src = os.path.join(src, "")
    excluded_folder = dst
    files_to_copy, files_symlinked_to_folders = _filter_files(src, pattern, excludes, ignore_case,
                                                              excluded_folder)

    copied_files = _ice_copy_files(files_to_copy, src, dst, keep_path, overwrite_equal, resolve_symlinks)
    copied_files.extend(_copy_files_symlinked_to_folders(files_symlinked_to_folders, src, dst))
    if conanfile:  # Some usages still pass None
        copied = '\n    '.join(files_to_copy)
        conanfile.output.debug(f"copy(pattern={pattern}) copied {len(copied_files)} files\n"
                               f"  from {src}\n"
                               f"  to {dst}\n"
                               f"  Files:\n    {copied}")
    return copied_files

def _ice_copy_files(files, src, dst, keep_path, overwrite_equal, resolve_symlinks):
    """ executes a multiple file copy from [(src_file, dst_file), (..)]
    managing symlinks if necessary
    """
    copied_files = []
    for filename in files:
        abs_src_name = os.path.join(src, filename)
        filename = filename if keep_path else os.path.basename(filename)
        abs_dst_name = os.path.normpath(os.path.join(dst, filename))
        parent_folder = os.path.dirname(abs_dst_name)
        if parent_folder:  # There are cases where this folder will be empty for relative paths
            os.makedirs(parent_folder, exist_ok=True)

        if os.path.islink(abs_src_name):
            if resolve_symlinks == False:
                linkto = os.readlink(abs_src_name)
                try:
                    os.remove(abs_dst_name)
                except OSError:
                    pass
                os.symlink(linkto, abs_dst_name)
            else: # Resolve the file and copy the original into it's place
                linkto = os.path.realpath(abs_src_name)
                try:
                    os.remove(abs_dst_name)
                except OSError:
                    pass
                shutil.copy2(linkto, abs_dst_name)
        else:
            # Avoid the copy if the file exists and has the exact same signature (size + mod time)
            if overwrite_equal or not os.path.exists(abs_dst_name) \
                    or not filecmp.cmp(abs_src_name, abs_dst_name):
                shutil.copy2(abs_src_name, abs_dst_name)
        copied_files.append(abs_dst_name)
    return copied_files
