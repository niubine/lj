document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const resultsTableBody = document.querySelector('#resultsTable tbody');
    const previewImage = document.getElementById('previewImage');
    const onlineLink = document.getElementById('onlineLink');
    const downloadSelectedBtn = document.getElementById('downloadSelectedBtn');
    const downloadAllBtn = document.getElementById('downloadAllBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const showThumbnailsBtn = document.getElementById('showThumbnailsBtn');

    const albumLabel = document.getElementById('albumLabel');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');

    // --- NEW: Add variables for our modal ---
    const modal = document.getElementById('thumbnailModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalClose = document.querySelector('.modal .close');
    const thumbnailGrid = document.getElementById('thumbnailGrid');

    let lightGalleryInstance = null; // 用于存储 lightGallery 实例
    let searchResults = [];
    let statusInterval = null;

    lightGalleryInstance = lightGallery(thumbnailGrid, {
        selector: '.grid-item a',
        plugins: [lgZoom, lgThumbnail], // Ensure lgZoom is included
        licenseKey: 'your_license_key', // Optional

        // --- General Settings for a better experience ---
        speed: 500,
        download: false, // Let's keep the UI clean, disable download button

        // --- ZOOM PLUGIN CONFIGURATION ---

        // a. Enable zoom controls (the '+' and '-' buttons)
        // This is enabled by default, but we'll be explicit.
        controls: true,

        // b. Enable zooming with mouse wheel
        // This is also enabled by default.
        mousewheel: true,

        // c. Enable double click to zoom
        // By default, double click toggles fullscreen. Let's change it to toggle zoom.
        doubleTapZoom: true, // This enables double-click/double-tap to zoom
        toggleThumb: true, // Let's not toggle thumbnails on double click

        // d. Configure zoom levels
        // The scale property defines the zoom steps when using buttons or double-click.
        // Example: [1, 1.5, 2.5] means first click zooms to 1.5x, second to 2.5x.
        scale: 1, // Default initial scale
        zoomFromOrigin: true, // Nice animation effect from thumbnail

        // e. Behavior of double click: zoom to actual size (100%)
        // This is a highly requested feature. When you double click, it will zoom to the image's
        // original resolution. Another double click will zoom back out.
        actualSize: true,

        // f. Allow zooming beyond the original image size
        // Set to false if you don't want images to become pixelated.
        // Set to true for maximum zoom capability.
        allowMediaOverlap: true,
    });

    // --- Event Listeners ---
    modalClose.addEventListener('click', () => {
        modal.style.display = 'none';
        if (lightGalleryInstance) {
            lightGalleryInstance.destroy(); // Important: cleanup
            lightGalleryInstance = null;
        }
    });

    window.addEventListener('click', (e) => {
        if (e.target == modal) {
            modal.style.display = 'none';
            if (lightGalleryInstance) {
                lightGalleryInstance.destroy();
                lightGalleryInstance = null;
            }
        }
    });

    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    resultsTableBody.addEventListener('click', (e) => {
        const row = e.target.closest('tr');
        if (!row) return;

        document.querySelectorAll('#resultsTable tbody tr').forEach(r => r.classList.remove('selected'));
        row.classList.add('selected');
        updatePreview(row.dataset.index);
    });

    downloadSelectedBtn.addEventListener('click', downloadSelected);
    downloadAllBtn.addEventListener('click', downloadAll);
    cancelBtn.addEventListener('click', cancelDownload);
    showThumbnailsBtn.addEventListener('click', showThumbnails);

    // modalClose.addEventListener('click', () => modal.style.display = 'none');
    // window.addEventListener('click', (e) => {
    //     if (e.target == modal) modal.style.display = 'none';
    // });


    // --- Core Functions ---
    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) {
            alert('请输入搜索内容！');
            return;
        }

        setLoadingState(true, '正在搜索...');
        try {
            const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            searchResults = data;
            renderResults(data);
        } catch (error) {
            console.error('Search failed:', error);
            alert('搜索失败，请检查网络或后台服务。');
        } finally {
            setLoadingState(false);
        }
    }

    function renderResults(results) {
        resultsTableBody.innerHTML = '';
        if (!results || results.length === 0) {
            resultsTableBody.innerHTML = '<tr><td colspan="5">没有找到结果。</td></tr>';
            return;
        }

        results.forEach((item, index) => {
            const row = document.createElement('tr');
            row.dataset.index = index;
            // Store full data on the element
            row.dataset.fullItem = JSON.stringify(item);
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${item.ztitle}</td>
                <td>${item.rtitle}</td>
                <td>${item.count}</td>
                <td>${item.author}</td>
            `;
            resultsTableBody.appendChild(row);
        });
        // Select and preview the first item by default
        if (results.length > 0) {
            resultsTableBody.querySelector('tr').classList.add('selected');
            updatePreview(0);
        }
    }

    function updatePreview(index) {
        const item = searchResults[index];
        if (!item) return;

        previewImage.src = item.img || '';
        previewImage.alt = item.ztitle;

        // --- THIS IS THE MODIFIED PART ---
        // Construct the URL for our internal viewer
        const viewerUrl = `/view?url=${encodeURIComponent(item.ztitle_href)}&count=${item.count}&title=${encodeURIComponent(item.ztitle)}`;
        onlineLink.href = viewerUrl;
        onlineLink.textContent = '在线全屏看图'; // Update text to be more descriptive
        // --- END OF MODIFICATION ---
    }


    function getSelectedAlbum() {
        const selectedRow = resultsTableBody.querySelector('tr.selected');
        if (!selectedRow) return null;
        return JSON.parse(selectedRow.dataset.fullItem);
    }

    function downloadSelected() {
        const selectedAlbum = getSelectedAlbum();
        if (!selectedAlbum) {
            alert('请先选择一个图集！');
            return;
        }
        startDownload([selectedAlbum]);
    }

    function downloadAll() {
        if (searchResults.length === 0) {
            alert('没有可下载的内容！');
            return;
        }
        startDownload(searchResults);
    }

    async function startDownload(albums) {
        try {
            const response = await fetch('/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ albums: albums })
            });
            const result = await response.json();
            if (result.status === 'success') {
                monitorProgress();
            } else {
                alert(`启动下载失败: ${result.message}`);
            }
        } catch (error) {
            console.error('Download start failed:', error);
            alert('启动下载时发生错误。');
        }
    }

    async function cancelDownload() {
        try {
            await fetch('/cancel', { method: 'POST' });
            alert('已发送取消请求。');
        } catch (error) {
            console.error('Cancel failed:', error);
        }
    }

    function monitorProgress() {
        if (statusInterval) clearInterval(statusInterval);

        setDownloadingUI(true);
        statusInterval = setInterval(async () => {
            try {
                const response = await fetch('/status');
                const status = await response.json();

                updateProgressBar(status);

                if (!status.is_downloading) {
                    clearInterval(statusInterval);
                    statusInterval = null;
                    setDownloadingUI(false);
                }
            } catch (error) {
                console.error('Failed to get status:', error);
                clearInterval(statusInterval);
                statusInterval = null;
                setDownloadingUI(false);
            }
        }, 1000);
    }

    function updateProgressBar(status) {
        albumLabel.textContent = `状态: ${status.current_album}`;
        const progress = status.progress || 0;
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${progress}% (${status.current || 0}/${status.total || 0})`;
    }

    function setDownloadingUI(isDownloading) {
        searchBtn.disabled = isDownloading;
        downloadSelectedBtn.disabled = isDownloading;
        downloadAllBtn.disabled = isDownloading;
        cancelBtn.disabled = !isDownloading;
    }

    function setLoadingState(isLoading, message = '') {
        searchBtn.disabled = isLoading;
        if (isLoading) {
            searchBtn.textContent = '搜索中...';
            resultsTableBody.innerHTML = `<tr><td colspan="5">${message}</td></tr>`;
        } else {
            searchBtn.textContent = '搜索';
        }
    }

    // --- THIS IS THE REWRITTEN FUNCTION ---
    async function showThumbnails() {
        const selectedAlbum = getSelectedAlbum();
        if (!selectedAlbum) {
            alert('请先选择一个图集！');
            return;
        }

        // 1. Prepare and show the modal with a loading state
        modalTitle.textContent = `加载中... (${selectedAlbum.ztitle})`;
        thumbnailGrid.innerHTML = '<p style="color: #ecf0f1;">正在获取图片列表，请稍候...</p>';
        modal.style.display = 'block';

        // 2. Cleanup previous lightGallery instance if it exists
        if (lightGalleryInstance) {
            lightGalleryInstance.destroy();
            lightGalleryInstance = null;
        }

        try {
            // 3. Fetch image URLs
            const response = await fetch(`/get_thumbnails?url=${encodeURIComponent(selectedAlbum.ztitle_href)}&count=${selectedAlbum.count}`);
            const urls = await response.json();

            if (!urls || urls.length === 0) {
                thumbnailGrid.innerHTML = '<p style="color: #e74c3c;">无法加载缩略图。</p>';
                return;
            }

            // 4. Populate the grid with thumbnails
            thumbnailGrid.innerHTML = ''; // Clear loading message
            modalTitle.textContent = `${selectedAlbum.ztitle} (${urls.length} 张)`;

            urls.forEach((url) => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'grid-item';

                // lightGallery requires an 'a' tag wrapping the 'img'
                const link = document.createElement('a');
                link.href = url; // Link to the full-size image

                const img = document.createElement('img');
                img.src = url; // Use the same URL for thumb, or a dedicated thumb URL if available
                img.loading = 'lazy'; // Lazy load for performance

                link.appendChild(img);
                itemDiv.appendChild(link);
                thumbnailGrid.appendChild(itemDiv);
            });

            // 5. Initialize lightGallery on the grid container
            lightGalleryInstance = lightGallery(thumbnailGrid, {
                selector: '.grid-item a', // Tell lightGallery which items are part of the gallery
                plugins: [lgZoom, lgThumbnail], // Enable plugins
                licenseKey: 'your_license_key', // Optional: if you have a commercial license
                speed: 500,
                // Zoom options
                scale: 1,
                enableZoomAfter: 300,
                actualSize: false, // Set to true to zoom to 100% on double click
            });

        } catch (error) {
            console.error('Failed to fetch thumbnails:', error);
            thumbnailGrid.innerHTML = '<p style="color: #e74c3c;">加载缩略图失败，请检查网络连接。</p>';
        }
    }
    // 初始检查下载状态，以防刷新页面时仍在下载
    monitorProgress();
});
