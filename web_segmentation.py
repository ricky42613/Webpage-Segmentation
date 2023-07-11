from bs4 import BeautifulSoup, Comment
import math
import itertools
import re

class WebSegmentation:
    def __init__(self):
        self.text_tag = [
            "a", "abbr", "acronym", "address", "area", "aside", "b", "base", "basefont", "bdi",
            "bdo", "big", "br", "caption", "cite", "code", "col", "colgroup", "del", "dfn", "dt", "dir", "em",
            "embed", "figcaption", "font", "h1", "h2", "h3", "h4", "h5", "h6", "head", "hr", "i", "img", "ins", "kbd",
            "keygen", "legend", "li", "link", "mark", "menuitem", "meta", "meter",
            "noframes", "noscript", "optgroup", "option", "output", "p", "param", "pre", "q",
            "rp", "rt", "s", "samp", "script", "small", "source", "span", "strike", "strong", "style",
            "sub", "summary", "sup", "tfoot", "th", "thead", "time", "title", "track", "tt", "u", "var",
            "video", "wbr", "label", "dd"
        ]
        self.ignore_class = 'pageeng_ignore'
        self.block_class = 'pageeng_block'

    def _is_only_text(self, block):
        """
        檢查是否block中只存在text tag
        若只有text tag則回傳text tag數量
        若含有其他則回傳0
        """
        # block_cpy = copy.copy(block)
        if block.name in self.text_tag:
            return len(block.find_all())+1
        block_cpy = BeautifulSoup(str(block), features="lxml")
        for item in block_cpy.select(f".{self.ignore_class}"):
            item.decompose()
        if len(block_cpy.find_all()) == 0:
            return 1
        else:
            link_text_flag = 0
            non_link_text_flag = 0
            text_tag_cnt = 0
            link_text_length = 0
            for tag in self.text_tag:
                if len(block_cpy.select(tag)) != 0:
                    text_tag_cnt += len(block_cpy.select(tag))
                    if tag == "a":
                        link_text_flag = 1
                        for link_item in block_cpy.select(tag):
                            link_text_length += len(link_item.text.strip())
                    else:
                        non_link_text_flag = 1
            if len(block_cpy.text.strip()) == link_text_length:
                return len(block.find_all())+1
            if text_tag_cnt == len(block_cpy.find_all()) - 2:
                return len(block.find_all())+1
            elif link_text_flag + non_link_text_flag < 2:
                return len(block.find_all())+1
            else:
                return 0


    def _get_measure_val(self, block):
        """
        計算node information entropy
        pnl : non link text ratio => ltn/tn
        pl : link text ratio => ntn/tn
        """
        block_cpy = BeautifulSoup(str(block), features="lxml")
        for item in block_cpy.select(f".{self.ignore_class}"):
            item.decompose()
        all_element = block_cpy.find_all()[2:]
        text_cnt = len(re.sub('[\s\n]', '', block_cpy.text))
        link_text_cnt = 0
        max_non_link_text_cnt = 0
        i = 0
        while i < len(all_element):
            skip = 1
            if all_element[i].name == "a":
                link_text_cnt += len(re.sub('[\s\n]', '', all_element[i].text))
                if len(all_element[i].find_all()) == 0:
                    skip = 1
                else:
                    skip = len(all_element[i].find_all())
            else:
                link_len_in_node = 0
                for sub_item in all_element[i].find_all("a"):
                    link_len_in_node += len(re.sub('[\s\n]', '', sub_item.text))
                if len(re.sub('[\s\n]', '', all_element[i].text)) - link_len_in_node > max_non_link_text_cnt:
                    max_non_link_text_cnt = len(re.sub('[\s\n]', '', all_element[i].text)) - link_len_in_node
            i += skip
        pl = link_text_cnt/text_cnt 
        pnl = 1-pl
        if pl == 0 or pnl == 0:
            entropy = 0.1
        else:
            entropy = (-1*pl*math.log2(pl)) + (-1*pnl*math.log2(pnl))
        if text_cnt-link_text_cnt == 0:
            struct_feature = 1
        else:
            struct_feature = max_non_link_text_cnt/(text_cnt-link_text_cnt)
        measure_val = 0.9 * entropy + 0.1 * struct_feature
        print(re.sub('[\s\n]', '', block_cpy.text), entropy, struct_feature, measure_val)
        return measure_val

    def _xpath_soup(self, element):
        """
        Generate xpath of soup element
        :param element: bs4 text or node
        :return: xpath as string
        """
        components = []
        child = element if element.name else element.parent
        for parent in child.parents:
            """
            @type parent: bs4.element.Tag
            """
            previous = itertools.islice(
                parent.children, 0, parent.contents.index(child))
            xpath_tag = child.name
            xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
            components.append(xpath_tag if xpath_index ==
                            1 else '%s[%d]' % (xpath_tag, xpath_index))
            child = parent
        components.reverse()
        return '/%s' % '/'.join(components)


    def _get_next_sibling_skip_ignore(self, block):
        block = block.find_next_sibling()
        if block == None:
            return None
        block_classname = block.get("class")
        if block_classname == None:
            block_classname = []
        while self.ignore_class in block_classname:
            block = block.find_next_sibling()
            if block == None:
                return None
            block_classname = block.get("class")
            if block_classname == None:
                block_classname = []
        return block


    def _parent_is_seg(self, block, seg_blocks):
        while block.name != 'body':
            if block.parent in seg_blocks:
                return True
            block = block.parent
        return False


    def _fusion_similar_blocks(self, blocks):
        item_tag_list = []
        finish_list = []
        ret_blocks = []
        for item in blocks:
            item['class'] = item.get('class', []) + [self.block_class]
            item_tag = ""
            for tag in item.find_all():
                if tag.name not in self.text_tag:
                    item_tag += tag.name
            item_tag_list.append(item_tag)
        for i in range(0, len(blocks)):
            if i not in finish_list:
                i_elem = blocks[i]
                current_tag = item_tag_list[i]
                if len(current_tag) > 0:
                    for j in range(i+1, len(blocks)):
                        j_elem = blocks[j]
                        cmp_tag = item_tag_list[j]
                        if current_tag == cmp_tag:
                            can_merge = 1
                            while i_elem.parent != j_elem.parent:
                                if i_elem.parent.name != j_elem.parent.name:
                                    can_merge = 0
                                    break
                                i_elem = i_elem.parent
                                j_elem = j_elem.parent
                                if i_elem.name == 'body' or j_elem.name == 'body':
                                    can_merge = 0
                                    break
                            if can_merge == 1:
                                block_in_new_parent = i_elem.parent.select(f".{self.block_class}")
                                has_other_thing = 0
                                can_merge_list = []
                                for k in range(0, len(blocks)):
                                    if k != i and k != j:
                                        if blocks[k] in block_in_new_parent and item_tag_list[k] != current_tag:
                                            has_other_thing = 1
                                        elif blocks[k] in block_in_new_parent and item_tag_list[k] == current_tag:
                                            can_merge_list.append(k)

                                if has_other_thing == 1:
                                    for k in range(0, len(blocks)):
                                        if k != i and k != j:
                                            if blocks[k] in block_in_new_parent and item_tag_list[k] == current_tag:
                                                appen_blk = blocks[k]
                                                not_found = 0
                                                while appen_blk.parent != i_elem.parent:
                                                    appen_blk = appen_blk.parent
                                                    if appen_blk.name == "body":
                                                        not_found = 1
                                                        break
                                                if not_found == 0:
                                                    ret_blocks.append(appen_blk)
                                                    finish_list.append(k)
                                    ret_blocks.append(i_elem)
                                    ret_blocks.append(j_elem)
                                    finish_list.append(i)
                                    finish_list.append(j)
                                else:
                                    ret_blocks.append(i_elem.parent)
                                    finish_list.append(i)
                                    finish_list.append(j)
                                    finish_list = finish_list + can_merge_list

        for i in range(0, len(blocks)):
            if i not in finish_list:
                ret_blocks.append(blocks[i])
        return ret_blocks


    def _fusion(self, blocks):
        tmp_ret = []
        fusion_block = []
        for i in range(0, len(blocks)-1):
            if self._get_next_sibling_skip_ignore(blocks[i]) == blocks[i+1] and blocks[i].name in self.text_tag and blocks[i+1].name in self.text_tag:
                if i not in fusion_block:
                    fusion_block.append(i)
                if i+1 not in fusion_block:
                    fusion_block.append(i+1)
                if blocks[i].parent not in tmp_ret:
                    tmp_ret.append(blocks[i].parent)
        for i in range(0, len(blocks)):
            if i not in fusion_block:
                tmp_ret.append(blocks[i])
        ret = []
        tmp_ret = self._fusion_similar_blocks(tmp_ret)

        for item in tmp_ret:
            if not self._parent_is_seg(item, tmp_ret):
                ret.append(self._xpath_soup(item))
        return ret

    def clean_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all('style'):
            item.decompose()
        for item in soup.find_all('script'):
            item.decompose()
        for item in soup.find_all('noscript'):
            item.decompose()
        for item in soup.find_all('head'):
            item.decompose()
        for item in soup.select('[hidden]'):
            # item.decompose()
            item['class'] = item.get('class', []) + [self.ignore_class]
        for item in soup.select('[style*="display:none"]'):
            # item.decompose()
            item['class'] = item.get('class', []) + [self.ignore_class]
        for item in soup.findAll(lambda tag: (not tag.contents or len(re.sub(r"[\n|\t|\s]", "", tag.get_text(strip=True))) <= 0) ):
            # item.decompose() 
            item['class'] = item.get('class', []) + [self.ignore_class]
        for item in soup.select('[tabindex="-1"]'):
            item['class'] = item.get('class', []) + [self.ignore_class]
        div = soup.find('html')
        for item in div(text=lambda text: isinstance(text, Comment)):
            item.extract()
        return soup.prettify()

    def segmentation(self, html):
        """
        切割頁面
        pnl : non link text ratio => ltn/tn
        pl : link text ratio => ntn/tn
        """
        ret = []
        soup = BeautifulSoup(html, "html.parser")
        all_element = soup.find_all("body")[0].find_all()
        i = 0
        while i < len(all_element):
            if all_element[i].get("class") != None:
                if self.ignore_class in all_element[i]['class']:
                    i += len(all_element[i].find_all())+1
                    continue
            if self._is_only_text(all_element[i]) != 0:
                ret.append(all_element[i])
                i += self._is_only_text(all_element[i])
            else:
                measure_val = self._get_measure_val(all_element[i])
                if measure_val < 0.6:
                    ret.append(all_element[i])
                    i += len(all_element[i].find_all())+1
                else:
                    i += 1
        fusion_blocks = self._fusion(ret)

        return fusion_blocks


if __name__ == "__main__":
    f = open("clean.html")
    content = f.read()
    WS = WebSegmentation()
    print(WS.segmentation(content))
