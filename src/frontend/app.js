const api = {
  animals: () => fetch('/api/animals').then(handleResponse),
  stats: () => fetch('/api/stats').then(handleResponse),
  createAnimal: (payload) => fetch('/api/animals', {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)
  }).then(handleResponse),
  createService: (payload) => fetch('/api/services', {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)
  }).then(handleResponse),
  history: (animalId) => fetch(`/api/animals/${animalId}/history`).then(handleResponse)
};

let animals = [];

function handleResponse(response) {
  return response.json().then(data => {
    if (!response.ok) throw new Error(data.error || 'Não foi possível concluir a operação.');
    return data;
  });
}

function escapeHtml(value = '') {
  return String(value).replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
}

function money(value) {
  return Number(value || 0).toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'});
}

function formatDate(value) {
  if (!value) return 'Não informada';
  const [year, month, day] = value.split('-');
  return `${day}/${month}/${year}`;
}

function showToast(message, error = false) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = `toast show${error ? ' error' : ''}`;
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.className = 'toast', 3000);
}

function navigate(sectionId) {
  document.querySelectorAll('.section').forEach(section => section.classList.toggle('active', section.id === sectionId));
  document.querySelectorAll('.nav-item').forEach(button => button.classList.toggle('active', button.dataset.section === sectionId));
  const titles = {dashboard: 'Visão geral', animals: 'Cadastro de animais', services: 'Registro de serviços', history: 'Histórico clínico'};
  document.getElementById('page-title').textContent = titles[sectionId] || 'VetVida';
}

async function refreshAll() {
  try {
    const [animalData, stats] = await Promise.all([api.animals(), api.stats()]);
    animals = animalData;
    renderAnimals();
    populateAnimalSelects();
    document.getElementById('stat-animals').textContent = stats.animals;
    document.getElementById('stat-services').textContent = stats.services;
    document.getElementById('stat-today').textContent = stats.today_services;
    document.getElementById('stat-revenue').textContent = money(stats.revenue);
  } catch (error) {
    showToast(error.message, true);
  }
}

function renderAnimals() {
  const container = document.getElementById('animals-list');
  document.getElementById('animal-count').textContent = animals.length;
  if (!animals.length) {
    container.innerHTML = '<div class="empty-state"><div class="empty-icon">🐾</div><h4>Nenhum animal cadastrado</h4><p>Use o formulário ao lado para começar.</p></div>';
    return;
  }
  container.innerHTML = animals.map(animal => `
    <div class="animal-card">
      <div class="animal-avatar">${animal.species === 'Gato' ? '🐱' : animal.species === 'Cachorro' ? '🐶' : '🐾'}</div>
      <div class="animal-info">
        <strong>${escapeHtml(animal.name)}</strong>
        <span>${escapeHtml(animal.species)}${animal.breed ? ' • ' + escapeHtml(animal.breed) : ''}</span>
      </div>
      <div class="animal-owner">Tutor<br><strong>${escapeHtml(animal.owner_name)}</strong></div>
    </div>
  `).join('');
}

function populateAnimalSelects() {
  const options = '<option value="">Selecione um animal</option>' + animals.map(a =>
    `<option value="${a.id}">${escapeHtml(a.name)} - ${escapeHtml(a.owner_name)}</option>`
  ).join('');
  document.getElementById('service-animal').innerHTML = options;
  document.getElementById('history-animal').innerHTML = options;
}

async function submitAnimal(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = Object.fromEntries(new FormData(form).entries());
  try {
    const result = await api.createAnimal(payload);
    form.reset();
    showToast(result.message);
    await refreshAll();
  } catch (error) {
    showToast(error.message, true);
  }
}

async function submitService(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = Object.fromEntries(new FormData(form).entries());
  try {
    const result = await api.createService(payload);
    form.reset();
    document.getElementById('service-date').value = new Date().toISOString().slice(0, 10);
    showToast(result.message);
    await refreshAll();
  } catch (error) {
    showToast(error.message, true);
  }
}

async function loadHistory() {
  const id = document.getElementById('history-animal').value;
  if (!id) return showToast('Selecione um animal para consultar.', true);
  const target = document.getElementById('history-content');
  try {
    const data = await api.history(id);
    const a = data.animal;
    target.className = '';
    target.innerHTML = `
      <div class="patient-summary">
        <div><h4>${escapeHtml(a.name)}</h4><p>${escapeHtml(a.species)}${a.breed ? ' • ' + escapeHtml(a.breed) : ''}</p></div>
        <div><p>Tutor</p><strong>${escapeHtml(a.owner_name)}</strong></div>
        <div><p>Nascimento</p><strong>${formatDate(a.birth_date)}</strong></div>
      </div>
      ${data.services.length ? `
        <table class="history-table">
          <thead><tr><th>Data</th><th>Serviço</th><th>Descrição</th><th>Veterinário(a)</th><th>Valor</th></tr></thead>
          <tbody>${data.services.map(s => `
            <tr>
              <td>${formatDate(s.service_date)}</td>
              <td><span class="service-badge">${escapeHtml(s.service_type)}</span></td>
              <td>${escapeHtml(s.description || '-')}</td>
              <td>${escapeHtml(s.veterinarian || '-')}</td>
              <td>${money(s.price)}</td>
            </tr>`).join('')}</tbody>
        </table>` : '<div class="empty-state"><div class="empty-icon">🩺</div><h4>Sem serviços registrados</h4><p>Este animal ainda não possui histórico de atendimento.</p></div>'}
    `;
  } catch (error) {
    showToast(error.message, true);
  }
}

document.querySelectorAll('.nav-item').forEach(button => button.addEventListener('click', () => navigate(button.dataset.section)));
document.querySelectorAll('[data-go]').forEach(button => button.addEventListener('click', () => navigate(button.dataset.go)));
document.getElementById('animal-form').addEventListener('submit', submitAnimal);
document.getElementById('service-form').addEventListener('submit', submitService);
document.getElementById('history-search').addEventListener('click', loadHistory);
document.getElementById('history-animal').addEventListener('change', () => {
  if (document.getElementById('history-animal').value) loadHistory();
});
document.getElementById('service-date').value = new Date().toISOString().slice(0, 10);
refreshAll();
