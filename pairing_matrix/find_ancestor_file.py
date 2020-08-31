import os


def find_ancestor_file(relative_to, ancestor_name):
    """Find a file or directory named `ancestor_name`. Start searching at `relative_to`,
    and traverse directly up the file tree until found."""
    if not os.path.isdir(relative_to):
        parent_folder = os.path.dirname(relative_to)
    else:
        parent_folder = relative_to
    folder = None

    removed = -1
    while folder != parent_folder:  # Stop if we hit the file system root
        folder = parent_folder
        removed += 1
        with os.scandir(folder) as ls:
            for f in ls:
                if f.name == ancestor_name:
                    return f.path
        parent_folder = os.path.normpath(os.path.join(folder, os.pardir))
