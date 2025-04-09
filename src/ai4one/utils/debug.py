def print_file_head(file_path, num_lines=10, encoding="utf8"):
    """
    打印文件的前 num_lines 行，并显示每行的行号。

    :param file_path: 文件的路径
    :param num_lines: 要打印的行数，默认为10
    :param encoding: 文件的编码格式，默认为'utf8'
    """
    length_str = len("print_file_head =>" + file_path) + 10
    print(f"print_file_head => {file_path}".center(length_str, "="))
    try:
        with open(file_path, "r", encoding=encoding) as f:
            for line_number, line in enumerate(f, start=1):
                if line_number > num_lines:
                    break
                print(f"Line {line_number}: {line}", end="")
        print("=" * length_str)
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
