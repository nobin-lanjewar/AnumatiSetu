/**
 * ANUMATISETU — Client-side Interactions
 * Sidebar toggle, Dynamic modals, Lucide Icons, Assistant Chat, Bilingual Engine (EN / MR)
 */

document.addEventListener('DOMContentLoaded', function () {
  // Initialize Lucide icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Load saved language preference
  const savedLang = localStorage.getItem('anumati_lang') || 'en';
  if (savedLang === 'mr') {
    setLanguage('mr');
  }

  // Sidebar Desktop Collapse Toggle
  const sidebarCollapseBtn = document.getElementById('sidebar-collapse-btn');
  if (sidebarCollapseBtn) {
    sidebarCollapseBtn.addEventListener('click', function () {
      document.body.classList.toggle('sidebar-collapsed');
      const isCollapsed = document.body.classList.contains('sidebar-collapsed');
      localStorage.setItem('sidebar_collapsed', isCollapsed ? '1' : '0');
    });

    if (localStorage.getItem('sidebar_collapsed') === '1') {
      document.body.classList.add('sidebar-collapsed');
    }
  }

  // Mobile Sidebar Drawer Toggle
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const sidebarEl = document.querySelector('.dashboard-sidebar');
  const mobileOverlay = document.getElementById('mobile-sidebar-overlay');

  if (mobileMenuBtn && sidebarEl) {
    mobileMenuBtn.addEventListener('click', function () {
      sidebarEl.classList.toggle('mobile-open');
      if (mobileOverlay) {
        mobileOverlay.classList.toggle('hidden');
      }
    });

    if (mobileOverlay) {
      mobileOverlay.addEventListener('click', function () {
        sidebarEl.classList.remove('mobile-open');
        mobileOverlay.classList.add('hidden');
      });
    }
  }

  // Notifications Dropdown Toggle
  const notifBtn = document.getElementById('notif-menu-btn');
  const notifDropdown = document.getElementById('notif-dropdown');
  if (notifBtn && notifDropdown) {
    notifBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      notifDropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', function (e) {
      if (!notifDropdown.contains(e.target) && !notifBtn.contains(e.target)) {
        notifDropdown.classList.add('hidden');
      }
    });
  }

  // Toast Auto-Dismiss
  const toasts = document.querySelectorAll('.anumati-toast');
  toasts.forEach(toast => {
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-10px)';
      toast.style.transition = 'all 0.4s ease';
      setTimeout(() => toast.remove(), 400);
    }, 4500);
  });
});

// Helper for modal management
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.style.overflow = 'hidden';
    if (window.lucide) window.lucide.createIcons();
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    document.body.style.overflow = '';
  }
}

// Client-side Bilingual Translation Engine (English <-> Marathi)
function setLanguage(lang) {
  localStorage.setItem('anumati_lang', lang);

  const enBtn = document.getElementById('lang-btn-en');
  const mrBtn = document.getElementById('lang-btn-mr');

  if (lang === 'mr') {
    if (enBtn && mrBtn) {
      enBtn.className = 'px-2 py-0.5 rounded text-slate-300 hover:text-white transition-all';
      mrBtn.className = 'px-2 py-0.5 rounded bg-cyan-500 text-slate-900 font-bold transition-all';
    }
    document.querySelectorAll('[data-i18n-mr]').forEach(el => {
      el.innerHTML = el.getAttribute('data-i18n-mr');
    });
  } else {
    if (enBtn && mrBtn) {
      enBtn.className = 'px-2 py-0.5 rounded bg-cyan-500 text-slate-900 font-bold transition-all';
      mrBtn.className = 'px-2 py-0.5 rounded text-slate-300 hover:text-white transition-all';
    }
    document.querySelectorAll('[data-i18n-en]').forEach(el => {
      el.innerHTML = el.getAttribute('data-i18n-en');
    });
  }

  // Re-render any icons inside translated elements
  if (window.lucide) {
    window.lucide.createIcons();
  }
}
