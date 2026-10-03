/**
 * ANUMATISETU — Client-side Interactions
 * Sidebar toggle, Dynamic modals, Lucide Icons, Assistant Chat
 */

document.addEventListener('DOMContentLoaded', function () {
  // Initialize Lucide icons
  if (window.lucide) {
    window.lucide.createIcons();
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
