const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

async function api(url, method='GET', body=null) {
  const opts = {method, headers:{'Content-Type':'application/json','Accept':'application/json'}};
  if (csrfToken) opts.headers['X-CSRFToken'] = csrfToken;
  if (body !== null) opts.body = JSON.stringify(body);
  try {
    const res = await fetch(url, opts);
    const data = await res.json().catch(()=>({success:false,error:'Invalid server response.'}));
    if (!res.ok || data.success === false) { toast(data.error || 'Something went wrong.', 'danger'); return {...data, success:false}; }
    return data;
  } catch (e) { toast('Network error. Please try again.', 'danger'); return {success:false,error:e.message}; }
}

function toast(message, type='success') {
  const box = document.getElementById('toastContainer'); if (!box) return;
  const el = document.createElement('div'); el.className = `toast align-items-center text-bg-${type} border-0`; el.setAttribute('role','alert');
  el.innerHTML = `<div class="d-flex"><div class="toast-body">${escapeHtml(message)}</div><button class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button></div>`;
  box.appendChild(el); const t = new bootstrap.Toast(el,{delay:3200}); t.show(); el.addEventListener('hidden.bs.toast',()=>el.remove());
}
function escapeHtml(s='') { return String(s).replace(/[&<>'"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }
function levelName(n) { return ({1:'Beginner',2:'Intermediate',3:'Advanced'})[n] || 'Not Set'; }

(async function initNav(){
  const saved = localStorage.getItem('theme') || 'light'; document.documentElement.setAttribute('data-bs-theme',saved);
  document.getElementById('themeToggle')?.addEventListener('click',()=>{const next=document.documentElement.getAttribute('data-bs-theme')==='dark'?'light':'dark';document.documentElement.setAttribute('data-bs-theme',next);localStorage.setItem('theme',next);});
  const me = await api('/api/auth/me');
  document.querySelectorAll('.guest-only').forEach(x=>x.classList.toggle('d-none', !!me.authenticated));
  document.querySelectorAll('.auth-only').forEach(x=>x.classList.toggle('d-none', !me.authenticated));
  document.querySelectorAll('.admin-only').forEach(x=>x.classList.toggle('d-none', !(me.authenticated && me.user.role==='admin')));
  document.getElementById('logoutBtn')?.addEventListener('click',async()=>{await api('/api/auth/logout','POST',{});location.href='/';});
})();
