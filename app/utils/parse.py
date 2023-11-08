

def filename_reduction(filename: str) -> str:
    """
    Reduce the length of the filename to 100 characters
    :param filename: filename
    :return: reduced filename
    """
    if len(filename) > 100:
        pure_filename = filename.split('/')[-1].split('.')[0]
        file_path = filename.replace(pure_filename, pure_filename[:100])
        return file_path