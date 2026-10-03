export function AppHeader() {
  return (
    <header className="app-header" role="banner">
      <div className="app-header__inner">
        <div className="app-header__brand">
          <a href="/" className="app-header__logo" aria-label="PyDebug home">
            <span className="app-header__logo-mark" aria-hidden="true">
              <svg viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M7.5 1C4.46 1 2 3.46 2 6.5c0 1.74.82 3.29 2.09 4.29L3 13.5l2.5-1.18c.63.22 1.3.18 1.95.18H7.5C10.54 12.5 13 10.04 13 7V6.5C13 3.46 10.54 1 7.5 1z"
                  fill="currentColor"
                  opacity="0.3"
                />
                <path
                  d="M5.5 5.5a1 1 0 1 1 2 0 1 1 0 0 1-2 0zm2.5 0a1 1 0 1 1 2 0 1 1 0 0 1-2 0z"
                  fill="currentColor"
                />
                <path
                  d="M5 8s.5 1.5 2.5 1.5S10 8 10 8"
                  stroke="currentColor"
                  strokeWidth="1.2"
                  strokeLinecap="round"
                />
              </svg>
            </span>
            <span className="app-header__product-name">PyDebug</span>
          </a>
          <div className="app-header__divider" aria-hidden="true" />
          <span className="app-header__subtitle">Python Debugging Assistant</span>
        </div>
        <div className="app-header__meta">
          <span className="app-header__badge">v0.1</span>
        </div>
      </div>
    </header>
  );
}
