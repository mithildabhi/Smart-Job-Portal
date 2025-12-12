// static/js/student_profile.js

// sanitize token helper (global)
function sanitizeToken(token) {
  if (!token) return null;
  token = token.toString().trim();
  // strip surrounding quotes (sometimes happens)
  token = token.replace(/^"(.*)"$/, '$1').replace(/^'(.*)'$/, '$1');
  return token || null;
}

// Simplified Skills UI (name-only), plus existing Education code preserved below
// ---------- Robust CSRF helper (replace older getCookie uses) ----------
function getCSRFToken() {
  // try cookie (safe)
  function cookieGet(name) {
    try {
      const v = `; ${document.cookie || ''}`;
      const parts = v.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    } catch (e) { /* ignore */ }
    return null;
  }

  // 1) prefer cookie
  let token = cookieGet('csrftoken') || cookieGet('csrf_token') || null;
  if (token) return token;

  // 2) fallback: input hidden in form (csrfmiddlewaretoken)
  const el = document.querySelector('input[name="csrfmiddlewaretoken"]');
  if (el && el.value) return el.value;

  // 3) fallback: meta tag <meta name="csrf-token" content="...">
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta && meta.content) return meta.content;

  // 4) no token found
  return null;
}

(function () {
  // ---------- CSRF ----------
  function getCookie(name) {
    const v = `; ${document.cookie}`;
    const parts = v.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }
  const csrftoken = sanitizeToken(getCSRFToken());

  // ---------- Skills (name-only) ----------
  function renderSkills(skills) {
    const skillsList = document.getElementById('skills-list');
    const chips = document.getElementById('skill-chips');
    if (!skillsList || !chips) return;

    // rebuild skill rows
    skillsList.innerHTML = '';
    skills.forEach((s, i) => {
      const div = document.createElement('div');
      div.className = 'skill-row d-flex justify-content-between align-items-center mb-2';
      div.dataset.skillIndex = i;
      div.dataset.skillName = s.name;
      div.innerHTML = `
        <div>
          <div class="skill-name-display">${s.name}</div>
        </div>
        <div class="text-end">
          <button class="btn btn-sm btn-outline-secondary skill-edit-btn"><i class="fas fa-edit"></i></button>
          <button class="btn btn-sm btn-outline-danger skill-delete-btn"><i class="fas fa-trash"></i></button>
        </div>
        <div class="skill-editor mt-2 w-100" style="display:none;">
          <div class="row g-2 align-items-center">
            <div class="col-md-8">
              <input type="text" class="form-control form-control-sm skill-name-input" value="${s.name}">
            </div>
            <div class="col-md-4 text-end">
              <button class="btn btn-sm btn-success skill-save-btn"><i class="fas fa-check"></i></button>
              <button class="btn btn-sm btn-secondary skill-cancel-btn"><i class="fas fa-times"></i></button>
            </div>
          </div>
        </div>
      `;
      skillsList.appendChild(div);
    });

    // rebuild chips
    chips.innerHTML = '';
    skills.forEach(s => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn btn-outline-primary btn-sm skill-chip me-2 mb-2';
      btn.dataset.skill = s.name;
      btn.textContent = s.name;
      chips.appendChild(btn);
    });
  }

  function openEditorForRow(row) {
    const editor = row.querySelector('.skill-editor');
    const name = row.dataset.skillName || row.querySelector('.skill-name-display').textContent;
    if (!editor) return;
    editor.style.display = '';
    const nameInput = editor.querySelector('.skill-name-input');
    if (nameInput) nameInput.value = name;
  }
  function closeEditorForRow(row) {
    const editor = row.querySelector('.skill-editor');
    if (editor) editor.style.display = 'none';
  }

  function collectSkillsFromDOM() {
    const rows = document.querySelectorAll('#skills-list .skill-row');
    const arr = [];
    rows.forEach(r => {
      const name = (r.dataset.skillName || r.querySelector('.skill-name-display')?.textContent || '').trim();
      if (name) arr.push({ name });
    });
    return arr;
  }

  async function sendSkillsToServer(skills) {
    if (!window.SKILLS_UPDATE_URL) {
      alert('No SKILLS_UPDATE_URL configured on the page.');
      return null;
    }
    // send names-only array for compatibility
    const payload = { skills: skills.map(s => s.name ? s.name.trim() : '').filter(Boolean) };
    try {
      const res = await fetch(window.SKILLS_UPDATE_URL, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error('Server error: ' + res.status + ' - ' + text);
      }
      const data = await res.json();
      return data;
    } catch (err) {
      console.error('Save skills error', err);
      alert('Could not save skills: ' + (err.message || err));
      return null;
    }
  }

  // ---------- Initialization ----------
  document.addEventListener('DOMContentLoaded', function () {
    const initialSkillsRaw = window.INITIAL_SKILLS || [];
    // normalize initial skills to [{name: '...'}]
    const initialSkills = initialSkillsRaw.map(s => ({ name: s.name || (typeof s === 'string' ? s : '') })).filter(s => s.name);
    renderSkills(initialSkills);

    // open editor on chip click (same as before)
    document.getElementById('skill-chips')?.addEventListener('click', function (e) {
      const btn = e.target.closest('.skill-chip');
      if (!btn) return;
      const skillName = btn.dataset.skill;
      const rows = document.querySelectorAll('#skills-list .skill-row');
      for (let i=0;i<rows.length;i++) {
        const row = rows[i];
        if ((row.dataset.skillName || row.querySelector('.skill-name-display').textContent).trim() === skillName) {
          openEditorForRow(row);
          row.scrollIntoView({behavior:'smooth', block:'center'});
          break;
        }
      }
    });

    // Save / Cancel / Delete / Edit handlers (delegated)
    document.getElementById('skills-list')?.addEventListener('click', async function (e) {
      const row = e.target.closest('.skill-row');
      if (!row) return;

      if (e.target.closest('.skill-edit-btn')) {
        openEditorForRow(row);
        return;
      }

      if (e.target.closest('.skill-save-btn')) {
        const editor = row.querySelector('.skill-editor');
        const name = editor.querySelector('.skill-name-input').value.trim();
        if (!name) return alert('Skill name required');
        // update DOM
        row.dataset.skillName = name;
        row.querySelector('.skill-name-display').textContent = name;
        closeEditorForRow(row);

        // send to server
        const skills = collectSkillsFromDOM();
        const res = await sendSkillsToServer(skills);
        if (res && res.success) {
          // if server returns updated list, map to {name}
          const serverList = (res.skills || []).map(x => ({ name: (x.name || x).toString() }));
          renderSkills(serverList.length ? serverList : skills);
        }
        return;
      }

      if (e.target.closest('.skill-cancel-btn')) {
        closeEditorForRow(row);
        return;
      }

      if (e.target.closest('.skill-delete-btn')) {
        if (!confirm('Delete this skill?')) return;
        row.remove();
        const skills = collectSkillsFromDOM();
        const res = await sendSkillsToServer(skills);
        if (res && res.success) {
          const serverList = (res.skills || []).map(x => ({ name: (x.name || x).toString() }));
          renderSkills(serverList);
        }
        return;
      }
    });

    // Add-skill UI
    document.getElementById('add-skill-btn')?.addEventListener('click', function () {
      document.getElementById('add-skill-row').style.display = '';
      document.getElementById('new-skill-name').focus();
    });
    document.getElementById('new-skill-cancel')?.addEventListener('click', function () {
      document.getElementById('add-skill-row').style.display = 'none';
    });
    document.getElementById('new-skill-save')?.addEventListener('click', async function () {
      const name = document.getElementById('new-skill-name').value.trim();
      if (!name) return alert('Skill name required');
      const skills = collectSkillsFromDOM();
      skills.push({ name });
      const res = await sendSkillsToServer(skills);
      if (res && res.success) {
        const serverList = (res.skills || []).map(x => ({ name: (x.name || x).toString() }));
        renderSkills(serverList.length ? serverList : skills);
        document.getElementById('add-skill-row').style.display = 'none';
        document.getElementById('new-skill-name').value = '';
      }
    });
  });

  // ---------- Education code preserved below ----------
  // (append the rest of your existing education IIFE here unchanged)
})();

