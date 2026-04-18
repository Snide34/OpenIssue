# OpenIssue Web Application - Complete UI Structure for Google Stitch

## Overview
OpenIssue is an AI-powered GitHub Issue Intelligence platform with a dark-themed Material Design 3 interface. The application features 7 main pages with sophisticated glassmorphism effects, real-time GitHub OAuth integration, and advanced AI-driven issue analysis.

---

## Design System

### Color Palette (Material Design 3 Dark Theme)
```css
Primary: #a3a6ff (Indigo)
Primary Container: #9396ff
Primary Dim: #6063ee
Secondary: #a28efc (Purple)
Secondary Container: #49339d
Tertiary: #ffa5d9 (Pink)
Error: #ff6e84 (Red)
Background: #0a0e13 (Deep Dark Blue)
Surface: #0a0e13
Surface Container: #151a20
On-Surface: #f4f6fe (Off-white)
Outline: #72767c
```

### Typography
- **Headlines**: Manrope (Bold, Extrabold)
- **Body**: Inter (Regular, Medium, Semibold)
- **Labels**: Space Grotesk (Regular, Bold)
- **Code**: Space Grotesk (Monospace alternative)

### Border Radius
- Default: 1rem
- Large: 2rem
- XL: 3rem
- Full: 9999px (Pills)

---

## Page Structure

### 1. Landing Page (`index.html`)
**Purpose**: Authentication entry point

**Layout**:
- Centered glassmorphism card (max-width: 28rem)
- Ambient gradient background blobs (primary/secondary)
- Noise texture overlay

**Components**:
1. **Logo Section**
   - 64px rounded square with gradient (primary → primary-dim)
   - Filled star icon (auto_awesome)
   - "OpenIssue" headline (5xl, extrabold)
   - Tagline: "AI-powered GitHub Issue Intelligence"

2. **Auth Card**
   - Glass panel with backdrop blur
   - "Welcome back" heading
   - "Continue with GitHub" button (gradient, with GitHub SVG icon)
   - Divider with "or" text
   - "Sign in with Email" button (secondary style)
   - Footer links: Privacy, Terms, Docs

3. **Status Indicator**
   - Pulsing tertiary dot
   - "Systems Operational" label

**Interactions**:
- Auto-redirect if session exists
- GitHub OAuth flow initiation
- Hover glow effects on primary button

---

### 2. Dashboard (`pages/dashboard.html`)
**Purpose**: Repository management hub

**Layout**:
- Fixed top navigation
- Full-width header with title and actions
- Responsive grid (1-4 columns based on viewport)

**Components**:

1. **Top Navigation Bar**
   - Logo (left)
   - Nav links: Dashboard (active), Intelligence, Conflicts, Security, Settings
   - Search bar (hidden on mobile)
   - Notification bell icon
   - User avatar (8x8 rounded)

2. **Page Header**
   - "Your GitHub Repositories" (5xl headline with gradient)
   - Subtitle description
   - Refresh button (right-aligned)

3. **Login Prompt** (when not authenticated)
   - Lock icon (64px)
   - "Sign in to see your repositories" heading
   - Description text
   - "Sign in with GitHub" CTA button

4. **Repository Grid**
   - Cards with hover lift effect
   - Each card contains:
     - Folder icon (40px, indigo background)
     - Language + Privacy badges (top-right)
     - Repository name (clickable, xl, bold)
     - Description (2-line clamp)
     - Stats: Stars count, Last updated date
     - Action buttons: "USE" (green), "View" (indigo)

5. **Empty State**
   - Folder-off icon
   - "No repositories found" message

**Interactions**:
- OAuth session check on load
- Repository selection stores to localStorage
- Toast notification on "USE" click
- Auto-redirect to Intelligence page

---

### 3. Intelligence Page (`pages/home.html`)
**Purpose**: AI-powered issue analysis

**Layout**:
- Two-column grid (5/7 split on large screens)
- Left: Input form
- Right: Analysis results (2-column grid)

**Components**:

1. **Repository Banner** (conditional)
   - Green gradient background
   - Check circle icon
   - "Currently Using Repository: {name}"
   - "Change Repo" button

2. **Input Form** (Left Column)
   - Title input field
   - Description textarea (12 rows)
   - "Analyze Issue" button (gradient, with sparkle icon)
   - AI status indicator (pulsing tertiary dot)

