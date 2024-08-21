import hashlib


def hash_file(file, blocksize=65536):
    # Special image hashing algorithms (a-hash, p-hash) might be able to improve this.
    sha = hashlib.sha256()
    file_buffer = file.read(blocksize)
    while len(file_buffer) > 0:
        sha.update(file_buffer)
        file_buffer = file.read(blocksize)

    return sha.hexdigest()
