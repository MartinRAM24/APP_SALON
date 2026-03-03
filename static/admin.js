const token = localStorage.getItem('token');
if (!token) window.location.href = '/';

const headers = { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` };

async function loadAdminAppointments() {
  const res = await fetch('/api/admin/citas', { headers });
  const data = await res.json();
  if (!res.ok) {
    document.getElementById('adminMsg').textContent = data.detail || 'Sin permisos';
    return;
  }
  const tbody = document.getElementById('adminAppointments');
  tbody.innerHTML = data.map(c => `<tr class="border-b">
    <td>${c.id}</td><td>${c.usuario_nombre}</td><td>${c.servicio_nombre}</td><td>${c.fecha}</td><td>${c.hora.slice(0,5)}</td><td>${c.estado}</td>
    <td class="space-x-2"><button onclick="cancelAppointment(${c.id})" class="bg-rose-500 text-white px-2 py-1 rounded">Cancelar</button></td>
  </tr>`).join('');
}

async function loadAdminSummary() {
  const res = await fetch('/api/admin/resumen', { headers });
  if (!res.ok) return;
  const summary = await res.json();
  const next = document.getElementById('adminNext');
  next.textContent = summary.proxima_cita
    ? `${summary.proxima_cita.cliente} · ${summary.proxima_cita.servicio} · ${summary.proxima_cita.fecha} ${summary.proxima_cita.hora}`
    : 'No hay citas próximas.';
  document.getElementById('adminTodayCount').textContent = summary.citas_hoy;
}

window.cancelAppointment = async (id) => {
  await fetch(`/api/admin/citas/${id}`, { method: 'DELETE', headers });
  loadAdminAppointments();
  loadAdminSummary();
};

document.getElementById('manualForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    usuario_id: document.getElementById('usuarioId').value,
    servicio_id: Number(document.getElementById('servicioId').value),
    fecha: document.getElementById('manualFecha').value,
    hora: document.getElementById('manualHora').value,
  };
  const res = await fetch('/api/admin/citas', { method: 'POST', headers, body: JSON.stringify(payload) });
  const data = await res.json();
  document.getElementById('adminMsg').textContent = res.ok ? 'Cita creada' : (data.detail || 'Error');
  loadAdminAppointments();
  loadAdminSummary();
});

document.getElementById('serviceForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    nombre: document.getElementById('nombreServicio').value,
    duracion_minutos: Number(document.getElementById('duracionServicio').value),
    precio: Number(document.getElementById('precioServicio').value),
  };
  const res = await fetch('/api/admin/servicios', { method: 'POST', headers, body: JSON.stringify(payload) });
  const data = await res.json();
  document.getElementById('adminMsg').textContent = res.ok ? `Servicio creado (ID ${data.id})` : (data.detail || 'Error');
});

document.getElementById('editServiceForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = document.getElementById('editServiceId').value;
  const payload = {};
  if (document.getElementById('editNombre').value) payload.nombre = document.getElementById('editNombre').value;
  if (document.getElementById('editDuracion').value) payload.duracion_minutos = Number(document.getElementById('editDuracion').value);
  if (document.getElementById('editPrecio').value) payload.precio = Number(document.getElementById('editPrecio').value);

  const res = await fetch(`/api/admin/servicios/${id}`, { method: 'PATCH', headers, body: JSON.stringify(payload) });
  const data = await res.json();
  document.getElementById('adminMsg').textContent = res.ok ? `Servicio ${data.nombre} actualizado` : (data.detail || 'Error');
});

document.getElementById('logoutAdmin')?.addEventListener('click', () => {
  localStorage.removeItem('token');
  localStorage.removeItem('rol');
  window.location.href = '/';
});

loadAdminAppointments();
loadAdminSummary();
