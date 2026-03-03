const msg = document.getElementById('message');

const registerForm = document.getElementById('registerForm');
registerForm?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(registerForm);
  const payload = Object.fromEntries(fd.entries());
  const res = await fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  msg.textContent = res.ok ? 'Registro exitoso. Ahora inicia sesión.' : (data.detail || 'Error al registrar');
});

const loginForm = document.getElementById('loginForm');
loginForm?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(loginForm);
  const payload = Object.fromEntries(fd.entries());
  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) {
    msg.textContent = data.detail || 'Credenciales inválidas';
    return;
  }
  localStorage.setItem('token', data.access_token);
  localStorage.setItem('rol', data.rol);
  msg.textContent = data.rol === 'admin' ? 'Login admin correcto. Redirigiendo al panel...' : 'Login correcto.';
  window.location.href = data.rol === 'admin' ? '/admin' : '/cliente';
});
