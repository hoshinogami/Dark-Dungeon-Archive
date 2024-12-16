import shutil
from pathlib import Path
from datetime import datetime
def find_subfolder(directory, target_name):
    """
    在给定的目录中查找与目标名称完全匹配的子文件夹。

    :param directory: 要搜索的根目录路径
    :param target_name: 目标子文件夹的名称
    :return: 匹配的子文件夹Path对象列表
    """
    matches = []
    path = Path(directory)

    for entry in path.rglob(target_name):
        if entry.is_dir():
            matches.append(entry)

    return matches


def copy_and_rename_files(source_folder, destination_folder, rename_pattern=None):
    """
    复制源文件夹及其所有子文件夹下的所有文件到目标文件夹，并根据提供的模式重命名文件。
    :param source_folder: 源文件夹路径（Path对象）
    :param destination_folder: 目标文件夹路径（Path对象），如果不存在则会创建
    :param rename_pattern: 用于生成新文件名的模式字符串或函数，默认为None表示不重命名
                           如果是字符串，可以包含'{index}'占位符，它会被替换为递增索引。
                           如果是函数，应接受旧文件名作为参数并返回新的文件名。
    """
    source_folder = Path(source_folder)
    destination_folder = Path(destination_folder)
    destination_folder.mkdir(parents=True, exist_ok=True)  # 确保目标文件夹存在

    def process_directory(src_dir, dest_dir):
        files = [f for f in src_dir.iterdir() if f.is_file()]
        subdirs = [d for d in src_dir.iterdir() if d.is_dir()]

        if callable(rename_pattern):
            rename_func = rename_pattern
        elif isinstance(rename_pattern, str) and '{index}' in rename_pattern:
            rename_func = lambda old_name, idx: rename_pattern.format(index=idx)
        else:
            rename_func = None

        file_index = 1  # 文件计数器，仅用于当前目录下的文件
        for file in files:
            dest_path = dest_dir / (rename_func(file.name, file_index) if rename_func else file.name)
            shutil.copy2(file, dest_path)  # 使用copy2以保留元数据
            print(f"Copied {file.name} to {dest_path}")
            file_index += 1

        for subdir in subdirs:
            new_subdir_path = dest_dir / subdir.name
            new_subdir_path.mkdir(exist_ok=True)
            print(f"Creating subdirectory {new_subdir_path}")
            process_directory(subdir, new_subdir_path)

    # 开始处理源文件夹
    process_directory(source_folder, destination_folder)
def merge_folders(src_folder, dest_folder):
    """
    将源文件夹中的所有内容复制到目标文件夹中，并合并任何同名文件夹或文件。
    :param src_folder: 源文件夹路径（Path对象）
    :param dest_folder: 目标文件夹路径（Path对象）
    """
    for item in src_folder.iterdir():
        dest_item = dest_folder / item.name
        if item.is_dir():
            if dest_item.exists():
                merge_folders(item, dest_item)  # 递归合并子文件夹
            else:
                shutil.copytree(item, dest_item)
        else:
            # 如果文件已存在，则覆盖它
            shutil.copy2(item, dest_item)


def rename_folder_to_copy_or_merge(original_folder):
    """
    将原始文件夹重命名为“原文件名-副本”。如果目标文件夹已存在，则合并内容。
    :param original_folder: 原始文件夹路径（可以是字符串或Path对象）
    """
    # 确保original_folder是Path对象
    original_folder = Path(original_folder)

    if not original_folder.exists() or not original_folder.is_dir():
        print(f"原始文件夹 {original_folder} 不存在或不是一个文件夹")
        return

    # 构建新的文件夹名称
    new_name = f"{original_folder.stem}-副本"
    new_folder_path = original_folder.with_name(new_name)

    try:
        if new_folder_path.exists():
            print(f"目标文件夹 {new_folder_path} 已经存在，开始合并...")
            merge_folders(original_folder, new_folder_path)
            print(f"合并完成：{original_folder} 的内容已合并到 {new_folder_path}")
            # 删除原始文件夹
            shutil.rmtree(original_folder)
            print(f"已删除原始文件夹 {original_folder}")
        else:
            # 执行重命名操作
            original_folder.rename(new_folder_path)
            print(f"已将原始文件夹 {original_folder} 重命名为：{new_folder_path}")
    except Exception as e:
        print(f"处理过程中出错: {e}")

def remove_timestamp_from_folder(folder_path, new_path,timestamp_pattern='%Y%m%d_%H%M%S'):
    """
    直接删除指定文件夹名称中的固定格式时间戳部分。
    :param folder_path: 文件夹路径（可以是字符串或Path对象）
    :param timestamp_pattern: 时间戳格式字符串，默认为'%Y%m%d_%H%M%S'
    """
    # 确保folder_path是Path对象
    folder_path = Path(folder_path)

    if not folder_path.exists() or not folder_path.is_dir():
        print(f"文件夹 {folder_path} 不存在或不是一个文件夹")
        return
    # 获取时间戳格式的长度（包括前缀下划线）
    # 计算时间戳格式的实际长度（包括前缀下划线）
    example_timestamp = datetime.now().strftime(timestamp_pattern)
    timestamp_length = len(f"_{example_timestamp}")  # 包括前缀下划线

    # 检查文件夹名称是否包含时间戳部分
    folder_name = folder_path.name
    if len(folder_name) > timestamp_length and folder_name[-timestamp_length].startswith('_'):
        timestamp_str = folder_name[-timestamp_length + 1:]

        try:
            # 验证时间戳是否符合给定的格式
            datetime.strptime(timestamp_str, timestamp_pattern)
            # 构建新的文件夹名称，去除时间戳部分
            folder_path.rename(new_path)
            # print(f"已将文件夹 {folder_path.name} 重命名为：{new_name}")
        except ValueError:
            print(f"文件夹 {folder_path.name} 的时间戳不符合指定模式，跳过该文件夹。")
    else:
        print(f"文件夹 {folder_path.name} 中未找到符合的时间戳，不做更改。")
def save_game(url,path):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    old_path = Path(url)/"remote"/path
    new_path = f"{old_path}_{timestamp}"
    copy_and_rename_files(old_path, new_path)
    return f"{path}_{timestamp}"
def cover_game(url,path):
    old_path = Path(url) / "remote" / path
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    timestamp_length = len(f"_{timestamp}")
    if "auto" in path:
        tem_path=path[:-timestamp_length-5]
    else:
        tem_path = path[:-timestamp_length]
    new_path=Path(url)/"remote"/tem_path
    rename_folder_to_copy_or_merge(new_path)
    remove_timestamp_from_folder(old_path,new_path)
def auto_save_game(url,path):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    old_path = Path(url) / "remote" / path
    new_path = f"{old_path}_auto_{timestamp}"
    copy_and_rename_files(old_path, new_path)
    return f"{path}_auto_{timestamp}"
def find_archive_name(url):
    un_url=Path(url)/"remote"
    subfolders = [entry.name for entry in Path(un_url).iterdir() if entry.is_dir()]
    return subfolders