// ==================== CARD VIDEO PLAY/PAUSE ====================
function toggleCardVideo(videoEl) {
    if (!videoEl) return;
    var playIcon = videoEl.parentElement.querySelector('.card-video-play');
    if (videoEl.paused) {
        document.querySelectorAll('.property-video-card').forEach(function(v) {
            if (v !== videoEl) { v.pause(); v.classList.remove('playing'); }
        });
        videoEl.play().catch(function(){});
        videoEl.classList.add('playing');
        if (playIcon) playIcon.style.opacity = '0';
    } else {
        videoEl.pause();
        videoEl.classList.remove('playing');
        if (playIcon) playIcon.style.opacity = '1';
    }
}

// Auto-pause card videos when scrolling out of view
(function() {
    var cardVideos = document.querySelectorAll('.property-video-card');
    if (!cardVideos.length) return;
    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            var video = entry.target;
            if (!entry.isIntersecting && !video.paused) {
                video.pause();
                video.classList.remove('playing');
                var icon = video.parentElement.querySelector('.card-video-play');
                if (icon) icon.style.opacity = '1';
            }
        });
    }, { threshold: 0.5 });
    cardVideos.forEach(function(v) { observer.observe(v); });
})();

// ==================== COPY PROPERTY LINK ====================
window.copyPropertyLink = function(url) {
    var fullUrl = window.location.origin + url;
    navigator.clipboard.writeText(fullUrl).then(function() {
        showToast('\u062a\u0645 \u0646\u0633\u062e \u0631\u0627\u0628\u0637 \u0627\u0644\u0648\u062d\u062f\u0629!');
    }).catch(function() {
        showToast('\u062d\u062f\u062b \u062e\u0637\u0623 \u0623\u062b\u0646\u0627\u0621 \u0627\u0644\u0646\u0633\u062e');
    });
};

function showToast(msg) {
    var existing = document.querySelector('.property-toast');
    if (existing) existing.remove();
    var toast = document.createElement('div');
    toast.className = 'property-toast';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(function() { toast.classList.add('show'); }, 10);
    setTimeout(function() { toast.classList.remove('show'); setTimeout(function() { toast.remove(); }, 300); }, 2000);
}

// ==================== DARK MODE ====================
(function() {
    var toggle = document.getElementById('darkModeToggle');
    if (!toggle) return;
    var saved = localStorage.getItem('rentplay_dark');
    if (saved === 'true') {
        document.documentElement.classList.add('dark-mode');
        toggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
    toggle.addEventListener('click', function() {
        var isDark = document.documentElement.classList.toggle('dark-mode');
        localStorage.setItem('rentplay_dark', isDark);
        toggle.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });
})();
