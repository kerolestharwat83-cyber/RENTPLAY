/**
 * RENTPLAY Django - Main JavaScript
 * Multi-Vendor Real Estate Marketplace
 * Includes: Mobile menu, Toasts, Filters toggle, Dashboard sidebar
 */

// ==================== MOBILE MENU ====================
function toggleMobile() {
    var nav = document.getElementById('navLinks');
    if (nav) nav.classList.toggle('open');
}
document.querySelectorAll('.nav-links a').forEach(function(link) {
    link.addEventListener('click', function() {
        var nav = document.getElementById('navLinks');
        if (nav && window.innerWidth < 768) nav.classList.remove('open');
    });
});

// ==================== FILTERS TOGGLE ====================
function toggleFilters() {
    var card = document.getElementById('filtersCard');
    var chevron = document.getElementById('filtersChevron');
    if (!card || !chevron) return;
    if (card.style.display === 'none') {
        card.style.display = 'block';
        chevron.classList.remove('fa-chevron-down');
        chevron.classList.add('fa-chevron-up');
    } else {
        card.style.display = 'none';
        chevron.classList.remove('fa-chevron-up');
        chevron.classList.add('fa-chevron-down');
    }
}

// ==================== TOAST NOTIFICATIONS ====================
function showToast(message, type) {
    var container = document.getElementById('jsToastContainer');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        container.id = 'jsToastContainer';
        document.body.appendChild(container);
    }
    var iconClass = type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-times-circle' : 'fa-info-circle';
    var toast = document.createElement('div');
    toast.className = 'toast ' + (type || 'info');
    toast.innerHTML = '<i class="fas ' + iconClass + '"></i> ' + message;
    container.appendChild(toast);
    setTimeout(function() {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(-100%)';
        toast.style.transition = 'all 0.4s';
        setTimeout(function() { toast.remove(); }, 400);
    }, 4000);
}

// Auto-hide Django toasts
document.querySelectorAll('.toast[data-autohide]').forEach(function(toast) {
    setTimeout(function() {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(-100%)';
        toast.style.transition = 'all 0.4s';
        setTimeout(function() { toast.remove(); }, 400);
    }, 4000);
});

// ==================== DASHBOARD SIDEBAR ====================
function toggleDashboardSidebar() {
    var sidebar = document.getElementById('dashboardSidebar');
    if (sidebar) sidebar.classList.toggle('open');
}

// ==================== GALLERY NAVIGATION ====================
function openGallery(propertyId) {
    window.location.href = '/property/' + propertyId + '/';
}

// =================--- PASSWORD TOGGLE ---====================
function togglePassword(btn) {
    var input = btn.parentElement.querySelector('input');
    var icon = btn.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

// =================--- PHONE INPUT FILTER ---====================
document.querySelectorAll('input[type="tel"]').forEach(function(input) {
    input.addEventListener('input', function() {
        this.value = this.value.replace(/[^0-9]/g, '');
    });
});

// =================--- LAZY LOADING ---====================
if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                var img = entry.target;
                if (img.dataset.src) { img.src = img.dataset.src; img.removeAttribute('data-src'); }
                observer.unobserve(img);
            }
        });
    });
    document.querySelectorAll('img[data-src]').forEach(function(img) { observer.observe(img); });
}

// ==================== DYNAMIC DISTRICT LOADER ====================
(function() {
    // For filter form
    var citySelect = document.getElementById('id_city');
    var districtSelect = document.getElementById('id_district');

    if (citySelect && districtSelect) {
        citySelect.addEventListener('change', function() {
            var cityId = this.value;
            districtSelect.innerHTML = '<option value="">---------</option>';
            districtSelect.disabled = true;

            if (cityId) {
                fetch('/ajax/districts/?city_id=' + encodeURIComponent(cityId))
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        districtSelect.disabled = false;
                        if (data.success && data.districts) {
                            data.districts.forEach(function(d) {
                                var opt = document.createElement('option');
                                opt.value = d.id;
                                opt.textContent = d.name;
                                districtSelect.appendChild(opt);
                            });
                        }
                    })
                    .catch(function() {
                        districtSelect.disabled = false;
                    });
            }
        });
    }

    // For property form
    var propCity = document.getElementById('prop_city');
    var propDistrict = document.getElementById('prop_district');

    if (propCity && propDistrict) {
        propCity.addEventListener('change', function() {
            var cityId = this.value;
            propDistrict.innerHTML = '<option value="">---------</option>';
            propDistrict.disabled = true;

            if (cityId) {
                fetch('/ajax/districts/?city_id=' + encodeURIComponent(cityId))
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        propDistrict.disabled = false;
                        if (data.success && data.districts) {
                            data.districts.forEach(function(d) {
                                var opt = document.createElement('option');
                                opt.value = d.id;
                                opt.textContent = d.name;
                                propDistrict.appendChild(opt);
                            });
                        }
                    })
                    .catch(function() {
                        propDistrict.disabled = false;
                    });
            }
        });
    }
})();

