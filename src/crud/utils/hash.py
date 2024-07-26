import hashlib


def hash_file(file, blocksize=65536):
    sha = hashlib.sha256()
    file_buffer = file.read(blocksize)
    while len(file_buffer) > 0:
        sha.update(file_buffer)
        file_buffer = file.read(blocksize)

    return sha.hexdigest()
