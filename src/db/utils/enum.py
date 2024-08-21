from categories import DATASETS, ERROR_CATEGORIES


DATASET_CATEGORIES_DB_NONE = "None"
ERROR_CATEGORIES_DB_NONE = "None"
# Images that have not been labeld by someone will be saved in these categories
# They are stored for labeling at a later time
DATASET_CATEGORIES_DB = DATASETS + [DATASET_CATEGORIES_DB_NONE]
ERROR_CATEGORIES_DB = ERROR_CATEGORIES + [ERROR_CATEGORIES_DB_NONE]