// ---------- Education inline editor (with client validation) ----------
(function () {
  function getCookie(name) {
    const v = `; ${document.cookie}`;
    const parts = v.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }
  const csrftoken = sanitizeToken(getCSRFToken('csrftoken'));

  function renderEducation(list) {
    const container = document.getElementById('education-list');
    if (!container) return;
    const rows = container.querySelectorAll('.education-row');
    if (rows.length && rows.length === list.length) {
      rows.forEach((row, i) => {
        const e = list[i];
        row.dataset.degree = e.degree || '';
        row.dataset.institute = e.institute || '';
        row.dataset.start = e.start_year || '';
        row.dataset.end = e.end_year || '';
        row.dataset.cgpa = e.cgpa || '';
        row.dataset.desc = e.description || '';
        row.querySelector('.edu-degree').textContent = e.degree || '';
        row.querySelector('.edu-institute').textContent = e.institute || '';
        const meta = row.querySelector('.text-muted.small');
        if (meta) meta.textContent = `${e.start_year || ''} - ${e.end_year || ''} \u00B7 CGPA: ${e.cgpa || ''}`;
        row.querySelector('.edu-desc').textContent = e.description || '';
        const editor = row.querySelector('.education-editor');
        if (editor) {
          editor.querySelector('.edu-input-degree').value = e.degree || '';
          editor.querySelector('.edu-input-institute').value = e.institute || '';
          editor.querySelector('.edu-input-start').value = e.start_year || '';
          editor.querySelector('.edu-input-end').value = e.end_year || '';
          editor.querySelector('.edu-input-cgpa').value = e.cgpa || '';
          editor.querySelector('.edu-input-desc').value = e.description || '';
        }
      });
    } else {
      container.innerHTML = '';
      list.forEach((e, idx) => {
        const el = document.createElement('div');
        el.className = 'education-row mb-3 p-3 rounded';
        el.dataset.index = idx;
        el.dataset.degree = e.degree || '';
        el.dataset.institute = e.institute || '';
        el.dataset.start = e.start_year || '';
        el.dataset.end = e.end_year || '';
        el.dataset.cgpa = e.cgpa || '';
        el.dataset.desc = e.description || '';
        el.innerHTML = `
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h5 class="mb-1 edu-degree">${e.degree || ''}</h5>
              <div class="edu-institute text-primary mb-1">${e.institute || ''}</div>
              <div class="text-muted small">${e.start_year || ''} - ${e.end_year || ''} &nbsp;•&nbsp; CGPA: ${e.cgpa || ''}</div>
              <div class="edu-desc mt-2 text-muted">${e.description || ''}</div>
            </div>
            <div class="text-end">
              <button class="btn btn-sm btn-outline-secondary edu-edit-btn"><i class="fas fa-edit"></i></button>
              <button class="btn btn-sm btn-outline-danger edu-delete-btn"><i class="fas fa-trash"></i></button>
            </div>
          </div>
          <div class="education-editor mt-3" style="display:none;">
            <div class="row g-2">
              <div class="col-md-6"><input type="text" class="form-control form-control-sm edu-input-degree" placeholder="Degree / Course" value="${e.degree || ''}"></div>
              <div class="col-md-6"><input type="text" class="form-control form-control-sm edu-input-institute" placeholder="Institute" value="${e.institute || ''}"></div>
              <div class="col-md-3"><input type="text" class="form-control form-control-sm edu-input-start" placeholder="Start Year" value="${e.start_year || ''}"></div>
              <div class="col-md-3"><input type="text" class="form-control form-control-sm edu-input-end" placeholder="End Year" value="${e.end_year || ''}"></div>
              <div class="col-md-3"><input type="text" class="form-control form-control-sm edu-input-cgpa" placeholder="CGPA" value="${e.cgpa || ''}"></div>
              <div class="col-md-12 mt-2"><textarea class="form-control form-control-sm edu-input-desc" placeholder="Description / coursework" rows="2">${e.description || ''}</textarea></div>
              <div class="col-md-12 text-end mt-2"><button class="btn btn-sm btn-success edu-save-btn"><i class="fas fa-check"></i> Save</button> <button class="btn btn-sm btn-secondary edu-cancel-btn"><i class="fas fa-times"></i> Cancel</button></div>
            </div>
          </div>
        `;
        container.appendChild(el);
      });
    }

    // Disable Add button if reached max
    const addBtn = document.getElementById('add-edu-btn');
    if (addBtn) addBtn.disabled = (list.length >= 2);
  }

  async function postEducationToServer(list) {
    if (!window.EDU_UPDATE_URL) {
      alert('No EDU_UPDATE_URL configured on page.');
      return null;
    }

    // Client-side validation before sending
    // - enforce max 2
    if (!Array.isArray(list)) list = [];
    if (list.length > 2) {
      alert('You can only save up to 2 education entries.');
      return null;
    }

    // Validate cgpa numeric
    for (const e of list) {
      const cgpa = (e.cgpa || '').toString().trim();
      if (cgpa) {
        if (isNaN(Number(cgpa))) {
          alert(`CGPA must be a number for "${e.degree || e.institute || ''}".`);
          return null;
        }
      }
    }

    try {
      const res = await fetch(window.SKILLS_UPDATE_URL, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(payload)
      });


      const text = await res.text();
      let data = null;
      try { data = JSON.parse(text); } catch (e) { /* not JSON */ }

      if (!res.ok) {
        const msg = (data && data.message) ? data.message : `Server error ${res.status}`;
        alert(msg);
        return null;
      }
      return data;
    } catch (err) {
      console.error('Education save error', err);
      alert('Could not save education: ' + (err.message || err));
      return null;
    }
  }

  function openEditor(row) {
    const editor = row.querySelector('.education-editor');
    if (!editor) return;
    editor.style.display = '';
  }
  function closeEditor(row) {
    const editor = row.querySelector('.education-editor');
    if (editor) editor.style.display = 'none';
  }
  function collectEducationFromDOM() {
    const rows = document.querySelectorAll('#education-list .education-row');
    const arr = [];
    rows.forEach(r => {
      arr.push({
        degree: (r.dataset.degree || '').trim(),
        institute: (r.dataset.institute || '').trim(),
        start_year: (r.dataset.start || '').trim(),
        end_year: (r.dataset.end || '').trim(),
        cgpa: (r.dataset.cgpa || '').trim(),
        description: (r.dataset.desc || '').trim()
      });
    });
    return arr;
  }

  document.addEventListener('DOMContentLoaded', function () {
    // initial render from template-provided data
    const initial = window.INITIAL_EDUCATION || [];
    renderEducation(initial);

    // delegate edit/delete/save/cancel
    document.getElementById('education-list').addEventListener('click', async function (e) {
      const row = e.target.closest('.education-row');
      if (!row) return;

      // Edit
      if (e.target.closest('.edu-edit-btn')) {
        openEditor(row);
        return;
      }
      // Delete
      if (e.target.closest('.edu-delete-btn')) {
        if (!confirm('Delete this education entry?')) return;
        row.remove();
        const list = collectEducationFromDOM();
        const res = await postEducationToServer(list);
        if (res && res.success) renderEducation(res.education || list);
        return;
      }
      // Save (inline)
      if (e.target.closest('.edu-save-btn')) {
        const editor = row.querySelector('.education-editor');
        const degree = editor.querySelector('.edu-input-degree').value.trim();
        const institute = editor.querySelector('.edu-input-institute').value.trim();
        const start = editor.querySelector('.edu-input-start').value.trim();
        const end = editor.querySelector('.edu-input-end').value.trim();
        const cgpa = editor.querySelector('.edu-input-cgpa').value.trim();
        const desc = editor.querySelector('.edu-input-desc').value.trim();

        // client-side cgpa validation
        if (cgpa && isNaN(Number(cgpa))) {
          alert('CGPA must be a number');
          return;
        }

        // Update row dataset and display
        row.dataset.degree = degree;
        row.dataset.institute = institute;
        row.dataset.start = start;
        row.dataset.end = end;
        row.dataset.cgpa = cgpa;
        row.dataset.desc = desc;

        row.querySelector('.edu-degree').textContent = degree;
        row.querySelector('.edu-institute').textContent = institute;
        const meta = row.querySelector('.text-muted.small');
        if (meta) meta.textContent = `${start} - ${end} \u00B7 CGPA: ${cgpa}`;
        row.querySelector('.edu-desc').textContent = desc;

        closeEditor(row);

        // save all to server
        const list = collectEducationFromDOM();
        // client-side max 2 guard
        if (list.length > 2) {
          alert('You can only save up to 2 education entries.');
          return;
        }
        const res = await postEducationToServer(list);
        if (res && res.success) renderEducation(res.education || list);
        return;
      }

      // Cancel
      if (e.target.closest('.edu-cancel-btn')) {
        closeEditor(row);
        return;
      }
    });

    // Add education handlers
    document.getElementById('add-edu-btn').addEventListener('click', function () {
      // disable if already 2 entries
      const current = document.querySelectorAll('#education-list .education-row').length;
      if (current >= 2) {
        alert('You already have 2 education entries (maximum).');
        return;
      }
      document.getElementById('add-edu-row').style.display = '';
      document.getElementById('new-edu-degree').focus();
    });
    document.getElementById('new-edu-cancel').addEventListener('click', function () {
      document.getElementById('add-edu-row').style.display = 'none';
    });
    document.getElementById('new-edu-save').addEventListener('click', async function () {
      const degree = document.getElementById('new-edu-degree').value.trim();
      const institute = document.getElementById('new-edu-institute').value.trim();
      const start = document.getElementById('new-edu-start').value.trim();
      const end = document.getElementById('new-edu-end').value.trim();
      const cgpa = document.getElementById('new-edu-cgpa').value.trim();
      const desc = document.getElementById('new-edu-desc').value.trim();

      // client-side cgpa validation
      if (cgpa && isNaN(Number(cgpa))) {
        alert('CGPA must be a number');
        return;
      }

      // guard max 2
      const list = collectEducationFromDOM();
      if (list.length >= 2) {
        alert('You can only save up to 2 education entries.');
        return;
      }

      list.push({ degree, institute, start_year: start, end_year: end, cgpa, description: desc });
      const res = await postEducationToServer(list);
      if (res && res.success) {
        renderEducation(res.education || list);
        // hide add form and reset
        document.getElementById('add-edu-row').style.display = 'none';
        document.getElementById('new-edu-degree').value = '';
        document.getElementById('new-edu-institute').value = '';
        document.getElementById('new-edu-start').value = '';
        document.getElementById('new-edu-end').value = '';
        document.getElementById('new-edu-cgpa').value = '';
        document.getElementById('new-edu-desc').value = '';
      }
    });
  });
})();