3. **Analysis Results** (Right Column)
   
   **Card 1: Classification & Priority**
   - Neural classification label
   - Dynamic icon (bug_report/auto_awesome/help)
   - Classification type (Bug/Feature/Question)
   - Priority pill with colored dot
   - Severity level (Critical/High/Medium/Low)

   **Card 2: Labels**
   - Suggested label pills
   - Confidence percentage

   **Card 3: Similar Issues** (full-width)
   - "Semantic Deduplication" heading
   - Duplicate count
   - DuplicateCluster component (see below)

   **Card 4: Knowledge Engine** (full-width)
   - Intelligence visualization thumbnail
   - AI observation text
   - Repository context note

**Custom Components**:

**DuplicateCluster**:
- Header with icon + count badge
- Stats grid (Definite/Likely/Possible/Related)
- Issue cards with:
  - Issue ID (monospace)
  - Title
  - Description snippet
  - Similarity bar (inline)
  - Action buttons (mark duplicate, view)
- "Show More" expand button

**SimilarityBar**:
- Color-coded progress bar:
  - 90-100%: Red (Definite)
  - 70-89%: Orange (Likely)
  - 50-69%: Yellow (Possible)
  - <50%: Blue (Related)
- Percentage label
- Animated fill effect
- Shimmer overlay

**Interactions**:
- Real-time API call on "Analyze"
- Loading state with spinner
- Dynamic result population
- Toast notifications

---

### 4. Conflicts Page (`pages/conflicts.html`)
**Purpose**: Code merge conflict resolution

**Layout**:
- Full-width header
- Two-column code comparison
- Bottom stats panel

**Components**:

1. **Conflict Header**
   - "AI Conflict Detected" badge (pulsing)
   - PR number
   - "Conflict Analyzer" title (4xl)
   - File path in code block
   - Branch names (colored)
   - Action buttons: "Discard Changes", "Resolve All"

2. **Code Comparison Grid**
   
   **Left Panel: Incoming Changes**
   - Branch label with fork icon
   - Line-numbered code view
   - Green highlights for additions
   - "Accept Incoming" button

   **Right Panel: Current Changes**
   - Branch label with merge icon
   - Line-numbered code view
   - Red highlights with strikethrough for deletions
   - "Keep Current" button

3. **AI Curator Insight** (Bottom Left)
   - Sparkle icon (large, faded)
   - "Curator Insight" heading
   - Analysis text with highlighted keywords
   - Action buttons: "View Dependencies", "Run Test Suite"

4. **Conflict Stats** (Bottom Right)
   - Additions count (large number)
   - Deletions count (large number, red)
   - Progress bar (additions/deletions ratio)
   - Similarity percentage
   - Confidence level

**Interactions**:
- Auto-load sample conflict on mount
- API call for detailed analysis
- Real-time stats update
- Toast notifications for actions

---

### 5. Security Scanner (`pages/security.html`)
**Purpose**: Repository vulnerability scanning

**Layout**:
- Header with shield icon
- Repository selector
- Results grid (1-4 columns)
- Vulnerability list

**Components**:

1. **Repository Selection**
   - Dropdown with all user repos
   - "Scan Repository" button (gradient)
   - Loading spinner state
   - "Not logged in" prompt

2. **Security Score Card**
   - Large score number (0-100)
   - Rating badge (Excellent/Good/Fair/Poor)
   - Color-coded background

3. **Stats Grid** (4 columns)
   - Critical count (red icon)
   - High count (orange icon)
   - Medium count (yellow icon)
   - Files scanned count (blue icon)

4. **Vulnerabilities List**
   - Grouped by severity
   - Each card contains:
     - Severity icon + badge
     - Vulnerability type
     - File path + line number
     - Code snippet (monospace)
     - Recommendation with lightbulb icon

5. **No Vulnerabilities State**
   - Green verified icon (6xl)
   - Success message

**Interactions**:
- Auth check on load
- Repository dropdown population
- Scan API call
- Progressive result display

---

### 6. Settings Page (`pages/settings.html`)
**Purpose**: Account and integration management

**Layout**:
- 3-column grid (2/1 split)
- Main content + sidebar

**Components**:

1. **GitHub Integration Section**
   - GitHub logo (56px, gradient background)
   - "Connect GitHub" heading
   - Status card with colored dot
   - "Connect with GitHub" button (gradient, with SVG icon)
   - "Disconnect" button (red, hidden when not connected)

2. **Status States**:
   - **Loading**: Spinner + "Connecting to GitHub..."
   - **Error**: Error icon + message (red background)
   - **Success**: Check icon + message (green background)
   - **Connected**: Avatar + username display