// ==================== BOOKING DURATION CALCULATOR ====================
(function() {
    var checkinInput = document.getElementById('checkin_date');
    var checkoutInput = document.getElementById('checkout_date');
    var monthsInput = document.getElementById('number_of_months');
    var durationDisplay = document.getElementById('durationDisplay');
    var yearsField = document.getElementById('duration_years');
    var monthsField = document.getElementById('duration_months_display');
    var daysField = document.getElementById('duration_days');

    function calculateDuration() {
        if (!checkinInput || !checkoutInput) return;

        var start = new Date(checkinInput.value);
        var end = new Date(checkoutInput.value);

        if (start && end && end > start) {
            var diffTime = Math.abs(end - start);
            var diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

            var years = Math.floor(diffDays / 365);
            var remaining = diffDays % 365;
            var months = Math.floor(remaining / 30);
            var days = remaining % 30;

            if (yearsField) yearsField.value = years;
            if (monthsField) monthsField.value = months;
            if (daysField) daysField.value = days;

            if (durationDisplay) durationDisplay.style.display = 'block';
        }
    }

    if (checkinInput) checkinInput.addEventListener('change', calculateDuration);
    if (checkoutInput) checkoutInput.addEventListener('change', calculateDuration);

    // Auto-calculate end date from months input
    if (monthsInput && checkinInput && checkoutInput) {
        monthsInput.addEventListener('input', function() {
            var months = parseInt(this.value) || 0;
            if (months > 0 && checkinInput.value) {
                var start = new Date(checkinInput.value);
                var end = new Date(start.getFullYear(), start.getMonth() + months, start.getDate());
                checkoutInput.value = end.toISOString().split('T')[0];
                calculateDuration();
            }
        });
    }
})();

// ==================== MOBILE OVERLAY ====================
function closeAllMenus() {
    var nav = document.getElementById('navLinks');
    var overlay = document.getElementById('mobileOverlay');
    var sidebar = document.getElementById('dashboardSidebar');

    if (nav) nav.classList.remove('open');
    if (overlay) overlay.classList.remove('active');
    if (sidebar) sidebar.classList.remove('open');
}

// Close menus on escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeAllMenus();
    }
});

// ==================== SMOOTH SCROLL ====================
document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
    anchor.addEventListener('click', function(e) {
        var target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// ==================== FORM VALIDATION ====================
document.querySelectorAll('form').forEach(function(form) {
    form.addEventListener('submit', function(e) {
        var requiredFields = form.querySelectorAll('[required]');
        var isValid = true;

        requiredFields.forEach(function(field) {
            if (!field.value.trim()) {
                isValid = false;
                field.style.borderColor = 'var(--danger)';
                field.addEventListener('input', function() {
                    this.style.borderColor = '';
                }, { once: true });
            }
        });

        if (!isValid) {
            e.preventDefault();
            showToast('Please fill in all required fields.', 'error');
        }
    });
});

// ==================== BACK TO TOP ====================
(function() {
    var btn = document.createElement('button');
    btn.id = 'backToTop';
    btn.innerHTML = '<i class="fas fa-chevron-up"></i>';
    btn.style.cssText = 'position:fixed;bottom:2rem;right:2rem;z-index:2000;width:44px;height:44px;border-radius:50%;border:none;background:linear-gradient(135deg,var(--primary) 0%,#7c3aed 100%);color:white;font-size:1rem;cursor:pointer;box-shadow:0 4px 14px rgba(79,70,229,0.35);opacity:0;transform:translateY(20px);transition:all 0.3s;pointer-events:none;';
    document.body.appendChild(btn);

    window.addEventListener('scroll', function() {
        if (window.scrollY > 500) {
            btn.style.opacity = '1';
            btn.style.transform = 'translateY(0)';
            btn.style.pointerEvents = 'auto';
        } else {
            btn.style.opacity = '0';
            btn.style.transform = 'translateY(20px)';
            btn.style.pointerEvents = 'none';
        }
    });

    btn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
})();

// ==================== NAVBAR SCROLL EFFECT ====================
(function() {
    var navbar = document.getElementById('navbar');
    if (!navbar) return;

    var lastScroll = 0;
    window.addEventListener('scroll', function() {
        var currentScroll = window.scrollY;

        if (currentScroll > 100) {
            navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,0.1)';
        } else {
            navbar.style.boxShadow = '';
        }

        lastScroll = currentScroll;
    });
})();

// ==================== AJAX FORM HANDLERS ====================
function submitAjaxForm(form, successCallback, errorCallback) {
    var fd = new FormData(form);
    var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');

    fetch(form.action, {
        method: 'POST',
        body: fd,
        headers: {
            'X-CSRFToken': csrfToken ? csrfToken.value : '',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.success && successCallback) successCallback(data);
        else if (!data.success && errorCallback) errorCallback(data);
    })
    .catch(function(err) {
        if (errorCallback) errorCallback({ error: err });
    });
}

// ==================== LAZY LOADING ====================
(function() {
    if ('IntersectionObserver' in window) {
        var imageObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    var img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        img.classList.add('loaded');
                    }
                    imageObserver.unobserve(img);
                }
            });
        }, { rootMargin: '50px' });

        document.querySelectorAll('img[data-src]').forEach(function(img) {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for older browsers
        document.querySelectorAll('img[data-src]').forEach(function(img) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
})();

// ==================== VIDEO UPLOAD PREVIEW ====================
(function() {
    var videoInput = document.querySelector('input[name="videos"]');
    if (videoInput) {
        videoInput.addEventListener('change', function() {
            var files = this.files;
            var previewContainer = document.getElementById('videoPreview');

            if (previewContainer) {
                previewContainer.innerHTML = '';

                for (var i = 0; i < Math.min(files.length, 5); i++) {
                    var file = files[i];
                    if (file.type.startsWith('video/')) {
                        var video = document.createElement('video');
                        video.src = URL.createObjectURL(file);
                        video.style.cssText = 'width:120px;height:80px;object-fit:cover;border-radius:8px;';
                        video.controls = true;
                        previewContainer.appendChild(video);
                    }
                }
            }
        });
    }
})();
