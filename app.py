from flask import Flask, render_template, request, jsonify
import threading
import requests
import os
import scraper  # 导入我们分离出的爬虫模块

app = Flask(__name__)

# --- 全局状态管理 ---
# 用一个字典来管理下载状态，这样更清晰
download_status = {
    "is_downloading": False,
    "progress": 0,
    "total": 0,
    "current": 0,
    "current_album": "N/A",
    "cancel_requested": False,
    "download_thread": None
}


# --- 后台下载任务 ---
def download_task(albums_to_download):
    """在后台线程中执行下载的函数"""
    global download_status

    session = requests.Session()
    # 模拟浏览器 headers
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": scraper.BASE_URL
    })

    total_albums = len(albums_to_download)
    for i, album in enumerate(albums_to_download):
        if download_status["cancel_requested"]:
            scraper.logger.info("Download cancelled by user.")
            break

        album_title = album['ztitle']
        author = album['author']
        url = album['ztitle_href']
        total_count = int(album['count'])

        download_status["current_album"] = f"({i + 1}/{total_albums}) {album_title}"
        download_status["progress"] = 0

        scraper.logger.info(f"Starting download for: {album_title}")
        image_urls = scraper.get_image_urls_for_album(session, url, total_count)

        if not image_urls:
            scraper.logger.warning(f"Could not find image URLs for {album_title}")
            continue

        album_dir = os.path.join("downloads", author, album_title)
        os.makedirs(album_dir, exist_ok=True)

        total_images_in_album = len(image_urls)
        download_status["total"] = total_images_in_album
        download_status["current"] = 0

        for idx, img_url in enumerate(image_urls):
            if download_status["cancel_requested"]:
                break

            filename = os.path.basename(img_url)
            filepath = os.path.join(album_dir, filename)

            if scraper.download_image(session, img_url, filepath):
                download_status["current"] = idx + 1
                download_status["progress"] = int((idx + 1) / total_images_in_album * 100)

        scraper.logger.info(f"Finished download for: {album_title}")

    # 重置状态
    download_status["is_downloading"] = False
    download_status["cancel_requested"] = False
    download_status["current_album"] = "下载完成"
    download_status["progress"] = 100


# --- Flask 路由 ---
@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')


@app.route('/search')
def search():
    """处理搜索请求"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    results = []
    if query.startswith(scraper.BASE_URL):
        if "/gallery/" in query:
            results = scraper.crawl_single_gallery(query)
        else:  # 认为是分类或搜索结果页
            results = scraper.crawl_all_pages(query)
    else:  # 认为是关键词搜索
        search_url = scraper.submit_search(query)
        if search_url:
            results = scraper.crawl_all_pages(search_url)

    return jsonify(results)


@app.route('/get_thumbnails')
def get_thumbnails():
    """获取指定图集的所有图片URL"""
    url = request.args.get('url').replace("ojbkcdn.cc", "52xv.com")
    print(url)
    count = request.args.get('count', type=int)
    if not url or not count:
        return jsonify({"error": "URL and count are required."}), 400

    session = requests.Session()
    image_urls = scraper.get_image_urls_for_album(session, url, count)
    return jsonify(image_urls)


@app.route('/download', methods=['POST'])
def download():
    """启动下载任务"""
    global download_status
    if download_status["is_downloading"]:
        return jsonify({"status": "error", "message": "A download task is already running."}), 400

    data = request.get_json()
    if not data or 'albums' not in data:
        return jsonify({"status": "error", "message": "Invalid request body."}), 400

    albums_to_download = data['albums']

    # 初始化状态
    download_status["is_downloading"] = True
    download_status["cancel_requested"] = False
    download_status["progress"] = 0
    download_status["current_album"] = "准备下载..."

    # 启动后台下载线程
    thread = threading.Thread(target=download_task, args=(albums_to_download,))
    download_status["download_thread"] = thread
    thread.start()

    return jsonify({"status": "success", "message": "Download started."})


@app.route('/status')
def status():
    """获取当前下载状态"""
    global download_status
    download_status["download_thread"] = str(download_status["download_thread"])
    return jsonify(download_status)


@app.route('/cancel', methods=['POST'])
def cancel():
    """取消下载"""
    global download_status
    if download_status["is_downloading"]:
        download_status["cancel_requested"] = True
        return jsonify({"status": "success", "message": "Cancellation requested."})
    return jsonify({"status": "error", "message": "No active download to cancel."})


@app.route('/view')
def view_album():
    """渲染专用的图片浏览页面"""
    # 这个路由只负责提供 HTML 骨架
    # 实际的图片URL列表将由页面上的 JS 异步获取
    album_url = request.args.get('url').replace("ojbkcdn.cc", "52xv.com")
    print(album_url)
    album_title = request.args.get('title', '图片浏览器') # 额外传递标题以获得更好体验
    if not album_url:
        return "Error: Missing album URL.", 400
    return render_template('view.html', title=album_title)


if __name__ == '__main__':
    # https://mxd.okyxxs.com/gallery/6456.html
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    app.run(debug=True)

