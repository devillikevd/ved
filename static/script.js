/* ═══════════════════════════════════════════════════════════
   VaidiDea Health Library - Advanced Frontend Logic
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

    // ── DOM REFS ───────────────────────────────────────────
    const $ = id => document.getElementById(id);
    const searchInput      = $('searchInput');
    const searchBtn        = $('searchBtn');
    const alphabetBar      = $('alphabetBar');
    const categoriesGrid   = $('categoriesGrid');
    const resultsSection   = $('resultsSection');
    const resultsGrid      = $('resultsGrid');
    const resultsTitle     = $('resultsTitle');
    const resultsBadge     = $('resultsBadge');
    const loader           = $('loader');
    const prevPage         = $('prevPage');
    const nextPage         = $('nextPage');
    const pageInfo         = $('pageInfo');
    const severityFilter   = $('severityFilter');
    const modalOverlay     = $('modalOverlay');
    const modalClose       = $('modalClose');
    const modalBody        = $('modalBody');
    const headerStat       = $('headerStat');

    // ── STATE ──────────────────────────────────────────────
    let currentPage = 1;
    let currentMode = null;   // 'alphabet' | 'search' | 'category'
    let currentQuery = '';
    let totalResults = 0;
    const LIMIT = 50;
    let letterCounts = {};

    // Category icon mapping to emoji/svg symbols
    const CATEGORY_ICONS = {
        virus: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>',
        cancer: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"/><path d="M8 12h8"/><path d="M12 8v8"/></svg>',
        blood: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>',
        metabolism: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>',
        brain: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a7 7 0 0 0-7 7c0 3 2 5.5 4 7l3 3 3-3c2-1.5 4-4 4-7a7 7 0 0 0-7-7z"/></svg>',
        neurology: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
        eye: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>',
        ear: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>',
        heart: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>',
        lungs: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M6.081 20C2.46 20 2 16.5 2 14s1-5.5 3-7c1.5-1.126 2-3.5 2-5"/><path d="M17.92 20C21.54 20 22 16.5 22 14s-1-5.5-3-7c-1.5-1.126-2-3.5-2-5"/><path d="M12 2v8"/></svg>',
        stomach: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>',
        skin: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/></svg>',
        bone: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18"/><path d="M8 4a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"/><path d="M16 16a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"/></svg>',
        kidney: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>',
        pregnancy: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>',
        baby: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>',
        dna: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 15c6.667-6 13.333 0 20-6"/><path d="M9 22c1.8-4 6.2-4 8 0"/><path d="M15 2c-1.8 4-6.2 4-8 0"/></svg>',
        stethoscope: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
        injury: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
        emergency: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
        checkup: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        medical: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>',
        code: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
    };

    const CATEGORY_COLORS = {
        virus: '#e53e3e', cancer: '#9b2c2c', blood: '#c53030', metabolism: '#dd6b20',
        brain: '#805ad5', neurology: '#6b46c1', eye: '#3182ce', ear: '#2b6cb0',
        heart: '#e53e3e', lungs: '#38a169', stomach: '#d69e2e', skin: '#ed8936',
        bone: '#4a5568', kidney: '#319795', pregnancy: '#d53f8c', baby: '#ed64a6',
        dna: '#667eea', stethoscope: '#4299e1', injury: '#e53e3e', emergency: '#c53030',
        checkup: '#38a169', medical: '#4a90d9', code: '#718096',
    };

    // ── INIT ───────────────────────────────────────────────
    loadStats();
    loadCategories();
    buildAlphabet();
    setupEventListeners();
    setupHeaderScroll();

    // ── STATS ──────────────────────────────────────────────
    async function loadStats() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();
            $('statDiseases').textContent = data.total_diseases.toLocaleString();
            $('statCategories').textContent = data.total_categories;
            $('heroCount').textContent = data.total_diseases.toLocaleString();
            headerStat.textContent = `${data.total_diseases.toLocaleString()} Diseases`;

            const critical = data.severity.find(s => s.severity === 'Critical');
            const severe = data.severity.find(s => s.severity === 'Severe');
            $('statCritical').textContent = critical ? critical.cnt.toLocaleString() : '0';
            $('statSevere').textContent = severe ? severe.cnt.toLocaleString() : '0';

            // Store letter counts for the alphabet badges
            data.by_letter.forEach(item => {
                letterCounts[item.first_letter] = item.cnt;
            });
            updateAlphabetCounts();
        } catch (e) {
            console.error('Failed to load stats', e);
        }
    }

    // ── CATEGORIES ─────────────────────────────────────────
    async function loadCategories() {
        try {
            const res = await fetch('/api/categories');
            const cats = await res.json();
            categoriesGrid.innerHTML = '';

            cats.forEach(cat => {
                const iconKey = cat.icon || 'medical';
                const iconSvg = CATEGORY_ICONS[iconKey] || CATEGORY_ICONS.medical;
                const iconColor = CATEGORY_COLORS[iconKey] || '#4a90d9';

                const card = document.createElement('div');
                card.className = 'category-card';
                card.innerHTML = `
                    <div class="cat-icon" style="background:${iconColor}12; color:${iconColor}">${iconSvg}</div>
                    <div class="cat-name">${cat.chapter}</div>
                    <div class="cat-meta">
                        <span class="cat-system">${cat.body_system}</span>
                        <span class="cat-count">${cat.disease_count.toLocaleString()}</span>
                    </div>
                `;
                card.onclick = () => {
                    document.querySelectorAll('.category-card').forEach(c => c.classList.remove('active'));
                    card.classList.add('active');
                    currentMode = 'category';
                    currentQuery = cat.chapter;
                    currentPage = 1;
                    fetchResults();
                    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                };
                categoriesGrid.appendChild(card);
            });
        } catch (e) {
            console.error('Failed to load categories', e);
        }
    }

    // ── ALPHABET ───────────────────────────────────────────
    function buildAlphabet() {
        for (let i = 65; i <= 90; i++) {
            const letter = String.fromCharCode(i);
            const btn = document.createElement('button');
            btn.className = 'alpha-btn';
            btn.id = `alpha-${letter}`;
            btn.innerHTML = `${letter}<span class="alpha-count" id="ac-${letter}">-</span>`;
            btn.onclick = () => {
                document.querySelectorAll('.alpha-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                document.querySelectorAll('.category-card').forEach(c => c.classList.remove('active'));
                searchInput.value = '';
                currentMode = 'alphabet';
                currentQuery = letter;
                currentPage = 1;
                fetchResults();
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            };
            alphabetBar.appendChild(btn);
        }
    }

    function updateAlphabetCounts() {
        for (let i = 65; i <= 90; i++) {
            const letter = String.fromCharCode(i);
            const el = $(`ac-${letter}`);
            if (el && letterCounts[letter]) {
                // Show in thousands if > 999
                const c = letterCounts[letter];
                el.textContent = c > 999 ? `${(c/1000).toFixed(1)}k` : c;
            }
        }
    }

    // ── SEARCH ─────────────────────────────────────────────
    function doSearch() {
        const q = searchInput.value.trim();
        if (q.length < 2) return;

        document.querySelectorAll('.alpha-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.category-card').forEach(c => c.classList.remove('active'));
        currentMode = 'search';
        currentQuery = q;
        currentPage = 1;
        fetchResults();
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // ── FETCH RESULTS ──────────────────────────────────────
    async function fetchResults() {
        resultsSection.style.display = 'block';
        resultsGrid.innerHTML = '';
        loader.classList.add('active');

        let url = '';
        if (currentMode === 'alphabet') {
            resultsTitle.textContent = `Diseases starting with "${currentQuery}"`;
            url = `/api/diseases/alphabet/${currentQuery}?page=${currentPage}&limit=${LIMIT}`;
        } else if (currentMode === 'search') {
            resultsTitle.textContent = `Search results for "${currentQuery}"`;
            url = `/api/diseases/search?q=${encodeURIComponent(currentQuery)}&page=${currentPage}&limit=${LIMIT}`;
        } else if (currentMode === 'category') {
            resultsTitle.textContent = currentQuery;
            url = `/api/diseases/category/${encodeURIComponent(currentQuery)}?page=${currentPage}&limit=${LIMIT}`;
        }

        try {
            const res = await fetch(url);
            const data = await res.json();
            loader.classList.remove('active');

            totalResults = data.total;
            resultsBadge.textContent = `${totalResults.toLocaleString()} results`;

            const totalPages = Math.ceil(totalResults / LIMIT);
            pageInfo.textContent = `Page ${currentPage} of ${totalPages || 1}`;
            prevPage.disabled = currentPage <= 1;
            nextPage.disabled = currentPage >= totalPages;

            if (data.results.length === 0) {
                resultsGrid.innerHTML = '<p style="grid-column:1/-1;text-align:center;padding:3rem;color:#718096;">No results found. Try a different search term.</p>';
                return;
            }

            renderCards(data.results);
        } catch (e) {
            console.error(e);
            loader.classList.remove('active');
            resultsGrid.innerHTML = '<p style="grid-column:1/-1;text-align:center;padding:3rem;color:#e53e3e;">Failed to fetch data. Ensure the server is running.</p>';
        }
    }

    // ── RENDER CARDS ───────────────────────────────────────
    function renderCards(diseases) {
        resultsGrid.innerHTML = '';
        diseases.forEach((d, i) => {
            const card = document.createElement('div');
            card.className = 'disease-card';
            card.style.animationDelay = `${i * 0.03}s`;

            const keywords = d.keywords ? d.keywords.split(',').filter(Boolean).slice(0, 4) : [];
            const keywordHtml = keywords.map(k => `<span class="keyword-tag">${k}</span>`).join('');

            card.innerHTML = `
                <div class="card-top">
                    <div class="card-code-wrap">
                        <span class="card-code">${d.code}</span>
                        <span class="card-code" style="background:#f0fff4;color:#276749;">${d.body_system}</span>
                    </div>
                    <div class="severity-dot ${d.severity}" title="${d.severity}"></div>
                </div>
                <div class="card-name">${d.name}</div>
                <div class="card-chapter">${d.chapter}</div>
                ${keywordHtml ? `<div class="card-keywords">${keywordHtml}</div>` : ''}
                <div class="card-footer">
                    <span class="card-severity ${d.severity}">${d.severity}</span>
                    <span class="card-arrow">View Details &#8594;</span>
                </div>
            `;

            card.onclick = () => openModal(d);
            resultsGrid.appendChild(card);
        });
    }

    // ── MODAL ──────────────────────────────────────────────
    async function openModal(d) {
        const keywords = d.keywords ? d.keywords.split(',').filter(Boolean) : [];
        const keywordHtml = keywords.map(k => `<span class="modal-keyword">${k}</span>`).join('');

        // 1. Show basic info and SKELETON LOADER for AI data
        modalBody.innerHTML = `
            <span class="modal-severity ${d.severity}">${d.severity}</span>
            <h2>${d.name}</h2>
            <div class="modal-grid">
                <div class="modal-field">
                    <div class="modal-field-label">ICD-10 Code</div>
                    <div class="modal-field-value">${d.code}</div>
                </div>
                <div class="modal-field">
                    <div class="modal-field-label">Body System</div>
                    <div class="modal-field-value">${d.body_system}</div>
                </div>
                <div class="modal-field">
                    <div class="modal-field-label">Category</div>
                    <div class="modal-field-value">${d.chapter}</div>
                </div>
                <div class="modal-field">
                    <div class="modal-field-label">Source</div>
                    <div class="modal-field-value">${d.source}</div>
                </div>
            </div>
            ${keywords.length ? `
                <div class="modal-field" style="margin-bottom:1.5rem">
                    <div class="modal-field-label">Related Keywords</div>
                    <div class="modal-keywords">${keywordHtml}</div>
                </div>
            ` : ''}
            
            <div id="aiDetailsContainer">
                <div class="ai-badge">✨ AI Generated Medical Insights</div>
                <div class="skeleton-loader">
                    <div class="skel-line" style="width:100%"></div>
                    <div class="skel-line" style="width:90%"></div>
                    <div class="skel-line" style="width:95%"></div>
                    <div class="skel-line" style="width:80%"></div>
                    <br>
                    <div class="skel-line" style="width:60%"></div>
                    <div class="skel-line" style="width:40%"></div>
                </div>
            </div>
        `;

        modalOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';

        // 2. Fetch AI details
        try {
            const res = await fetch(`/api/disease/${d.code}/details`);
            const details = await res.json();
            
            const aiContainer = $('aiDetailsContainer');
            if(aiContainer) {
                aiContainer.innerHTML = `
                    <div class="ai-badge">✨ AI Generated Medical Insights</div>
                    
                    <div class="detail-section">
                        <h3>Overview</h3>
                        <div class="detail-content">${details.overview}</div>
                    </div>
                    
                    <div class="detail-grid" style="grid-template-columns: 1fr; gap: 1rem; margin-top: 1rem;">
                        <div class="detail-section">
                            <h3 style="color: #c53030;">Causes & Risk Factors</h3>
                            <ul class="detail-list">${details.causes}</ul>
                        </div>
                    </div>
                    
                    <div class="detail-grid" style="grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 0.5rem;">
                        <div class="detail-section">
                            <h3 style="color: #dd6b20;">Common Symptoms</h3>
                            <ul class="detail-list">${details.symptoms}</ul>
                        </div>
                        <div class="detail-section">
                            <h3 style="color: #3182ce;">Medicines & Management</h3>
                            <ul class="detail-list">${details.medicines}</ul>
                        </div>
                        <div class="detail-section">
                            <h3 style="color: #38a169;">Home Remedies & Lifestyle</h3>
                            <ul class="detail-list">${details.home_remedies}</ul>
                        </div>
                        <div class="detail-section">
                            <h3 style="color: #805ad5;">Prevention</h3>
                            <ul class="detail-list">${details.prevention}</ul>
                        </div>
                    </div>
                    
                    <div class="detail-section" style="margin-top: 1rem; background: #fff5f5; padding: 1rem; border-left: 4px solid #e53e3e; border-radius: 4px;">
                        <h3 style="color: #c53030; margin-bottom: 0.25rem;">⚠️ When to see a doctor</h3>
                        <div class="detail-content" style="color: #742a2a;">${details.when_to_see_doctor}</div>
                    </div>
                `;
            }
        } catch (e) {
            console.error("Failed to fetch details", e);
            const aiContainer = $('aiDetailsContainer');
            if(aiContainer) {
                aiContainer.innerHTML = `<div style="color: #e53e3e; padding: 1rem; background: #fff5f5; border-radius: 8px;">Failed to load detailed insights. Please ensure the backend is running.</div>`;
            }
        }
    }

    function closeModal() {
        modalOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // ── EVENT LISTENERS ────────────────────────────────────
    function setupEventListeners() {
        searchBtn.onclick = doSearch;
        searchInput.addEventListener('keypress', e => { if (e.key === 'Enter') doSearch(); });

        // Quick suggestion chips
        document.querySelectorAll('.suggestion').forEach(chip => {
            chip.onclick = () => {
                searchInput.value = chip.dataset.q;
                doSearch();
            };
        });

        // Pagination
        prevPage.onclick = () => { if (currentPage > 1) { currentPage--; fetchResults(); } };
        nextPage.onclick = () => { currentPage++; fetchResults(); };

        // Severity filter (client-side for simplicity)
        severityFilter.onchange = () => {
            const val = severityFilter.value;
            document.querySelectorAll('.disease-card').forEach(card => {
                if (!val) {
                    card.style.display = '';
                } else {
                    const dot = card.querySelector('.severity-dot');
                    card.style.display = dot && dot.classList.contains(val) ? '' : 'none';
                }
            });
        };

        // Modal
        modalClose.onclick = closeModal;
        modalOverlay.onclick = (e) => { if (e.target === modalOverlay) closeModal(); };
        document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
    }

    // ── HEADER SCROLL EFFECT ───────────────────────────────
    function setupHeaderScroll() {
        const header = $('mainHeader');
        window.addEventListener('scroll', () => {
            header.classList.toggle('scrolled', window.scrollY > 10);
        });
    }

});
