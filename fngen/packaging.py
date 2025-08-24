import os
from pathlib import Path
import shutil
import tarfile
import tempfile
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern


from typing import List


def package_source(source_root_path, format_type: str = 'tar'):
    if format_type not in ['tar', 'zip']:
        raise ValueError(
            f"Unsupported archive format: '{format_type}'. Must be 'tar' or 'zip'.")

    _, _, _, package_file_paths = get_packaged_files(
        source_root_path=source_root_path)

    with tempfile.TemporaryDirectory() as temp_dir_str:
        staging_dir = Path(temp_dir_str)
        # print(f"Staging deployment in: {staging_dir}")

        copy_directory_with_whitelist(
            source_root_path, staging_dir, package_file_paths)

        archive_base_name = Path(tempfile.gettempdir()) / \
            f"fngen_deployment_{os.urandom(8).hex()}"

        shutil_format = 'gztar' if format_type == 'tar' else 'zip'

        # print(f"Creating '{format_type}' archive from {staging_dir}...")

        archive_path_str = shutil.make_archive(
            base_name=str(archive_base_name),
            format=shutil_format,
            root_dir=staging_dir
        )

        archive_path = Path(archive_path_str)
        # print(f"Archive created: {archive_path}")

    return archive_path


def path_spec(content: List[str]) -> PathSpec:
    all_pattern_lines: List[str] = []
    for content_string in content:
        all_pattern_lines.extend(content_string.splitlines())

    processed_lines = [
        line for line in all_pattern_lines
        if line.strip() and not line.strip().startswith('#')
    ]

    return PathSpec.from_lines(GitWildMatchPattern, processed_lines)


def should_include_path(path: str, include_spec, ignore_spec) -> bool:
    """
    Determines whether a given path should be included based on the include and ignore specs.
    """
    is_included = include_spec.match_file(path)
    is_ignored = ignore_spec.match_file(path)
    return is_included or not is_ignored


def filter_dir_files_from_walk(
    directory: str,
    ignore_content_blocks: List[str],
    include_content_blocks: List[str]
) -> List[str]:
    directory = os.path.abspath(directory)
    if not os.path.isdir(directory):
        return []

    ignore_spec = path_spec(ignore_content_blocks)
    include_spec = path_spec(include_content_blocks)

    packaged_files: List[str] = []

    for root, dirs, files in os.walk(directory, topdown=True):
        original_dirs = list(dirs)
        dirs[:] = [
            d for d in original_dirs
            if should_include_path(
                os.path.relpath(os.path.join(root, d),
                                directory).rstrip("/") + "/",
                include_spec,
                ignore_spec
            )
        ]

        for file_name in files:
            file_path_rel = os.path.relpath(
                os.path.join(root, file_name), directory)
            if should_include_path(file_path_rel, include_spec, ignore_spec):
                packaged_files.append(file_path_rel)

    return packaged_files


def copy_directory_with_whitelist(src_dir, dst_dir, whitelist):
    """
    Copies only the files listed in `whitelist` from `src_dir` to `dst_dir`.

    :param src_dir: Root source directory.
    :param dst_dir: Root destination directory.
    :param whitelist: List of relative file paths (relative to `src_dir`) to copy.
    """
    for rel_path in whitelist:
        src_path = os.path.join(src_dir, rel_path)
        dst_path = os.path.join(dst_dir, rel_path)

        # Create destination directories if needed
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)

        # Copy the file
        shutil.copy2(src_path, dst_path)


def _read_file_content(filepath: str, default: str = "") -> str:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return default


FNIGNORE_NAME = ".fnignore"
FNINCLUDE_NAME = ".fninclude"
GITIGNORE_NAME = ".gitignore"


def get_packaged_files(source_root_path):
    fnignore_content = _read_file_content(
        os.path.join(source_root_path, FNIGNORE_NAME))
    fninclude_content = _read_file_content(
        os.path.join(source_root_path, FNINCLUDE_NAME))
    gitignore_content = _read_file_content(
        os.path.join(source_root_path, GITIGNORE_NAME))

    package_file_paths = filter_dir_files_from_walk(
        source_root_path, [gitignore_content, fnignore_content], [fninclude_content])

    return fnignore_content, fnignore_content, gitignore_content, package_file_paths
