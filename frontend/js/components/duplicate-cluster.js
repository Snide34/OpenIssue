/**
 * Duplicate Cluster View Component
 * Groups and visualizes related/duplicate issues
 */

class DuplicateCluster {
    constructor(container, issues, options = {}) {
        this.container = container;
        this.issues = issues || [];
        this.options = {
            showActions: options.showActions !== false,
            expandable: options.expandable !== false,
            maxVisible: options.maxVisible || 5,
            ...options
        };
        
        this.expanded = false;
        this.render();
    }

    render() {
        if (this.issues.length === 0) {
            this.renderEmpty();
            return;
        }

        // Sort by similarity (highest first)
        const sortedIssues = [...this.issues].sort((a, b) => 
            (b.similarity_score || 0) - (a.similarity_score || 0)
        );

        // Group by similarity level
        const groups = {
            definite: sortedIssues.filter(i => (i.similarity_score || 0) * 100 >= 90),
            likely: sortedIssues.filter(i => (i.similarity_score || 0) * 100 >= 70 && (i.similarity_score || 0) * 100 < 90),
            possible: sortedIssues.filter(i => (i.similarity_score || 0) * 100 >= 50 && (i.similarity_score || 0) * 100 < 70),
            related: sortedIssues.filter(i => (i.similarity_score || 0) * 100 < 50)
        };

        const html = `
            <div class="duplicate-cluster">
                ${this.renderHeader(sortedIssues)}
                ${this.renderStats(groups)}
                ${this.renderIssueList(sortedIssues)}
            </div>
        `;

        if (typeof this.container === 'string') {
            document.querySelector(this.container).innerHTML = html;
        } else {
            this.container.innerHTML = html;
        }

        this.attachEventListeners();
    }

