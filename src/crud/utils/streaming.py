def stream_file(file, blocksize=65536):
    yield from iter(lambda: file.read(blocksize), b"")


def stream_dataset(dataset_gen):
    for file in dataset_gen:
        yield from stream_file(file)