// ---------- Experience editor (max 4) ----------
(function () {
  const csrftoken = sanitizeToken(getCSRFToken());

  function renderExperience(list) {
    const container = document.getElementById('experience-list'); if(!container) return;
    const rows = container.querySelectorAll('.experience-row');
    if(rows.length && rows.length === list.length) {
      rows.forEach((row,i) => {
        const e = list[i];
        row.dataset.title = e.title || '';
        row.dataset.company = e.company || '';
        row.dataset.start = e.start || '';
        row.dataset.end = e.end || '';
        row.dataset.duration = e.duration || '';
        row.dataset.desc = e.description || '';
        row.querySelector('.item-title').textContent = e.title || '';
        row.querySelector('.item-subtitle').textContent = e.company || '';
        const meta = row.querySelector('.item-duration');
        if(meta) meta.textContent = `${e.start || ''} - ${e.end || ''} • ${e.duration || ''}`;
        row.querySelector('.item-description').textContent = e.description || '';
        const editor = row.querySelector('.experience-editor');
        if(editor) {
          editor.querySelector('.exp-input-title').value = e.title || '';
          editor.querySelector('.exp-input-company').value = e.company || '';
          editor.querySelector('.exp-input-start').value = e.start || '';
          editor.querySelector('.exp-input-end').value = e.end || '';
          editor.querySelector('.exp-input-duration').value = e.duration || '';
          editor.querySelector('.exp-input-desc').value = e.description || '';
        }
      });
    } else {
      container.innerHTML = '';
      list.forEach((e,idx) => {
        const el = document.createElement('div');
        el.className = 'experience-row mb-3 p-3 rounded experience-item';
        el.dataset.index = idx; el.dataset.title = e.title || ''; el.dataset.company = e.company || ''; el.dataset.start = e.start || ''; el.dataset.end = e.end || ''; el.dataset.duration = e.duration || ''; el.dataset.desc = e.description || '';
        el.innerHTML = `
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="item-title">${e.title || ''}</div>
              <div class="item-subtitle">${e.company || ''}</div>
              <div class="item-duration text-muted small">${e.start || ''} - ${e.end || ''} &nbsp;•&nbsp; ${e.duration || ''}</div>
              <div class="item-description mt-2 text-muted">${e.description || ''}</div>
            </div>
            <div class="text-end">
              <button class="btn btn-sm btn-outline-secondary exp-edit-btn"><i class="fas fa-edit"></i></button>
              <button class="btn btn-sm btn-outline-danger exp-delete-btn"><i class="fas fa-trash"></i></button>
            </div>
          </div>
          <div class="experience-editor mt-3" style="display:none;">
            <div class="row g-2">
              <div class="col-md-6"><input type="text" class="form-control form-control-sm exp-input-title" placeholder="Title/Role" value="${e.title || ''}"></div>
              <div class="col-md-6"><input type="text" class="form-control form-control-sm exp-input-company" placeholder="Company" value="${e.company || ''}"></div>
              <div class="col-md-3"><input type="text" class="form-control form-control-sm exp-input-start" placeholder="Start" value="${e.start || ''}"></div>
              <div class="col-md-3"><input type="text" class="form-control form-control-sm exp-input-end" placeholder="End" value="${e.end || ''}"></div>
              <div class="col-md-6"><input type="text" class="form-control form-control-sm exp-input-duration" placeholder="Duration" value="${e.duration || ''}"></div>
              <div class="col-md-12 mt-2"><textarea class="form-control form-control-sm exp-input-desc" placeholder="Description" rows="2">${e.description || ''}</textarea></div>
              <div class="col-md-12 text-end mt-2"><button class="btn btn-sm btn-success exp-save-btn"><i class="fas fa-check"></i> Save</button> <button class="btn btn-sm btn-secondary exp-cancel-btn"><i class="fas fa-times"></i> Cancel</button></div>
            </div>
          </div>
        `;
        container.appendChild(el);
      });
    }

    const addBtn = document.getElementById('add-exp-btn'); if(addBtn) addBtn.disabled = (list.length >= 4);
  }

  function collectExperienceFromDOM() {
    const rows = document.querySelectorAll('#experience-list .experience-row'); const arr = [];
    rows.forEach(r => {
      arr.push({
        title: (r.dataset.title || '').trim(),
        company: (r.dataset.company || '').trim(),
        start: (r.dataset.start || '').trim(),
        end: (r.dataset.end || '').trim(),
        duration: (r.dataset.duration || '').trim(),
        description: (r.dataset.desc || '').trim()
      });
    });
    return arr;
  }

  async function postExperienceToServer(list) {
    if (!window.EXP_UPDATE_URL) { alert('No EXP_UPDATE_URL configured'); return null; }
    if (!Array.isArray(list)) list = [];
    if (list.length > 4) { alert('You can only save up to 4 experience entries.'); return null; }

    const token = sanitizeToken(getCSRFToken());
    if (!token) {
      console.error('CSRF token missing for Experience. document.cookie=', document.cookie);
      alert('CSRF token not found — cannot save experience. Make sure cookies are enabled and your server sets csrftoken.');
      return null;
    }

    try {
      const res = await fetch(window.EXP_UPDATE_URL, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type':'application/json',
          'X-CSRFToken': token,
          'X-Requested-With':'XMLHttpRequest'
        },
        body: JSON.stringify({ experience: list })
      });

      const text = await res.text();
      let data = null;
      try { data = JSON.parse(text); } catch(e) { /* not JSON */ }

      if (!res.ok) { alert((data && data.message) ? data.message : 'Server error '+res.status); return null; }
      return data;
    } catch(err) { console.error(err); alert('Could not save experience: ' + (err.message || err)); return null; }
  }

  document.addEventListener('DOMContentLoaded', function () {
    const initial = window.INITIAL_EXPERIENCE || [];
    renderExperience(initial);

    document.getElementById('experience-list')?.addEventListener('click', async function(e){
      const row = e.target.closest('.experience-row'); if(!row) return;
      if (e.target.closest('.exp-edit-btn')) { row.querySelector('.experience-editor').style.display=''; return; }
      if (e.target.closest('.exp-cancel-btn')) { row.querySelector('.experience-editor').style.display='none'; return; }
      if (e.target.closest('.exp-delete-btn')) {
        if (!confirm('Delete this experience entry?')) return;
        row.remove();
        const list = collectExperienceFromDOM();
        const res = await postExperienceToServer(list);
        if (res && res.success) renderExperience(res.experience || list);
        return;
      }
      if (e.target.closest('.exp-save-btn')) {
        const editor = row.querySelector('.experience-editor');
        const title = editor.querySelector('.exp-input-title').value.trim();
        const company = editor.querySelector('.exp-input-company').value.trim();
        const start = editor.querySelector('.exp-input-start').value.trim();
        const end = editor.querySelector('.exp-input-end').value.trim();
        const duration = editor.querySelector('.exp-input-duration').value.trim();
        const desc = editor.querySelector('.exp-input-desc').value.trim();

        // update dataset/display
        row.dataset.title = title; row.dataset.company = company; row.dataset.start = start; row.dataset.end = end; row.dataset.duration = duration; row.dataset.desc = desc;
        row.querySelector('.item-title').textContent = title; row.querySelector('.item-subtitle').textContent = company;
        const meta = row.querySelector('.item-duration'); if(meta) meta.textContent = `${start} - ${end} • ${duration}`;
        row.querySelector('.item-description').textContent = desc;
        row.querySelector('.experience-editor').style.display='none';

        const list = collectExperienceFromDOM();
        if (list.length > 4) { alert('You can only save up to 4 experience entries.'); return; }
        const res = await postExperienceToServer(list);
        if (res && res.success) renderExperience(res.experience || list);
      }
    });

    document.getElementById('add-exp-btn')?.addEventListener('click', function(){
      const current = document.querySelectorAll('#experience-list .experience-row').length;
      if (current >= 4) { alert('Maximum 4 experience entries allowed.'); return; }
      document.getElementById('add-exp-row').style.display = '';
      document.getElementById('new-exp-title').focus();
    });
    document.getElementById('new-exp-cancel')?.addEventListener('click', function(){ document.getElementById('add-exp-row').style.display='none'; });
    document.getElementById('new-exp-save')?.addEventListener('click', async function(){
      const title = document.getElementById('new-exp-title').value.trim();
      const company = document.getElementById('new-exp-company').value.trim();
      const start = document.getElementById('new-exp-start').value.trim();
      const end = document.getElementById('new-exp-end').value.trim();
      const duration = document.getElementById('new-exp-duration').value.trim();
      const desc = document.getElementById('new-exp-desc').value.trim();

      const list = collectExperienceFromDOM();
      if (list.length >= 4) { alert('Maximum 4 experience entries allowed.'); return; }
      list.push({ title, company, start, end, duration, description: desc });
      const res = await postExperienceToServer(list);
      if (res && res.success) {
        renderExperience(res.experience || list);
        document.getElementById('add-exp-row').style.display='none';
        document.getElementById('new-exp-title').value=''; document.getElementById('new-exp-company').value=''; document.getElementById('new-exp-start').value=''; document.getElementById('new-exp-end').value=''; document.getElementById('new-exp-duration').value=''; document.getElementById('new-exp-desc').value='';
      }
    });
  });
})();