3. **Repository Selection Section** (conditional)
   - "Select All" button
   - Selected count display
   - Scrollable repo list (max-height: 24rem)
   - Each repo item:
     - Checkbox
     - Repo name (bold)
     - Privacy badge
     - Description
     - Stats (stars, forks, language)
   - "Save Selection" + "Cancel" buttons

4. **Linked Repositories Section** (conditional)
   - "Linked Repositories" heading
   - Refresh button
   - Repo cards with:
     - Name (clickable link)
     - Privacy badge
     - Stars + last updated
     - Unlink button (hover-visible)

5. **Info Sidebar**
   - "Integration Info" heading
   - Permissions description
   - Data security note
   - Documentation link

**Interactions**:
- OAuth flow initiation
- Session verification
- Repository fetching
- Selection management
- Unlink confirmation

---

### 7. Login Page (`pages/login.html`)
**Purpose**: Duplicate of landing page for direct access

**Layout**: Identical to `index.html`

---

## Shared Components

### Navigation Bar
**Fixed top bar** (all pages except landing):
- Height: 64px
- Background: rgba(10, 14, 19, 0.6) with backdrop blur
- Border bottom: 1px white/5%
- Shadow: 0 8px 32px rgba(0,0,0,0.3)

**Contents**:
- Logo (gradient text)
- Nav links (hover: white, active: indigo with bottom border)
- Search bar (desktop only)
- Notification icon
- User avatar

### Footer
**Bottom section** (all pages):
- Border top: 1px white/5%
- Padding: 3rem 2rem
- Three-column flex layout:
  - Logo + tagline
  - Links (Privacy, Security, Changelog, Docs)
  - Status indicator (pulsing dot + "All systems operational")

### Toast Notifications
**Floating alerts**:
- Position: fixed, bottom-right
- Background: Color-coded (green/red/blue)
- Icon + message
- Auto-dismiss after 3 seconds
- Fade-out animation

---

## Custom Web Components

### 1. DuplicateCluster (`duplicate-cluster.js`)
**Purpose**: Visualize similar/duplicate issues

**Props**:
- `issues`: Array of issue objects
- `showActions`: Boolean
- `expandable`: Boolean
- `maxVisible`: Number (default: 5)

**Methods**:
- `render()`: Generate HTML
- `update(newIssues)`: Refresh data
- `markAsDuplicate(issueId)`: API call
- `markAllAsDuplicates()`: Bulk action

### 2. SimilarityBar (`similarity-bar.js`)
**Purpose**: Visual similarity percentage indicator

**Props**:
- `similarity`: Number (0-100)
- `showPercentage`: Boolean
- `showLabel`: Boolean
- `animated`: Boolean
- `size`: String (small/medium/large)

**Methods**:
- `render()`: Generate HTML
- `update(newSimilarity)`: Update value
- `getColorClass()`: Determine color based on value

---

## State Management

### LocalStorage Keys
```javascript
{
  "session_id": "string",           // OAuth session
  "selected_repo": "JSON",          // Current repo object
  "github_connected": "boolean",    // Connection status
  "github_username": "string",      // User's GitHub username
  "github_avatar": "string",        // Avatar URL
  "user_id": "string"               // Generated user ID
}
```

### API Endpoints
```
Base URL: http://localhost:8001

Authentication:
- GET  /auth/login              // Initiate OAuth
- POST /auth/callback           // OAuth callback
- GET  /auth/check              // Verify session
- GET  /auth/repos              // Fetch user repos
- POST /auth/logout             // End session

Analysis:
- POST /analyze/                // Analyze issue

Conflicts:
- POST /conflicts/detailed      // Analyze code conflict

Security:
- POST /security/scan/github    // Scan repository
```

---

## Responsive Breakpoints

```css
Mobile: < 640px
Tablet: 640px - 1024px
Desktop: > 1024px
Wide: > 1536px
```

### Mobile Adaptations
- Navigation: Hamburger menu
- Grid: Single column
- Cards: Full width
- Search: Hidden
- Font sizes: Reduced by 0.125rem

---

## Animation & Effects

### Glassmorphism
```css
background: rgba(33, 38, 46, 0.6);
backdrop-filter: blur(20px);
border: 1px solid rgba(255, 255, 255, 0.05);
```

### Hover Effects
- Cards: `translateY(-4px)` + shadow increase
- Buttons: `scale(0.95)` on active
- Links: Color transition (0.2s ease)

### Loading States
- Spinner: Rotating hourglass icon
- Shimmer: Gradient animation (2s infinite)
- Pulse: Opacity animation (2s ease-in-out)