    renderHeader(issues) {
        const highestSimilarity = issues.length > 0 ? (issues[0].similarity_score || 0) * 100 : 0;
        const icon = highestSimilarity >= 90 ? 'content_copy' : 
                     highestSimilarity >= 70 ? 'link' : 'compare_arrows';
        
        return `
            <div class="duplicate-cluster-header">
                <div class="duplicate-cluster-title">
                    <span class="material-symbols-outlined">${icon}</span>
                    <h3>Similar Issues Found</h3>
                    <span class="duplicate-count-badge">${issues.length}</span>
                </div>
                ${this.options.showActions ? `
                    <div class="duplicate-cluster-actions">
                        <button class="btn-secondary btn-sm mark-all-duplicates">
                            <span class="material-symbols-outlined">done_all</span>
                            Mark All as Duplicates
                        </button>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderStats(groups) {
        return `
            <div class="duplicate-stats">
                ${groups.definite.length > 0 ? `
                    <div class="stat-item stat-definite">
                        <span class="stat-count">${groups.definite.length}</span>
                        <span class="stat-label">Definite</span>
                    </div>
                ` : ''}
                ${groups.likely.length > 0 ? `
                    <div class="stat-item stat-likely">
                        <span class="stat-count">${groups.likely.length}</span>
                        <span class="stat-label">Likely</span>
                    </div>
                ` : ''}
                ${groups.possible.length > 0 ? `
                    <div class="stat-item stat-possible">
                        <span class="stat-count">${groups.possible.length}</span>
                        <span class="stat-label">Possible</span>
                    </div>
                ` : ''}
                ${groups.related.length > 0 ? `
                    <div class="stat-item stat-related">
                        <span class="stat-count">${groups.related.length}</span>
                        <span class="stat-label">Related</span>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderIssueList(issues) {
        const visibleIssues = this.expanded ? issues : issues.slice(0, this.options.maxVisible);
        const hasMore = issues.length > this.options.maxVisible;

        return `
            <div class="duplicate-issue-list">
                ${visibleIssues.map((issue, index) => this.renderIssueCard(issue, index)).join('')}
                
                ${hasMore && this.options.expandable ? `
                    <button class="expand-duplicates-btn">
                        <span class="material-symbols-outlined">
                            ${this.expanded ? 'expand_less' : 'expand_more'}
                        </span>
                        ${this.expanded ? 'Show Less' : `Show ${issues.length - this.options.maxVisible} More`}
                    </button>
                ` : ''}
            </div>
        `;
    }

    renderIssueCard(issue, index) {
        const similarity = (issue.similarity_score || 0) * 100;
        const issueId = issue.id ? issue.id.substring(0, 8) : `#${1000 + index}`;
        const title = issue.title || 'Untitled Issue';
        const description = issue.description || '';
        const truncatedDesc = description.length > 100 ? description.substring(0, 100) + '...' : description;

        return `
            <div class="duplicate-issue-card" data-issue-id="${issue.id || index}">
                <div class="duplicate-issue-main">
                    <div class="duplicate-issue-header">
                        <span class="issue-id">${issueId}</span>
                        <h4 class="issue-title">${title}</h4>
                    </div>
                    ${truncatedDesc ? `
                        <p class="issue-description">${truncatedDesc}</p>
                    ` : ''}
                    <div class="similarity-bar-wrapper">
                        <div class="similarity-bar-inline" data-similarity="${similarity}"></div>
                    </div>
                </div>
                ${this.options.showActions ? `
                    <div class="duplicate-issue-actions">
                        <button class="btn-icon mark-duplicate" title="Mark as duplicate">
                            <span class="material-symbols-outlined">content_copy</span>
                        </button>
                        <button class="btn-icon view-issue" title="View issue">
                            <span class="material-symbols-outlined">open_in_new</span>
                        </button>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderEmpty() {
        const html = `
            <div class="duplicate-cluster-empty">
                <span class="material-symbols-outlined">search_off</span>
                <p>No similar issues found</p>
                <span class="empty-subtitle">This appears to be a unique issue</span>
            </div>
        `;

        if (typeof this.container === 'string') {
            document.querySelector(this.container).innerHTML = html;
        } else {
            this.container.innerHTML = html;
        }
    }

    attachEventListeners() {
        const container = typeof this.container === 'string' ? 
            document.querySelector(this.container) : this.container;

        // Expand/collapse button
        const expandBtn = container.querySelector('.expand-duplicates-btn');
        if (expandBtn) {
            expandBtn.addEventListener('click', () => {
                this.expanded = !this.expanded;
                this.render();
            });
        }

        // Initialize similarity bars
        container.querySelectorAll('.similarity-bar-inline').forEach(el => {
            const similarity = parseFloat(el.dataset.similarity);
            new SimilarityBar(el, similarity, {
                showLabel: false,
                showPercentage: true,
                size: 'small',
                animated: true
            });
        });

        // Mark as duplicate buttons
        container.querySelectorAll('.mark-duplicate').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const card = btn.closest('.duplicate-issue-card');
                const issueId = card.dataset.issueId;
                this.markAsDuplicate(issueId);
            });
        });

        // View issue buttons
        container.querySelectorAll('.view-issue').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const card = btn.closest('.duplicate-issue-card');
                const issueId = card.dataset.issueId;
                this.viewIssue(issueId);
            });
        });

        // Mark all button
        const markAllBtn = container.querySelector('.mark-all-duplicates');
        if (markAllBtn) {
            markAllBtn.addEventListener('click', () => {
                this.markAllAsDuplicates();
            });
        }
    }

    markAsDuplicate(issueId) {
        console.log('Marking as duplicate:', issueId);
        // TODO: Implement API call
        this.showNotification(`Issue ${issueId} marked as duplicate`, 'success');
    }

    markAllAsDuplicates() {
        console.log('Marking all as duplicates');
        // TODO: Implement API call
        this.showNotification(`${this.issues.length} issues marked as duplicates`, 'success');
    }

    viewIssue(issueId) {
        console.log('Viewing issue:', issueId);
        // TODO: Navigate to issue detail page
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        const bgColor = type === 'success' ? 'bg-green-600' : 'bg-blue-600';
        notification.className = `fixed top-6 right-6 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-3 z-50`;
        notification.innerHTML = `
            <span class="material-symbols-outlined">check_circle</span>
            <span>${message}</span>
        `;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    update(newIssues) {
        this.issues = newIssues || [];
        this.render();
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DuplicateCluster;
}