// ---------- Datepicker + duration helpers (flatpickr-aware) ----------
(function(){
  // parse YYYY-MM-DD or try Date fallback
  function parseDateISO(s) {
    if (!s) return null;
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s);
    if (m) return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
    const d = new Date(s);
    return isNaN(d.getTime()) ? null : d;
  }

  // format: "June 2024"
  function formatMonthYear(d) {
    if (!d) return '';
    try {
      const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
      return `${months[d.getMonth()]} ${d.getFullYear()}`;
    } catch (e) {
      return '';
    }
  }

  // compute duration in human readable full-words:
  // "2 months", "1 year 3 months", "Less than 1 month"
  function computeDurationHuman(startDate, endDate) {
    if (!startDate) return '';
    const now = new Date();
    const e = endDate || now;

    // normalize day components to avoid negative day quirks
    let years = e.getFullYear() - startDate.getFullYear();
    let months = e.getMonth() - startDate.getMonth();
    let days = e.getDate() - startDate.getDate();

    if (days < 0) {
      months -= 1;
      // we don't need exact days for display, months is enough
    }
    if (months < 0) {
      years -= 1;
      months += 12;
    }

    const parts = [];
    if (years > 0) parts.push(years + (years === 1 ? ' year' : ' years'));
    if (months > 0) parts.push(months + (months === 1 ? ' month' : ' months'));

    if (parts.length === 0) {
      // less than 1 month
      return 'Less than 1 month';
    }
    return parts.join(' ');
  }

  // init flatpickr or fallback to native change listener
  function initDatepickers(container) {
    container = container || document;
    if (typeof flatpickr !== 'undefined') {
      container.querySelectorAll('.datepicker').forEach(el => {
        if (el._flatpickr) return;
        flatpickr(el, {
          dateFormat: 'Y-m-d',
          allowInput: true,
          onChange: function(selectedDates, dateStr, instance) { rowDurationUpdate(el); }
        });
      });
    } else {
      container.querySelectorAll('.datepicker, input[type="date"]').forEach(el => {
        // avoid adding duplicate listener
        if (!el._profile_listener_attached) {
          el.addEventListener('change', function(){ rowDurationUpdate(el); });
          el._profile_listener_attached = true;
        }
      });
    }
  }

  // sanitize token helper
  function sanitizeToken(token) {
    if (!token) return null;
    token = token.toString().trim();
    // strip surrounding quotes (sometimes happens)
    token = token.replace(/^"(.*)"$/, '$1').replace(/^'(.*)'$/, '$1');
    return token || null;
  }

  // update duration and meta for a row when date inputs change
  function rowDurationUpdate(el) {
    const row = el.closest('.experience-row') || el.closest('.project-row');
    if (!row) return;

    const startEl = row.querySelector('.exp-input-start, .proj-input-start');
    const endEl = row.querySelector('.exp-input-end, .proj-input-end');

    const startStr = startEl ? (startEl.value||'').trim() : (row.dataset.start||'');
    const endStr   = endEl ? (endEl.value||'').trim() : (row.dataset.end||'');

    const sDate = parseDateISO(startStr);
    const eDate = endStr ? parseDateISO(endStr) : null;

    const human = computeDurationHuman(sDate, eDate);

    // update duration input if exists
    const durInput = row.querySelector('.exp-input-duration, .proj-input-duration');
    if (durInput) durInput.value = human;

    // format meta like "June 2024 - July 2024 • 2 months"
    const startLabel = sDate ? formatMonthYear(sDate) : (startStr || '');
    const endLabel = endStr ? (eDate ? formatMonthYear(eDate) : endStr) : (endStr === '' ? 'Present' : '');

    const meta = row.querySelector('.item-duration, .text-muted.small');
    if (meta) {
      // keep a consistent separator
      const durationPart = human ? ` \u00B7 ${human}` : '';
      meta.textContent = `${startLabel} - ${endLabel}${durationPart}`;
    }

    // update dataset for later collect
    row.dataset.start = startStr || '';
    row.dataset.end = endStr || '';
    row.dataset.duration = human || '';
  }

  // expose to global for other code
  window.initProfileDatepickers = function (containerSelector) {
    const c = document.querySelector(containerSelector) || document;
    initDatepickers(c);
  };
  window.computeDurationForInputs = function (startStr, endStr) {
    const s = parseDateISO(startStr);
    const e = endStr ? parseDateISO(endStr) : null;
    return computeDurationHuman(s,e);
  };

  // auto init for page static content
  document.addEventListener('DOMContentLoaded', function(){
    initDatepickers(document);
    // when experience/projects already rendered by other IIFE, this will attach pickers
  });

})();

