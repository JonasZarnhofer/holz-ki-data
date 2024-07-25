"""
This script uploads all images from the given directories to the minio server.
It was only used once to migrate the old dataset from the filesystem to the minio server.
"""

import os
import requests


HOST = "http://localhost:8002"

BASE_DIR = "/home/arch/code/diplomarbeit/holz-ki-old/data/"
TRAIN_DIRS = [BASE_DIR + "oak_data_2/train/"]
TEST_DIRS = [BASE_DIR + "oak_data_2/test/"]

TEST_BUCKET = "test"
TRAIN_BUCKET = "train"

CATEGORIES = [
    "ast",
    "ast_punkt",
    "ast_faul",
    "splint",
    "riss",
    "verfaerbung",
    "ungehobelt",
]


def get_category(name: str):
    for category in CATEGORIES:
        if category in name:
            return category
    return None


def migrate_train(data_dir: str):
    for file in sorted(os.listdir(data_dir)):
        if file.endswith(".jpg"):
            path = os.path.join(data_dir, file)
            print(path)

            category = get_category(file)
            with open(path, "rb") as f:
                r = requests.post(
                    HOST + "/image/train/" + category,
                    files={"image": ("image", f, "image/jpeg")},
                )


def migrate_test(data_dir: str):
    for file in sorted(os.listdir(data_dir)):
        if file.endswith(".jpg"):
            path = os.path.join(data_dir, file)
            print(path)

            category = get_category(file)
            with open(path, "rb") as f:
                r = requests.post(
                    HOST + "/image/test/" + category,
                    files={"image": ("image", f, "image/jpeg")},
                )


for dir in TRAIN_DIRS:
    migrate_train(dir)

for dir in TEST_DIRS:
    migrate_test(dir)