### Transitions
- Default: `all 0.3s cubic-bezier(0.4, 0, 0.2, 1)`
- Fast: `0.2s ease`
- Slow: `0.6s ease-out`

---

## Accessibility Features

- Semantic HTML5 elements
- ARIA labels on icons
- Keyboard navigation support
- Focus visible states
- Color contrast ratios (WCAG AA)
- Alt text on images
- Screen reader announcements

---

## Browser Support

- Chrome/Edge: 90+
- Firefox: 88+
- Safari: 14+
- Mobile Safari: 14+
- Samsung Internet: 15+

---

## Dependencies

### External Libraries
- **Tailwind CSS**: v3.x (CDN)
- **Google Fonts**: Manrope, Inter, Space Grotesk
- **Material Symbols**: Outlined variant

### Custom Scripts
- `main.js`: Intelligence page logic
- `dashboard.js`: Repository management
- `conflicts.js`: Conflict analyzer
- `security.js`: Security scanner
- `githubAuth.js`: OAuth integration
- `nav.js`: Navigation fixes
- `duplicate-cluster.js`: Custom component
- `similarity-bar.js`: Custom component

### Custom Styles
- `main.css`: Base styles
- `github.css`: GitHub integration styles
- `similarity.css`: Duplicate detection styles

---

## Key User Flows

### 1. First-Time User
1. Land on index.html
2. Click "Continue with GitHub"
3. OAuth redirect → GitHub authorization
4. Callback to dashboard.html with session
5. View repositories
6. Click "USE" on a repo
7. Redirect to home.html (Intelligence)
8. Enter issue details
9. Click "Analyze Issue"
10. View AI-generated results

### 2. Returning User
1. Land on index.html
2. Auto-redirect to dashboard.html (session exists)
3. Navigate to desired page via top nav

### 3. Security Scan
1. Navigate to security.html
2. Select repository from dropdown
3. Click "Scan Repository"
4. View security score + vulnerabilities
5. Review recommendations

---

## Performance Optimizations

- Lazy loading for images
- Debounced search inputs
- Virtualized long lists
- Code splitting by page
- CDN for external resources
- Minified production builds
- Gzip compression

---

## Future Enhancement Areas

1. **Real-time Updates**: WebSocket integration
2. **Offline Support**: Service worker + cache
3. **Dark/Light Toggle**: Theme switcher
4. **Keyboard Shortcuts**: Power user features
5. **Export Functionality**: PDF/CSV reports
6. **Collaboration**: Multi-user sessions
7. **Mobile App**: React Native version
8. **Internationalization**: Multi-language support

---

## File Structure Summary

```
frontend/
├── index.html                    # Landing/Login
├── pages/
│   ├── login.html               # Alt login page
│   ├── home.html                # Intelligence
│   ├── dashboard.html           # Repositories
│   ├── conflicts.html           # Conflict analyzer
│   ├── security.html            # Security scanner
│   └── settings.html            # Settings
├── js/
│   ├── main.js                  # Intelligence logic
│   ├── dashboard.js             # Dashboard logic
│   ├── conflicts.js             # Conflicts logic
│   ├── security.js              # Security logic
│   ├── githubAuth.js            # OAuth logic
│   ├── nav.js                   # Navigation fixes
│   ├── config.js                # Configuration
│   ├── authCheck.js             # Auth verification
│   └── components/
│       ├── duplicate-cluster.js # Duplicate UI
│       └── similarity-bar.js    # Similarity UI
├── styles/
│   └── main.css                 # Base styles
├── css/
│   ├── github.css               # GitHub styles
│   └── similarity.css           # Duplicate styles
└── public/
    └── favicon.ico              # Site icon
```

---

## Design Principles

1. **Clarity**: Information hierarchy is clear
2. **Consistency**: Patterns repeat across pages
3. **Feedback**: Every action has visual response
4. **Efficiency**: Minimal clicks to complete tasks
5. **Aesthetics**: Modern, professional appearance
6. **Accessibility**: Usable by all users
7. **Performance**: Fast load times
8. **Scalability**: Handles large datasets

---

## Notes for Google Stitch

- All pages use Tailwind CSS utility classes
- Color system is Material Design 3 compliant
- Components are modular and reusable
- State management is localStorage-based
- API integration is RESTful
- Authentication is OAuth 2.0 (GitHub)
- UI is fully responsive (mobile-first)
- Animations use CSS transitions/keyframes
- Icons are Material Symbols (Google Fonts)
- Typography is web-safe with fallbacks

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Prepared For**: Google Stitch UI Upgrade
