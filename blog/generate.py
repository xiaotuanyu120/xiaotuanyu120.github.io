# coding=utf-8

import os
import re
import json

import mistune
import codecs
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html

from config import Config
from page_info import PageInfo


CONF_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = Config(os.path.join(CONF_DIR, 'conf'), 'blog.ini').conf('blog')


class HighlightRenderer(mistune.Renderer):
    def block_code(self, code, lang):
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % mistune.escape(code)
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = html.HtmlFormatter()
        return highlight(code, lexer, formatter)


class Md2Html(object):
    def __init__(self, md_dir=None, html_dir=None, template_dir=None):
        """
        Md2Html collect md_info and convert md to html

        initial items:
            md_dir: markdown file's absolute path direction
            html_dir: html file's absolute path direction
            extend_file: included in generated html file
            topics_file: topics file that include md title and html path
            index_json_file: store all md_info in json format
            md_info: a dict that store all information of markdown file
        """
        default_md_dir = BLOG["md_dir"]
        default_html_dir = BLOG["html_dir"]
        default_template_dir = BLOG["template_dir"]
        self.md_dir = md_dir or default_md_dir
        self.html_dir = html_dir or default_html_dir
        self.html_index = "/".join((self.html_dir, "index.html"))

        # HTML模板
        self.template_dir = template_dir or default_template_dir
        self.template_0_html_start = "/".join((self.template_dir, "template-0-html-start.html"))
        self.template_1_header = "/".join((self.template_dir, "template-1-header.html"))
        self.template_2_body_nav_begin = "/".join((self.template_dir, "template-2-body-nav-begin.html"))
        self.template_2_body_nav_end = "/".join((self.template_dir, "template-2-body-nav-end.html"))
        self.template_3_body_sidebar_begin = "/".join((self.template_dir, "template-3-body-sidebar-begin.html"))
        self.template_5_body_sidebar_midd01 = "/".join((self.template_dir, "template-5-body-sidebar-midd01.html"))
        self.template_5_body_sidebar_midd02 = "/".join((self.template_dir, "template-5-body-sidebar-midd02.html"))
        self.template_5_body_sidebar_end = "/".join((self.template_dir, "template-5-body-sidebar-end.html"))
        self.template_6_body_footer = "/".join((self.template_dir, "template-6-body-footer.html"))
        self.template_7_body_script = "/".join((self.template_dir, "template-7-body-script.html"))
        self.template_8_html_end = "/".join((self.template_dir, "template-8-html-end.html"))
        self.template_index_begin = "/".join((self.template_dir, "template-index-begin.html"))
        self.template_index_midd = "/".join((self.template_dir, "template-index-midd.html"))
        self.template_index_end = "/".join((self.template_dir, "template-index-end.html"))
        self.template_category_index_begin = "/".join((self.template_dir, "template-category-index-begin.html"))
        self.template_category_index_end = "/".join((self.template_dir, "template-category-index-end.html"))

        # make sure html_dir,md_dir is absolute path to an existing dir
        if not _dir_check(self.html_dir):
            return self.html_dir
        if not _dir_check(self.md_dir):
            return self.md_dir

        self.md_info = {}
        self.extend_file = BLOG["extend_file"]
        # self.topics_file = BLOG["topics_file"]
        self.topics_json = BLOG["topics_json"]
        self.index_json_file = BLOG["index_json_file"]

        ####################################
        # 初始化文章信息，顺序不要换
        ####################################
        # collect md info and html info first
        self.md_info_coll()
        self.html_info_coll()
        # collect topic data base on md_info and html_info
        self.topic_data = self._topic_data()
        # initial page_info get all variables
        self.index_json()
        self.topic_json()
        p_info = PageInfo()
        self.TOPIC_DICT = p_info.get_topic()
        self.CAT_DICT = p_info.get_cat()
        self.LATEST_PAGE = p_info.get_latest_page()
        # get template content
        self.template_content = self._get_template_content()
        self.template_content_topic_for_all = self._get_template_content("ALL")

    def md_info_coll(self):
        '''
        collect markdown file's information
        '''
        for md_path, sub_dir, mds in os.walk(self.md_dir):
            for md in mds:
                md_spl = md.split('.')
                if len(md_spl) > 1 and md_spl[-1] == "md":
                    md_cname = os.path.join(md_path, md)
                    html = md.rsplit(".md")[0] + ".html"
                    self.md_info[md_cname] = {}
                    self.md_info[md_cname]["md"] = md
                    self.md_info[md_cname]["md_path"] = md_path
                    self.md_info[md_cname]['html'] = html

    def html_info_coll(self):
        md_cnames = self.md_info.keys()
        for md_cname in md_cnames:
            # clear header
            result = _header_parse(md_cname)
            if result['error']:
                del self.md_info[md_cname]
                continue
            else:
                self.md_info[md_cname]['headers'] = result['data']

            # clear categories
            categories = self.md_info[md_cname]['headers']['categories']
            cate = _categories_check(md_cname, categories)
            if cate['error']:
                del self.md_info[md_cname]
                continue
            else:
                self.md_info[md_cname]['base_cat'] = cate['data']['base_cat']
                self.md_info[md_cname]['sub_cat'] = cate['data']['sub_cat']

            # collect html complete path
            self.md_info[md_cname]["html_path"] = \
                os.path.join(self.html_dir, categories)
            html_path = self.md_info[md_cname]["html_path"]
            html = self.md_info[md_cname]["html"]
            self.md_info[md_cname]['html_cname'] = \
                os.path.join(html_path, html)

    def html_gen(self):
        '''
        包含了最重要的逻辑部分：
            1、获取md文件列表
            2、分析header和检查其合法性
            3、分析并创建html文件需要保存的目录
            4、生成html文件
        '''
        # start generate html
        md_cnames = self.md_info.keys()
        for md_cname in md_cnames:
            # prepare html_path
            html_path = self.md_info[md_cname]["html_path"]
            if not os.path.isdir(html_path):
                os.makedirs(html_path)

            # if html_file exist and newer than md file, skip generate it
            html_cname = self.md_info[md_cname]["html_cname"]
            if os.path.isfile(html_cname):
                html_mtime = os.path.getmtime(html_cname)
                md_mtime = os.path.getmtime(md_cname)
                mtime_compare = md_mtime - html_mtime
                if mtime_compare <= 0:
                    continue

            md_content = _get_md_content(md_cname)
            renderer = HighlightRenderer()
            content = _generate_html(md_cname, md_content, renderer)

            # prepare template_5_body_sidebar_end identified by cat and sub_cat
            cat = self.md_info[md_cname]["base_cat"]
            sub_cat = self.md_info[md_cname]["sub_cat"]
            template_content_topic_for_sub_cat = self._get_template_content(topic_for=sub_cat)
            template_5_body_sidebar_end = "".join((
                template_content_topic_for_sub_cat["template_5_body_sidebar_end"][0],
                template_content_topic_for_sub_cat["template_5_body_sidebar_end"][1],
                template_content_topic_for_sub_cat["template_5_body_sidebar_end"][2],
                "".join((template_content_topic_for_sub_cat["template_5_body_sidebar_end"][3][cat])),
                template_content_topic_for_sub_cat["template_5_body_sidebar_end"][4]))
            if content:
                with codecs.open(html_cname, 'w', encoding='utf8') as f:
                    f.write(self.template_content["template_0_html_start"])
                    f.write(self.template_content["template_1_header"])
                    f.write(self.template_content["template_2_body_nav"])
                    f.write(self.template_content["template_3_body_sidebar_begin"])
                    f.write(content)
                    f.write(template_5_body_sidebar_end)
                    f.write(self.template_content["template_6_body_footer"])
                    f.write(self.template_content["template_7_body_script"])
                    f.write(self.template_content["template_8_html_end"])
                print "INFO: [%s] convert success." % md_cname
            else:
                del self.md_info[md_cname]
                continue

    def html_gen_index(self):
        """generate index.html of homepage"""
        with codecs.open(self.html_index, 'w', encoding='utf8') as f:
            f.write(self.template_content["template_0_html_start"])
            f.write(self.template_content["template_1_header"])
            f.write(self.template_content["template_2_body_nav"])
            f.write(self.template_content["template_index"])
            f.write(self.template_content["template_6_body_footer"])
            f.write(self.template_content["template_7_body_script"])
            f.write(self.template_content["template_8_html_end"])
        print "INFO: site index.html generate success."

    def html_gen_category_index(self):
        """generate index.html of categories"""
        cats = self.TOPIC_DICT.keys()
        for cat in cats:
            cat_index_file = "/".join((self.html_dir, cat, "index.html"))
            template_category_index = "".join((
                self.template_content_topic_for_all["template_category_index"][0],
                self.template_content_topic_for_all["template_category_index"][1][cat],
                self.template_content_topic_for_all["template_category_index"][2]))
            template_5_body_sidebar_end = "".join((
                self.template_content["template_5_body_sidebar_end"][0],
                self.template_content["template_5_body_sidebar_end"][1],
                self.template_content["template_5_body_sidebar_end"][2],
                self.template_content["template_5_body_sidebar_end"][3][cat],
                self.template_content["template_5_body_sidebar_end"][4]))
            with codecs.open(cat_index_file, 'w', encoding='utf8') as f:
                f.write(self.template_content["template_0_html_start"])
                f.write(self.template_content["template_1_header"])
                f.write(self.template_content["template_2_body_nav"])
                f.write(self.template_content["template_3_body_sidebar_begin"])
                f.write(template_category_index)
                f.write(template_5_body_sidebar_end)
                f.write(self.template_content["template_6_body_footer"])
                f.write(self.template_content["template_7_body_script"])
                f.write(self.template_content["template_8_html_end"])
            print("INFO: category %s index.html generate success." % cat)

    def html_gen_sub_category_index(self):
        """generate index.html of sub categories"""
        cats = self.TOPIC_DICT.keys()
        for cat in cats:
            sub_cats = self.TOPIC_DICT[cat].keys()
            for sub_cat in sub_cats:
                cat_index_file = "/".join((self.html_dir, cat, sub_cat, "index.html"))
                template_content_topic_for_sub_cat = self._get_template_content(topic_for=sub_cat)
                template_category_index = "".join((
                    template_content_topic_for_sub_cat["template_category_index"][0],
                    template_content_topic_for_sub_cat["template_category_index"][1][cat],
                    template_content_topic_for_sub_cat["template_category_index"][2]))
                template_5_body_sidebar_end = "".join((
                    template_content_topic_for_sub_cat["template_5_body_sidebar_end"][0],
                    template_content_topic_for_sub_cat["template_5_body_sidebar_end"][1],
                    template_content_topic_for_sub_cat["template_5_body_sidebar_end"][2],
                    template_content_topic_for_sub_cat["template_5_body_sidebar_end"][3][cat],
                    template_content_topic_for_sub_cat["template_5_body_sidebar_end"][4]))
                with codecs.open(cat_index_file, 'w', encoding='utf8') as f:
                    f.write(self.template_content["template_0_html_start"])
                    f.write(self.template_content["template_1_header"])
                    f.write(self.template_content["template_2_body_nav"])
                    f.write(self.template_content["template_3_body_sidebar_begin"])
                    f.write(template_category_index)
                    f.write(template_5_body_sidebar_end)
                    f.write(self.template_content["template_6_body_footer"])
                    f.write(self.template_content["template_7_body_script"])
                    f.write(self.template_content["template_8_html_end"])
                print("INFO: sub category %s index.html generate success." % sub_cat)

    def _get_template_content(self, topic_for=None):
        """generate a dict which contains all template strings
        no_topic and raw_sub_cat will finally pass to _get_content_list"""
        template_content = {}

        with codecs.open(self.template_0_html_start, 'r', encoding='utf8') as f:
            template_0_html_start = f.read()
            template_content["template_0_html_start"] = template_0_html_start

        with codecs.open(self.template_1_header, 'r', encoding='utf8') as f:
            template_1_header = f.read()
            template_content["template_1_header"] = template_1_header

        template_content["template_2_body_nav"] = self._get_template_2_body_nav()

        with codecs.open(self.template_3_body_sidebar_begin, 'r', encoding='utf8') as f:
            template_3_body_sidebar_begin = f.read()
            template_content["template_3_body_sidebar_begin"] = template_3_body_sidebar_begin

        template_content["template_5_body_sidebar_end"] = self._get_template_5_body_sidebar_end(topic_for=topic_for)

        with codecs.open(self.template_6_body_footer, 'r', encoding='utf8') as f:
            template_6_body_footer = f.read()
            template_content["template_6_body_footer"] = template_6_body_footer

        with codecs.open(self.template_7_body_script, 'r', encoding='utf8') as f:
            template_7_body_script = f.read()
            template_content["template_7_body_script"] = template_7_body_script

        with codecs.open(self.template_8_html_end, 'r', encoding='utf8') as f:
            template_8_html_end = f.read()
            template_content["template_8_html_end"] = template_8_html_end

        template_content["template_index"] = self._get_template_index()

        template_content["template_category_index"] = self._get_template_category_index(topic_for=topic_for)

        return template_content

    def _get_cat_list_html(self):
        """return a string of all topic html items"""
        topic_list = []
        for topic in self._get_topics():
            nav_html = '\n\
            <li role="presentation">\n\
             <a href="/%s" role="menuitem" tabindex="-1">\n\
              %s\n\
             </a>\n\
            </li>' % (topic, topic)
            topic_list.append(nav_html)
        topic_list_html = "".join(topic_list)
        return topic_list_html

    def _get_template_2_body_nav(self):
        # 为nav template中的文档类别列表准备数据
        with codecs.open(self.template_2_body_nav_begin, 'r', encoding='utf8') as f:
            template_2_body_nav_begin = f.read()

        nav_list_html = self._get_cat_list_html()

        with codecs.open(self.template_2_body_nav_end, 'r', encoding='utf8') as f:
            template_2_body_nav_end = f.read()

        return "".join((template_2_body_nav_begin, nav_list_html, template_2_body_nav_end))

    def _get_template_index(self):
        with codecs.open(self.template_index_begin, 'r', encoding='utf8') as f:
            template_index_begin = f.read()

        index_list_html = self._get_cat_list_html()

        with codecs.open(self.template_index_midd, 'r', encoding='utf8') as f:
            template_index_midd = f.read()

        latest_page_htmls = []
        for page, page_url in self.LATEST_PAGE.items():
            page_html = '\n\
       <a href="%s">\n\
        %s\n\
       </a><br>\n' % (page_url, page)
            latest_page_htmls.append(page_html)
        latest_page_raw_htmls = "".join(latest_page_htmls)

        with codecs.open(self.template_index_end, 'r', encoding='utf8') as f:
            template_index_end = f.read()

        return "".join((
            template_index_begin, index_list_html,
            template_index_midd, latest_page_raw_htmls,
            template_index_end))

    def _get_content_list(self, topic_for=None):
        """ return a dict of {cat:sub-cat-html-content}
        topic_for - means will return dict which only contain topics for it.
                    if None, no topics inside
                    if All, all sub_cat contains topics
        """
        content_list_result = {}
        sub_cat_html_end = '\n\
            </ul>\n\
           </li>'
        cats = self.TOPIC_DICT.keys()
        for cat in cats:
            sub_cat_list = []
            sub_cats = self.TOPIC_DICT[cat].keys()
            for sub_cat in sub_cats:
                sub_cat_html_begin = '\n\
           <li class="toctree-l1">\n\
            <a class="reference internal" href="/%s/%s">\n\
              %s\n\
            </a>\n\
            <ul>' % (cat, sub_cat, sub_cat)
                if topic_for == "ALL" or topic_for == sub_cat:
                    topics = self.TOPIC_DICT[cat].get(sub_cat, [])
                    topics_list = []
                    for t in topics:
                        topic_html = '\n\
             <li class="toctree-l2">\n\
              <a class="reference internal" href="%s">\n\
                %s\n\
              </a>\n\
             </li>' % (t[1], t[0])
                        topics_list.append(topic_html)
                    topics_list_html = "".join(topics_list)
                else:
                    topics_list_html = ""
                sub_cat_list.append("".join((sub_cat_html_begin, topics_list_html, sub_cat_html_end)))
            content_list_result[cat] = "".join(sub_cat_list)
        return content_list_result

    def _get_template_category_index(self, topic_for):
        """create html content of template_category_index
        topic_for will pass to _get_content_list
        """
        with codecs.open(self.template_category_index_begin, 'r', encoding='utf8') as f:
            template_category_index_begin = f.read()

        content_index_dict = self._get_content_list(topic_for=topic_for)

        with codecs.open(self.template_category_index_end, 'r', encoding='utf8') as f:
            template_category_index_end = f.read()

        return (template_category_index_begin, content_index_dict, template_category_index_end)

    def _get_template_5_body_sidebar_end(self, topic_for):
        """create html content of template_5_body_sidebar_end
        topic_for will pass to _get_content_list
        """
        with codecs.open(self.template_5_body_sidebar_midd01, 'r', encoding='utf8') as f:
            template_5_body_sidebar_midd01 = f.read()

        index_list_html = self._get_cat_list_html()

        with codecs.open(self.template_5_body_sidebar_midd02, 'r', encoding='utf8') as f:
            template_5_body_sidebar_midd02 = f.read()

        content_index_dict = self._get_content_list(topic_for=topic_for)

        with codecs.open(self.template_5_body_sidebar_end, 'r', encoding='utf8') as f:
            template_5_body_sidebar_end = f.read()

        return (template_5_body_sidebar_midd01, index_list_html, template_5_body_sidebar_midd02, content_index_dict, template_5_body_sidebar_end)

    def topic_index(self):
        '''
        生成self.topics_file文件的主要函数
        '''
        index = _html_cat_parse(self.md_info)
        topics_def_temp = "def topics():\n    topics = "
        topics_def_end = "\n    return topics"
        topics_def = topics_def_temp + index + topics_def_end
        with open(self.topics_file, 'w') as f:
            f.write(topics_def)

    def index_json(self):
        index_data = json.dumps(self.md_info, indent=4)
        with open(self.index_json_file, 'w') as f:
            f.write(index_data)

    def topic_json(self):
        topic_json_data = json.dumps(self.topic_data, indent=4)
        with open(self.topics_json, 'w') as f:
            f.write(topic_json_data)

    def _get_topics(self):
        "return ['cat1', 'cat2', 'cat2', ...]"
        return self.topic_data.keys()

    def _topic_data(self):
        "prepare data for topics.json, data like {cat1:{subcat1:[key1, key2, ...], ...}}"
        topic_data = {}
        for md_cname in self.md_info.keys():
            base_cat = self.md_info[md_cname]['base_cat']
            sub_cat = self.md_info[md_cname]['sub_cat']
            title = self.md_info[md_cname]['headers']['title']
            html_cname = self.md_info[md_cname]['html_cname']
            html_link = html_cname.split(self.html_dir)[1]

            # initial base_cat to a dict and initial sub_cat to a list
            # save title, html_link and sort it
            topic_data.setdefault(base_cat, {}).setdefault(sub_cat, []).append(
                [title, html_link])
            topic_data[base_cat][sub_cat].sort(key=_sort_key)
        return topic_data


