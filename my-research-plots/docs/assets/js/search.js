/**
 * Client-side search functionality for SnapshotPlot static sites
 */

class SnapshotSearch {
    constructor() {
        this.searchIndex = [];
        this.searchInput = document.getElementById('search-input');
        this.searchResults = document.getElementById('search-results');
        this.isLoaded = false;
        
        this.init();
    }
    
    async init() {
        // Load search index
        try {
            const response = await fetch('/assets/js/search-index.json');
            this.searchIndex = await response.json();
            this.isLoaded = true;
            console.log(`Loaded ${this.searchIndex.length} snapshots for search`);
        } catch (error) {
            console.warn('Search index not available:', error);
            return;
        }
        
        // Setup event listeners
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        if (!this.searchInput) return;
        
        let debounceTimer;
        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                this.performSearch(e.target.value);
            }, 150);
        });
        
        this.searchInput.addEventListener('focus', () => {
            if (this.searchInput.value.trim()) {
                this.performSearch(this.searchInput.value);
            }
        });
        
        // Hide results when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.searchInput.contains(e.target) && !this.searchResults.contains(e.target)) {
                this.hideResults();
            }
        });
        
        // Keyboard navigation
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideResults();
            }
        });
    }
    
    performSearch(query) {
        if (!this.isLoaded || !query.trim()) {
            this.hideResults();
            return;
        }
        
        const results = this.search(query.toLowerCase(), 8);
        this.displayResults(results, query);
    }
    
    search(query, limit = 10) {
        const terms = query.split(' ').filter(term => term.length > 1);
        if (terms.length === 0) return [];
        
        const scored = this.searchIndex.map(item => ({
            item,
            score: this.calculateScore(item, terms, query)
        })).filter(result => result.score > 0);
        
        // Sort by score (descending) and return top results
        scored.sort((a, b) => b.score - a.score);
        return scored.slice(0, limit).map(result => result.item);
    }
    
    calculateScore(item, terms, fullQuery) {
        let score = 0;
        const titleLower = (item.title || '').toLowerCase();
        const descLower = (item.description || '').toLowerCase();
        const tagsLower = (item.tags || []).map(tag => tag.toLowerCase()).join(' ');
        const keywordsLower = (item.keywords || []).join(' ');
        const codeLower = (item.code_preview || '').toLowerCase();
        
        // Exact phrase match in title (highest score)
        if (titleLower.includes(fullQuery)) score += 100;
        
        // Individual term matches
        for (const term of terms) {
            // Title matches
            if (titleLower.includes(term)) score += 50;
            
            // Tag matches
            if (tagsLower.includes(term)) score += 30;
            
            // Description matches
            if (descLower.includes(term)) score += 20;
            
            // Keywords matches
            if (keywordsLower.includes(term)) score += 15;
            
            // Code content matches
            if (codeLower.includes(term)) score += 10;
            
            // Function name matches
            if ((item.function_name || '').toLowerCase().includes(term)) score += 25;
        }
        
        return score;
    }
    
    displayResults(results, query) {
        if (results.length === 0) {
            this.searchResults.innerHTML = `
                <div class="search-no-results">
                    <p>No results found for "${query}"</p>
                </div>
            `;
        } else {
            const resultsHtml = results.map(result => this.formatResult(result, query)).join('');
            this.searchResults.innerHTML = resultsHtml;
        }
        
        this.searchResults.classList.add('visible');
    }
    
    formatResult(result, query) {
        const title = this.highlightText(result.title || 'Untitled', query);
        const description = this.highlightText((result.description || '').substring(0, 100) + '...', query);
        const tags = (result.tags || []).map(tag => `<span class="tag">${tag}</span>`).join('');
        const date = result.date ? new Date(result.date).toLocaleDateString() : '';
        
        return `
            <div class="search-result-item" onclick="window.location.href='${result.url}'">
                <div class="result-main">
                    <h4 class="result-title">${title}</h4>
                    <p class="result-description">${description}</p>
                    <div class="result-meta">
                        <span class="result-date">${date}</span>
                        <span class="result-function">${result.function_name || ''}</span>
                        <div class="result-tags">${tags}</div>
                    </div>
                </div>
                <div class="result-thumbnail">
                    ${result.plot_image ? `<img src="/${result.collection}/${result.id}/${result.plot_image}" alt="Plot" />` : '📊'}
                </div>
            </div>
        `;
    }
    
    highlightText(text, query) {
        if (!query.trim()) return text;
        
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    hideResults() {
        this.searchResults.classList.remove('visible');
    }
}

// Initialize search when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SnapshotSearch();
});