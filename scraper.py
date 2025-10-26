import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 常量
BASE_URL = "https://www.mxd009.cc"
BASE_URL = "https://mxd.okyxxs.com"


def submit_search(keywords: str) -> str:
    """
    提交搜索请求，返回重定向后的 URL
    """
    form_data = {
        "keyboard": keywords,
        "show": "title",
        "tempid": "1",
        "tbname": "news"
    }

    SEARCH_URL = f"{BASE_URL}/e/search/index.php"
    session = requests.Session()
    response = session.post(SEARCH_URL, data=form_data, allow_redirects=False)

    if response.status_code == 302:
        new_location = response.headers.get("Location")
        return urljoin(SEARCH_URL, new_location)
    else:
        print("未发生重定向，状态码:", response.status_code)
        return ""

def get_total_count(soup: BeautifulSoup) -> int:
    """
    从页面中提取总图片组数
    """
    biaoqian_div = soup.find("div", class_="biaoqian")
    if biaoqian_div:
        p_text = biaoqian_div.find("p").get_text(strip=True)
        match = re.search(r"(\d+)", p_text)
        if match:
            return int(match.group(1))
    return 0

def parse_gallery_items_from_root(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    提取页面中所有图片组信息
    """
    gallery_root = soup.find("div", class_="box galleryList")
    items = []

    if not gallery_root:
        return items

    for li in gallery_root.select("ul.databox > li"):
        img_tag = li.select_one("div.img-box img")
        ztitle_tag = li.select_one("p.ztitle a")
        rtitle_tag = li.select_one("p.rtitle a")
        author_tag = li.select_one("p.ztitle font")
        # 1. 找到所有 class 为 img-box 的 div
        count_tag = li.select_one("em.num")

        href = ztitle_tag["href"] if ztitle_tag and ztitle_tag.has_attr("href") else ""
        full_link = urljoin(BASE_URL, href)
        count = 0
        if count_tag:
            text = count_tag.get_text(strip=True)  # '15P'
            match = re.search(r'\d+', text)
            if match:
                count = int(match.group(0))
                # print(f"图集图片数量: {count}")

        rtitle = rtitle_tag.get_text(strip=True) if rtitle_tag else ""
        if author_tag:
            author = author_tag.get_text(strip=True)
        else:
            author = rtitle
        item = {
            "img": img_tag["src"] if img_tag else "",
            "ztitle": ztitle_tag.get_text(strip=True) if ztitle_tag else "",
            "ztitle_href": full_link,
            "author": author,
            "rtitle": rtitle,
            "count": str(count)
        }

        items.append(item)

    return items

def crawl_single_gallery(url) -> List[Dict[str, str]]:
    """
    提取当前单页面信息
    """

    items = []
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # 判断是否存在 id="tishi" 的 div
        tishi_div = soup.find('div', id='tishi')

        if tishi_div:
            # 未登陆情况下
            # 提取提示中说的“全本XX张图片”
            total_text = tishi_div.find('p').get_text() if tishi_div else ''
            match = re.search(r'全本(\d+)张图片', total_text)
            if match:
                total_count = int(match.group(1))
                # print(f"全图集共有 {total_count} 张图片")
        else:
            # 登陆情况下，默认本程序是不登陆的
            # 从 id="page" 开始找
            page_div = soup.find('div', id='page')

            # 在 page_div 下找 span 含 "1/97" 结构
            if page_div:
                span = page_div.find('span', string=re.compile(r'\d+/\d+'))
                if span:
                    match = re.search(r'\d+/(\d+)', span.text)
                    if match:
                        total_count = int(match.group(1))
                        print("总页数为:", total_count)
                    else:
                        print("未匹配到页码格式。")
                else:
                    print("未找到包含页码的 <span> 标签。")
            else:
                print("未找到 id='page' 的 div。")

        # 获取 gallerypic 区域
        gallery_div = soup.find('div', class_='gallerypic')

        if not gallery_div:
            return items

        # 获取 class 为 gallery_jieshao 的 div
        jieshao_div = soup.find('div', class_='gallery_jieshao')

        # 从中提取 h1 的内容
        if jieshao_div:
            title = jieshao_div.find('h1').get_text(strip=True)
            # print("图集标题:", title)

        type_author = [a.get_text(strip=True) for a in soup.select('.gallery_renwu_title a')]

        first_img = gallery_div.find('img')
        # if first_img and first_img.has_attr('src'):
        #     print("第一个图片地址:", first_img['src'])
        # else:
        #     print("未找到 img 标签")

        item = {
            "img": first_img["src"] if first_img else "",
            "ztitle": title,
            "ztitle_href": url,
            "author": type_author[1],
            "rtitle": type_author[0],
            "count": str(total_count)
        }

        items.append(item)

        return items


    except Exception as e:
        result = "请求失败:" + str(e)
        print(result)
        return items

def crawl_all_pages(search_url: str) -> List[Dict[str, str]]:
    """
    分页抓取所有图片组信息
    """
    all_results = []
    page = 0

    if "searchid" in search_url:
        searchid_match = re.search(r"searchid=(\d+)", search_url)
        if not searchid_match:
            print("无法提取 searchid")
            return []

        searchid = searchid_match.group(1)

        while True:
            # 构造分页 URL
            if page == 0:
                page_url = search_url
            else:
                page_url = f"{BASE_URL}/e/search/result/index.php?page={page}&searchid={searchid}"

            print(f"\n[抓取第 {page + 1} 页] {page_url}")

            try:
                response = requests.get(page_url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
            except Exception as e:
                print("请求失败:", e)
                break

            if page == 0:
                total = get_total_count(soup)
                print(f"[总计] 页面声明图片组总数: {total}")

            results = parse_gallery_items_from_root(soup)
            if not results:
                print("[结束] 当前页无数据，提前结束。")
                break

            all_results.extend(results)

            # 打印当前页的结果
            # for i, item in enumerate(results, 1):
            #    print(f"  第 {len(all_results) - len(results) + i} 项:")
            #    print(f"    缩略图: {item['img']}")
            #    print(f"    主标题: {item['ztitle']}")
            #    print(f"    分类  : {item['rtitle']}")
            #    print(f"    链接  : {item['ztitle_href']}")
            #
            if len(all_results) >= total:
                print("[完成] 已抓取全部项目。")
                break

            page += 1

        return all_results

    else:
        search_url = re.sub(r'_\d+\.html$', '.html', search_url)
        response = requests.get(search_url)
        if not response:
            return "", []

        soup = BeautifulSoup(response.text, "html.parser")

        # 获取总页数
        page_div = soup.find("div", class_="layui-box layui-laypage layui-laypage-default")
        total_pages = 1
        if page_div:
            span = page_div.find("span")
            if span:
                match = re.search(r'\d+/(\d+)', span.text.strip())
                if match:
                    total_pages = int(match.group(1))
                    print(f"总页数：{total_pages}")

        for index in range(1, total_pages + 1):
            page_url = re.sub(r'\.html$', f'_{index}.html', search_url)

            print(f"\n[抓取第 {index + 1} 页] {page_url}")

            try:
                response = requests.get(page_url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
            except Exception as e:
                print("请求失败:", e)
                break

            results = parse_gallery_items_from_root(soup)
            if not results:
                print("[结束] 当前页无数据，提前结束。")
                break

            all_results.extend(results)

        return all_results


from urllib.parse import urlparse, urlunparse
import os


def get_image_urls_for_album(session, url: str, total_count: int) -> List[str]:
    """根据图集首页URL和图片总数，获取所有图片的URL列表"""
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch album page {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    img_tags = soup.select("div.gallerypic img")
    if not img_tags:
        return []

    first_img_url = img_tags[0].get("src", "")
    if not first_img_url:
        return []

    ext_match = re.search(r'\.(jpg|png|jpeg|gif|webp)$', first_img_url, re.IGNORECASE)
    extension = ext_match.group(0) if ext_match else ".jpg"

    is_numbered_padded = re.search(r"/(\d{3})\.[a-zA-Z]+$", first_img_url)
    image_urls = []

    img_index_match = re.search(r'/(\d+)\.(jpg|png|jpeg|gif|webp)$', first_img_url)
    img_index = 0
    if img_index_match:
        img_index = int(img_index_match.group(1))

    parsed = urlparse(first_img_url)
    base_path = os.path.dirname(parsed.path)
    base_url = urlunparse((parsed.scheme, parsed.netloc, base_path, '', '', ''))

    start_index = 1 if img_index <= 1 else img_index

    if is_numbered_padded:
        for i in range(start_index, start_index + total_count):
            img_url = f"{base_url}/{i:03d}{extension}".replace("ojbkcdn.cc", "52xv.com")
            image_urls.append(img_url)
    else:
        for i in range(start_index, start_index + total_count):
            img_url = f"{base_url}/{i}{extension}".replace("ojbkcdn.cc", "52xv.com")
            image_urls.append(img_url)

    return image_urls


def download_image(session, url: str, filepath: str) -> bool:
    """下载单个图片"""
    if os.path.exists(filepath):
        logger.info(f"File already exists, skipping: {filepath}")
        return True
    try:
        response = session.get(url, timeout=15, stream=True)
        response.raise_for_status()
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return False