def _dir_check(dir):
    """
    make sure dir is absolute path,
    make sure html_dir exist and not a file
    """
    if not os.path.isabs(dir):
        print "%s should be ABSOLUTE PATH like '/path/to/dir'" % dir
        return

    if not os.path.isdir(dir):
        print "%s should be an EXISTING DIR" % dir
        return
    return dir


def _categories_check(md_cname, categories):
    '''
    check categories of md_cname, make sure its format like "linux/advance"
    '''
    result = {'data': {}, 'error': None}

    try:
        base_cat, sub_cat = categories.split('/')
    except ValueError:
        result['error'] = "Wrong CATEGORIES format! depth should be 2!"

    if result['error']:
        print "ERROR: [%s]'s error is '%s'" % (md_cname, result['error'])
    else:
        result['data'] = {'base_cat': base_cat, 'sub_cat': sub_cat}
    return result


def _header_parse(md_cname):
    '''
    parse header info of markdown file, and save it into self.md_info

    parse rules:
        headers totally is 4
        first "---" means start
        second "---" means end
    '''
    with open(md_cname, 'r') as f:
        row_num = 0
        header_list = ['title', 'date', 'categories', 'tags']
        result = {'data': {}, 'error': None}
        for row in f.readlines():
            if result['error']:
                break

            if row.strip() == "":
                continue

            row_num += 1
            if row_num == 1:
                if not row.strip() == "---":
                    result = {'data': {}, 'error': None}
                    result['error'] = "Missing header start tag: '---'!"
                    break
            elif 1 < row_num < 6:
                if ":" not in row:
                    result = {'data': {}, 'error': None}
                    result['error'] = "Missing header seperate tag: ':'!"
                    break
                key, value = row.strip().split(":", 1)
                header_key = key.strip()
                header_value = value.strip()
                if header_key not in header_list:
                    result = {'data': {}, 'error': None}
                    result['error'] = "Invaild header(%s)!" % header_key
                    break
                else:
                    result['data'][header_key] = header_value
                    header_list.remove(header_key)
            elif row_num == 6:
                if not row.strip() == "---":
                    result = {'data': {}, 'error': None}
                    result['error'] = "Missing header end tag: '---'!"
                break

        if result['error']:
            print "ERROR: [%s]'s error is '%s'" % (md_cname, result['error'])
        return result


