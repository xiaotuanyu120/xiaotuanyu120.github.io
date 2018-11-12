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
        self.template_2_body_nav = "/".join((self.template_dir, "template-2-body-nav.html"))
        self.template_3_body_sidebar_start = "/".join((self.template_dir, "template-3-body-sidebar-start.html"))
        self.template_5_body_sidebar_end = "/".join((self.template_dir, "template-5-body-sidebar-end.html"))
        self.template_6_body_footer = "/".join((self.template_dir, "template-6-body-footer.html"))
        self.template_7_body_script = "/".join((self.template_dir, "template-7-body-script.html"))
        self.template_8_html_end = "/".join((self.template_dir, "template-8-html-end.html"))
        self.template_index = "/".join((self.template_dir, "template-index.html"))

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

        # collect md info and html info first
        self.md_info_coll()
        self.html_info_coll()

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
            if content:
                '''
                使用HTML模板及动态内容生成HTML文件
                '''
                with codecs.open(self.template_0_html_start, 'r', encoding='utf8') as f:
                    template_0_html_start = f.read()

                with codecs.open(self.template_1_header, 'r', encoding='utf8') as f:
                    template_1_header = f.read()

                with codecs.open(self.template_2_body_nav, 'r', encoding='utf8') as f:
                    template_2_body_nav = f.read()

                with codecs.open(self.template_3_body_sidebar_start, 'r', encoding='utf8') as f:
                    template_3_body_sidebar_start = f.read()

                with codecs.open(self.template_5_body_sidebar_end, 'r', encoding='utf8') as f:
                    template_5_body_sidebar_end = f.read()

                with codecs.open(self.template_6_body_footer, 'r', encoding='utf8') as f:
                    template_6_body_footer = f.read()

                with codecs.open(self.template_7_body_script, 'r', encoding='utf8') as f:
                    template_7_body_script = f.read()

                with codecs.open(self.template_8_html_end, 'r', encoding='utf8') as f:
                    template_8_html_end = f.read()

                with codecs.open(html_cname, 'w', encoding='utf8') as f:
                    f.write(template_0_html_start)
                    f.write(template_1_header)
                    f.write(template_2_body_nav)
                    f.write(template_3_body_sidebar_start)
                    f.write(content)
                    f.write(template_5_body_sidebar_end)
                    f.write(template_6_body_footer)
                    f.write(template_7_body_script)
                    f.write(template_8_html_end)
                print "INFO: [%s] convert success." % md_cname
            else:
                del self.md_info[md_cname]
                continue

    def html_gen_index(self):
        with codecs.open(self.template_0_html_start, 'r', encoding='utf8') as f:
            template_0_html_start = f.read()

        with codecs.open(self.template_1_header, 'r', encoding='utf8') as f:
            template_1_header = f.read()

        with codecs.open(self.template_2_body_nav, 'r', encoding='utf8') as f:
            template_2_body_nav = f.read()

        with codecs.open(self.template_3_body_sidebar_start, 'r', encoding='utf8') as f:
            template_3_body_sidebar_start = f.read()

        with codecs.open(self.template_5_body_sidebar_end, 'r', encoding='utf8') as f:
            template_5_body_sidebar_end = f.read()

        with codecs.open(self.template_6_body_footer, 'r', encoding='utf8') as f:
            template_6_body_footer = f.read()

        with codecs.open(self.template_7_body_script, 'r', encoding='utf8') as f:
            template_7_body_script = f.read()

        with codecs.open(self.template_8_html_end, 'r', encoding='utf8') as f:
            template_8_html_end = f.read()

        with codecs.open(self.template_index, 'r', encoding='utf8') as f:
            template_index = f.read()

        with codecs.open(self.html_index, 'w', encoding='utf8') as f:
            f.write(template_0_html_start)
            f.write(template_1_header)
            f.write(template_2_body_nav)
            f.write(template_index)
            f.write(template_6_body_footer)
            f.write(template_7_body_script)
            f.write(template_8_html_end)
        print "INFO: site index.html generate success."


class IndexJsonGen(Md2Html):
    def __init__(self):
        super(IndexJsonGen, self).__init__()

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
        topic_data = {}
        for md_cname in self.md_info.keys():
            base_cat = self.md_info[md_cname]['base_cat']
            sub_cat = self.md_info[md_cname]['sub_cat']
            title = self.md_info[md_cname]['headers']['title']
            html_cname = self.md_info[md_cname]['html_cname']
            html_link = html_cname.split(self.html_dir)[1]

            # initial base_cat to a dict
            # if not base_cat in topic_data.keys():
            #     topic_data[base_cat] = {}

            # initial sub_cat to a list
            # if not sub_cat in topic_data[base_cat].keys():
            #     topic_data[base_cat][sub_cat] = []

            # save title, html_link and sort it
            # topic_data[base_cat][sub_cat].append([title, html_link])

            # initial base_cat to a dict and initial sub_cat to a list
            # save title, html_link and sort it
            topic_data.setdefault(base_cat, {}).setdefault(sub_cat, []).append(
                [title, html_link])
            topic_data[base_cat][sub_cat].sort(key=_sort_key)
        topic_data = json.dumps(topic_data, indent=4)
        with open(self.topics_json, 'w') as f:
            f.write(topic_data)


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
    IJG = IndexJsonGen()
    IJG.index_json()
    IJG.topic_json()
    M2H = Md2Html(md_dir=md_dir, html_dir=html_dir)
    M2H.html_gen_index()
    M2H.html_gen()


if __name__ == "__main__":
    main()