// ---------- Projects editor (max 3) ----------
(function(){
  const csrftoken = sanitizeToken(getCSRFToken());

  function renderProjects(list){
    const container = document.getElementById('projects-list'); if(!container) return;
    const rows = container.querySelectorAll('.project-row');
    if(rows.length && rows.length === list.length){
      rows.forEach((row,i)=>{ const e = list[i]; row.dataset.title = e.title||''; row.dataset.tech = e.technologies||''; row.dataset.start = e.start||''; row.dataset.end = e.end||''; row.dataset.desc = e.description||''; row.querySelector('.item-title').textContent = e.title||''; row.querySelector('.item-subtitle').textContent = e.technologies||''; const meta = row.querySelector('.item-duration'); if(meta) meta.textContent = `${e.start||''} - ${e.end||''}`; row.querySelector('.item-description').textContent = e.description||''; const editor = row.querySelector('.project-editor'); if(editor){ editor.querySelector('.proj-input-title').value = e.title||''; editor.querySelector('.proj-input-tech').value = e.technologies||''; editor.querySelector('.proj-input-start').value = e.start||''; editor.querySelector('.proj-input-end').value = e.end||''; editor.querySelector('.proj-input-desc').value = e.description||''; }});
    } else {
      container.innerHTML = '';
      list.forEach((e,idx)=>{
        const el = document.createElement('div');
        el.className = 'project-row mb-3 p-3 rounded experience-item';
        el.dataset.index = idx; el.dataset.title = e.title||''; el.dataset.tech = e.technologies||''; el.dataset.start = e.start||''; el.dataset.end = e.end||''; el.dataset.desc = e.description||'';
        el.innerHTML = `
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="item-title">${e.title||''}</div>
              <div class="item-subtitle">${e.technologies||''}</div>
              <div class="item-duration text-muted small">${e.start||''} - ${e.end||''}</div>
              <div class="item-description mt-2 text-muted">${e.description||''}</div>
            </div>
            <div class="text-end">
              <button class="btn btn-sm btn-outline-secondary proj-edit-btn"><i class="fas fa-edit"></i></button>
              <button class="btn btn-sm btn-outline-danger proj-delete-btn"><i class="fas fa-trash"></i></button>
            </div>
          </div>
          <div class="project-editor mt-3" style="display:none;">
            <div class="row g-2">
              <div class="col-md-6"><input type="text" class="form-control form-control-sm proj-input-title" placeholder="Project title" value="${e.title||''}"></div>
              <div class="col-md-6"><input type="text" class="form-control form-control-sm proj-input-tech" placeholder="Technologies (comma separated)" value="${e.technologies||''}"></div>
              <div class="col-md-3"><input type="text" class="form-control form-control-sm proj-input-start datepicker" placeholder="Start date" value="${e.start||''}"></div>
              <div class="col-md-3"><input type="text" class="form-control form-control-sm proj-input-end datepicker" placeholder="End date (leave blank for Present)" value="${e.end||''}"></div>
              <div class="col-md-12 mt-2"><textarea class="form-control form-control-sm proj-input-desc" placeholder="Short description" rows="2">${e.description||''}</textarea></div>
              <div class="col-md-12 text-end mt-2"><button class="btn btn-sm btn-success proj-save-btn"><i class="fas fa-check"></i> Save</button> <button class="btn btn-sm btn-secondary proj-cancel-btn"><i class="fas fa-times"></i> Cancel</button></div>
            </div>
          </div>
        `;
        container.appendChild(el);
      });
    }
    // disable add button if max reached
    const addBtn = document.getElementById('add-proj-btn'); if(addBtn) addBtn.disabled = (list.length >= 3);
    // init datepickers for newly added fields
    if (window.initProfileDatepickers) window.initProfileDatepickers('#projects-list');
  }

  function collectProjectsFromDOM(){
    const rows = document.querySelectorAll('#projects-list .project-row'); const arr = [];
    rows.forEach(r => {
      arr.push({
        title: (r.dataset.title || '').trim(),
        technologies: (r.dataset.tech || '').trim(),
        start: (r.dataset.start || '').trim(),
        end: (r.dataset.end || '').trim(),
        description: (r.dataset.desc || '').trim()
      });
    });
    return arr;
  }

async function postProjectsToServer(list){
  if (!window.PROJ_UPDATE_URL) { alert('No PROJ_UPDATE_URL configured on page.'); return null; }
  if (!Array.isArray(list)) list = [];
  if (list.length > 3) { alert('You can only save up to 3 projects.'); return null; }

  const token = sanitizeToken(getCSRFToken());
  if (!token) {
    console.error('CSRF token missing for Projects. document.cookie=', document.cookie);
    alert('CSRF token not found — cannot save projects. Make sure cookies are enabled and your server sets csrftoken.');
    return null;
  }

  console.log('postProjectsToServer -> URL=', window.PROJ_UPDATE_URL, 'CSRF token length=', token.length, 'payload=', list);

  try {
    const res = await fetch(window.PROJ_UPDATE_URL, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': token,
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify({ projects: list })
    });

    const text = await res.text();
    let data = null;
    try { data = JSON.parse(text); } catch(e) { /* not JSON */ }

    if (!res.ok) {
      console.error('postProjectsToServer failed', res.status, text);
      alert((data && data.message) ? data.message : 'Server error ' + res.status);
      return null;
    }
    return data;
  } catch(err) {
    console.error('postProjectsToServer exception', err);
    alert('Could not save projects: ' + (err.message || err));
    return null;
  }
}


  document.addEventListener('DOMContentLoaded', function(){
    const initial = window.INITIAL_PROJECTS || [];
    renderProjects(initial);

    document.getElementById('projects-list')?.addEventListener('click', async function(e){
      const row = e.target.closest('.project-row'); if(!row) return;
      if (e.target.closest('.proj-edit-btn')) { row.querySelector('.project-editor').style.display=''; if(window.initProfileDatepickers) window.initProfileDatepickers(row); return; }
      if (e.target.closest('.proj-cancel-btn')) { row.querySelector('.project-editor').style.display='none'; return; }
      if (e.target.closest('.proj-delete-btn')) {
        if (!confirm('Delete this project?')) return;
        row.remove();
        const list = collectProjectsFromDOM();
        const res = await postProjectsToServer(list);
        if (res && res.success) renderProjects(res.projects || list);
        return;
      }
      if (e.target.closest('.proj-save-btn')) {
        const editor = row.querySelector('.project-editor');
        const title = editor.querySelector('.proj-input-title').value.trim();
        const tech = editor.querySelector('.proj-input-tech').value.trim();
        const start = editor.querySelector('.proj-input-start').value.trim();
        const end = editor.querySelector('.proj-input-end').value.trim();
        const desc = editor.querySelector('.proj-input-desc').value.trim();
        row.dataset.title = title; row.dataset.tech = tech; row.dataset.start = start; row.dataset.end = end; row.dataset.desc = desc;
        row.querySelector('.item-title').textContent = title; row.querySelector('.item-subtitle').textContent = tech;
        const meta = row.querySelector('.item-duration'); if(meta) meta.textContent = `${start} - ${end}`;
        row.querySelector('.item-description').textContent = desc;
        row.querySelector('.project-editor').style.display='none';
        const list = collectProjectsFromDOM();
        if (list.length > 3) { alert('You can only save up to 3 projects.'); return; }
        const res = await postProjectsToServer(list);
        if (res && res.success) renderProjects(res.projects || list);
      }
    });

    document.getElementById('add-proj-btn')?.addEventListener('click', function(){
      const current = document.querySelectorAll('#projects-list .project-row').length;
      if (current >= 3) { alert('Maximum 3 projects allowed.'); return; }
      document.getElementById('add-proj-row').style.display = '';
      document.getElementById('new-proj-title').focus();
      if (window.initProfileDatepickers) window.initProfileDatepickers('#add-proj-row');
    });
    document.getElementById('new-proj-cancel')?.addEventListener('click', function(){ document.getElementById('add-proj-row').style.display='none'; });
    document.getElementById('new-proj-save')?.addEventListener('click', async function(){
      const title = document.getElementById('new-proj-title').value.trim();
      const tech = document.getElementById('new-proj-tech').value.trim();
      const start = document.getElementById('new-proj-start').value.trim();
      const end = document.getElementById('new-proj-end').value.trim();
      const desc = document.getElementById('new-proj-desc').value.trim();
      const list = collectProjectsFromDOM();
      if (list.length >= 3) { alert('Maximum 3 projects allowed.'); return; }
      list.push({ title, technologies: tech, start, end, description: desc });
      const res = await postProjectsToServer(list);
      if (res && res.success) {
        renderProjects(res.projects || list);
        document.getElementById('add-proj-row').style.display='none';
        document.getElementById('new-proj-title').value=''; document.getElementById('new-proj-tech').value=''; document.getElementById('new-proj-start').value=''; document.getElementById('new-proj-end').value=''; document.getElementById('new-proj-desc').value='';
      }
    });
  });
})();
