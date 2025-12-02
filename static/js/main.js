// Simple JS for dark mode + small UX

document.addEventListener("DOMContentLoaded", function(){
  const btn = document.getElementById('darkToggle');
  // restore
  if (localStorage.getItem('thendral-dark') === '1'){
    document.body.classList.add('dark');
    if (btn) btn.textContent = 'Light';
  }

  if (btn){
    btn.addEventListener('click', function(){
      document.body.classList.toggle('dark');
      const isDark = document.body.classList.contains('dark');
      localStorage.setItem('thendral-dark', isDark ? '1' : '0');
      btn.textContent = isDark ? 'Light' : 'Dark';
    });
  }
});
