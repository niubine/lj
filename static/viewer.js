document.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('loader');
    const imageCounter = document.getElementById('imageCounter');
    const mainImageWrapper = document.getElementById('mainImageWrapper');
    const thumbnailStrip = document.getElementById('thumbnailStrip');

    let lightGalleryInstance = null;

    async function initializeViewer() {
        const params = new URLSearchParams(window.location.search);
        const albumUrl = params.get('url');
        const count = params.get('count');

        if (!albumUrl || !count) {
            loader.textContent = '错误：缺少图集信息。';
            return;
        }

        try {
            const response = await fetch(`/get_thumbnails?url=${encodeURIComponent(albumUrl)}&count=${count}`);
            if (!response.ok) throw new Error('Failed to fetch image list');

            const imageUrls = await response.json();

            if (imageUrls && imageUrls.length > 0) {
                loader.style.display = 'none';
                createGallery(imageUrls);
            } else {
                loader.textContent = '无法加载图片列表。';
            }
        } catch (error) {
            console.error(error);
            loader.textContent = '加载图片列表失败。';
        }
    }

    function createGallery(imageUrls) {
        // 1. 动态生成 lightGallery 所需的链接列表 (隐藏的)
        const dynamicEl = imageUrls.map(url => ({
            src: url,
            thumb: url, // 使用原图作为缩略图，lightGallery 会处理
        }));

        // 2. 初始化 lightGallery 实例
        lightGalleryInstance = lightGallery(mainImageWrapper, {
            dynamic: true,
            dynamicEl: dynamicEl,
            thumbnail: false, // 我们用自己的缩略图条，禁用插件自带的
            download: false, // 禁用下载按钮
            counter: false, // 禁用计数器，我们用自己的
            slideShowAutoplay: false,
            // 更多自定义选项...
        });

        // 3. 动态生成我们自己的底部缩略图导航条
        imageUrls.forEach((url, index) => {
            const thumbItem = document.createElement('div');
            thumbItem.className = 'thumb-item';
            thumbItem.dataset.index = index;

            const img = document.createElement('img');
            img.src = url;
            img.loading = 'lazy'; // 懒加载缩略图

            const indexSpan = document.createElement('span');
            indexSpan.className = 'thumb-index';
            indexSpan.textContent = index + 1;

            thumbItem.appendChild(img);
            thumbItem.appendChild(indexSpan);

            // 点击缩略图，跳转到对应的大图
            thumbItem.addEventListener('click', () => {
                lightGalleryInstance.slide(index);
            });

            thumbnailStrip.appendChild(thumbItem);
        });

        // 4. 监听 lightGallery 的事件，同步我们的 UI
        mainImageWrapper.addEventListener('lgAfterSlide', (event) => {
            const { index } = event.detail;
            updateActiveThumbnail(index);
            updateCounter(index, imageUrls.length);
        });

        // 5. 初始打开第一张图
        lightGalleryInstance.openGallery();
    }

    function updateActiveThumbnail(currentIndex) {
        // 移除所有 active 状态
        thumbnailStrip.querySelectorAll('.thumb-item').forEach(item => {
            item.classList.remove('active');
        });

        // 为当前缩略图添加 active 状态
        const activeThumb = thumbnailStrip.querySelector(`.thumb-item[data-index='${currentIndex}']`);
        if (activeThumb) {
            activeThumb.classList.add('active');
            // 自动将活动的缩略图滚动到视图中央
            activeThumb.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
                inline: 'center'
            });
        }
    }

    function updateCounter(currentIndex, total) {
        imageCounter.textContent = `${currentIndex + 1} / ${total}`;
    }

    // --- Start the process ---
    initializeViewer();
});