def _get_md_content(md_cname):
    '''
    return markdown content
    '''
    with open(md_cname, 'r') as f:
        row_num = 0
        content = []
        for line in f.readlines():
            if line.strip() == "":
                content.append(line)
                continue
            row_num += 1
            if row_num > 6:
                content.append(line)
        result = ''.join(content)
        return result


def _generate_html(md_cname, md_content, renderer):
    '''
    convert markdown content to html format
    '''
    try:
        md_content = unicode(md_content, 'utf-8')
        html_content = mistune.Markdown(renderer=renderer)(md_content)
    except TypeError as e:
        print "ERROR: [%s]'s error is '%s'" % (md_cname, str(e))
        return
    return html_content


def _tryint(input):
    '''
    attaching function for _sort_key
    '''
    try:
        return int(input)
    except:
        return input


def _sort_key(in_list):
    '''
    function for sort key by number
    '''
    return [_tryint(c) for c in re.split('([0-9]+)', in_list[0])]


def main(md_dir=None, html_dir=None):
    M2H = Md2Html(md_dir=md_dir, html_dir=html_dir)
    M2H.html_gen()
    M2H.html_gen_index()
    M2H.html_gen_category_index()
    M2H.html_gen_sub_category_index()


if __name__ == "__main__":
    main()
