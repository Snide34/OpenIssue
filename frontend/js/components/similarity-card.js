/**
 * Similarity Card Component
 * Creates a glassmorphic card with similarity bar for duplicate detection
 */

class SimilarityCard {
    constructor(issue1, issue2, similarity) {
        this.issue1 = issue1;
        this.issue2 = issue2;
        this.similarity = similarity;
    }

    getSeverityClass() {
        if (this.similarity >= 85) return 'high';
        if (this.similarity >= 50) return 'medium';
        return 'low';
    }

    getSeverityLabel() {
        if (this.similarity >= 85) return 'Likely Duplicate';
        if (this.similarity >= 50) return 'Possible Duplicate';
        return 'Low Similarity';
    }

    getSeverityColor() {
        if (this.similarity >= 85) return 'text-error';
        if (this.similarity >= 50) return 'text-orange-500';
        return 'text-primary';
    }

    render() {
        const card = document.createElement('div');
        card.className = 'glass-card p-6 group';
        
        card.innerHTML = `
            <div class="flex items-start justify-between mb-4">
                <div class="flex items-center gap-3">
                    <div class="icon-container">
                        <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 0, 'wght' 300;">
                            content_copy
                        </span>
                    </div>
                    <div>
                        <h3 class="font-headline font-bold text-lg text-on-surface">
                            Duplicate Detection
                        </h3>
                        <p class="text-xs text-on-surface-variant font-label">
                            ${this.similarity}% similarity score
                        </p>
                    </div>
                </div>
                <span class="badge ${this.getSeverityClass()}" style="font-size: 0.625rem;">
                    ${this.getSeverityLabel()}
                </span>
            </div>

            <!-- Similarity Bar -->
            <div class="similarity-bar-container mb-4">
                <div class="similarity-bar ${this.getSeverityClass()}" 
                     style="width: 0%; transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);"
                     data-width="${this.similarity}%">
                </div>
            </div>
            <p class="similarity-label ${this.getSeverityColor()}">
                ${this.similarity}% Match - ${this.getSeverityLabel()}
            </p>

            <!-- Issue Comparison -->
            <div class="grid grid-cols-2 gap-4 mt-6 pt-6 border-t border-white/5">
                <div>
                    <p class="text-xs text-on-surface-variant font-label uppercase tracking-wider mb-2">
                        Issue #${this.issue1.number}
                    </p>
                    <h4 class="font-body font-semibold text-sm text-on-surface mb-2 line-clamp-2">
                        ${this.issue1.title}
                    </h4>
                    <div class="flex items-center gap-2 text-xs text-on-surface-variant">
                        <span class="material-symbols-outlined text-xs" style="font-variation-settings: 'FILL' 1, 'wght' 300;">
                            person
                        </span>
                        ${this.issue1.author}
                    </div>
                </div>
                <div>
                    <p class="text-xs text-on-surface-variant font-label uppercase tracking-wider mb-2">
                        Issue #${this.issue2.number}
                    </p>
                    <h4 class="font-body font-semibold text-sm text-on-surface mb-2 line-clamp-2">
                        ${this.issue2.title}
                    </h4>
                    <div class="flex items-center gap-2 text-xs text-on-surface-variant">
                        <span class="material-symbols-outlined text-xs" style="font-variation-settings: 'FILL' 1, 'wght' 300;">
                            person
                        </span>
                        ${this.issue2.author}
                    </div>
                </div>
            </div>

            <!-- Actions -->
            <div class="flex gap-2 mt-6">
                <button class="btn-primary-gradient text-xs flex items-center gap-2">
                    <span class="material-symbols-outlined text-sm" style="font-variation-settings: 'FILL' 0, 'wght' 400;">
                        merge
                    </span>
                    Merge Issues
                </button>
                <button class="btn-secondary text-xs flex items-center gap-2">
                    <span class="material-symbols-outlined text-sm" style="font-variation-settings: 'FILL' 0, 'wght' 400;">
                        visibility
                    </span>
                    View Details
                </button>
            </div>
        `;

        // Animate similarity bar after render
        setTimeout(() => {
            const bar = card.querySelector('.similarity-bar');
            if (bar) {
                bar.style.width = bar.dataset.width;
            }
        }, 100);

        return card;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SimilarityCard;
}
