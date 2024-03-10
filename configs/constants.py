import json

# Untuk kembali ke directory utama
import sys
import os
sys.path.insert(
    0, 
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..'
        )
    )
)

path = os.path.dirname(__file__)

class Constants:
    CATEGORY_VALUES_MAP = json.load(open(path+'/category-map.json'))
    ITEM_NAME_VALUES_MAP = json.load(open(path+'/item-name-map.json'))
    ITEM_SOURCE = {
        "All" : "All",
        "Klik Indomaret" : "klikindomaret",
        "Alfa Gift" : "alfagift"
    }
