import os
import json
import operator

from config import Config

# get config file
CONF_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = Config(os.path.join(CONF_DIR, 'conf'), 'blog.ini').conf('blog')


class PageInfo(object):
    """PageInfo get all info of markdown page"""
    def __init__(self):
        # load json file that save all markdown page info
        with open(BLOG['topics_json'], 'r') as json_file:
            self.TOPIC_DICT = json.load(json_file)

        with open(BLOG['index_json_file'], 'r') as json_file:
            self.INDEX_JSON = json.load(json_file)

    def get_cat(self):
        # get base_cat and sub_cat of markdown page info
        CAT_DICT = {}
        for i in self.INDEX_JSON:
            base_cat = self.INDEX_JSON[i]["base_cat"]
            if not base_cat in CAT_DICT.keys():
                CAT_DICT[base_cat] = []
            sub_cat = self.INDEX_JSON[i]["sub_cat"]
            if not sub_cat in CAT_DICT[base_cat]:
                CAT_DICT[base_cat].append(sub_cat)
        return CAT_DICT

    def get_topic(self):
        return self.TOPIC_DICT

    def get_index(self):
        return self.INDEX_JSON

    def sort_latest(self, input):
        return input['headers']['date']

    def get_latest_page(self):
        page_index = self.INDEX_JSON.values()
        sorted_ph = sorted(page_index, key=self.sort_latest, reverse=True)
        latest_page = {x['headers']['title']:'/'.join([x['headers']['categories'],x['html']]) for x in sorted_ph[:10]}
        return latest_page


if __name__ == '__main__':
    p_info = PageInfo()
    print p_info.get_latest_page()
