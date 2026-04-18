/**
 * Similarity Progress Bar Component
 * Visual % match indicator for duplicate detection
 * 
 * Color coding:
 * - 90-100%: RED (Definite duplicate)
 * - 70-89%: ORANGE (Likely duplicate)
 * - 50-69%: YELLOW (Possibly related)
 * - <50%: BLUE (Loosely related)
 */

class SimilarityBar {
    constructor(container, similarity, options = {}) {
        this.container = container;
        this.similarity = Math.min(100, Math.max(0, similarity)); // Clamp 0-100
        this.options = {
            showPercentage: options.showPercentage !== false,
            showLabel: options.showLabel !== false,
            animated: options.animated !== false,
            size: options.size || 'medium', // small, medium, large
            ...options
        };
        
        this.render();
    }

    getColorClass() {
        if (this.similarity >= 90) return 'duplicate-definite';
        if (this.similarity >= 70) return 'duplicate-likely';
        if (this.similarity >= 50) return 'duplicate-possible';
        return 'duplicate-related';
    }

    getColorHex() {
        if (this.similarity >= 90) return '#ef4444'; // red-500
        if (this.similarity >= 70) return '#f97316'; // orange-500
        if (this.similarity >= 50) return '#eab308'; // yellow-500
        return '#3b82f6'; // blue-500
    }

    getLabel() {
        if (this.similarity >= 90) return 'Definite Duplicate';
        if (this.similarity >= 70) return 'Likely Duplicate';
        if (this.similarity >= 50) return 'Possibly Related';
        return 'Loosely Related';
    }

    getIcon() {
        if (this.similarity >= 90) return 'content_copy'; // duplicate icon
        if (this.similarity >= 70) return 'link'; // link icon
        if (this.similarity >= 50) return 'compare_arrows'; // compare icon
        return 'info'; // info icon
    }

    render() {
        const colorClass = this.getColorClass();
        const colorHex = this.getColorHex();
        const label = this.getLabel();
        const icon = this.getIcon();
        const sizeClass = `similarity-bar-${this.options.size}`;
        const animatedClass = this.options.animated ? 'similarity-bar-animated' : '';

        const html = `
            <div class="similarity-bar-container ${sizeClass}">
                ${this.options.showLabel ? `
                    <div class="similarity-bar-header">
                        <div class="similarity-bar-label">
                            <span class="material-symbols-outlined similarity-icon ${colorClass}">${icon}</span>
                            <span class="similarity-label-text ${colorClass}">${label}</span>
                        </div>
                        ${this.options.showPercentage ? `
                            <span class="similarity-percentage ${colorClass}">${this.similarity.toFixed(0)}%</span>
                        ` : ''}
                    </div>
                ` : ''}
                
                <div class="similarity-bar-track">
                    <div class="similarity-bar-fill ${colorClass} ${animatedClass}" 
                         style="width: ${this.similarity}%; background-color: ${colorHex};"
                         data-similarity="${this.similarity}">
                        ${!this.options.showLabel && this.options.showPercentage ? `
                            <span class="similarity-bar-inline-text">${this.similarity.toFixed(0)}%</span>
                        ` : ''}
                    </div>
                </div>
                
                ${this.options.showConfidence ? `
                    <div class="similarity-confidence">
                        <span class="material-symbols-outlined">verified</span>
                        <span>${this.options.confidence || 95}% confidence</span>
                    </div>
                ` : ''}
            </div>
        `;

        if (typeof this.container === 'string') {
            document.querySelector(this.container).innerHTML = html;
        } else {
            this.container.innerHTML = html;
        }

        // Trigger animation
        if (this.options.animated) {
            setTimeout(() => {
                const fill = this.container.querySelector('.similarity-bar-fill');
                if (fill) fill.classList.add('similarity-bar-animate-in');
            }, 50);
        }
    }

    update(newSimilarity) {
        this.similarity = Math.min(100, Math.max(0, newSimilarity));
        this.render();
    }

    static createInline(similarity, options = {}) {
        const container = document.createElement('div');
        new SimilarityBar(container, similarity, options);
        return container;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SimilarityBar;
}
