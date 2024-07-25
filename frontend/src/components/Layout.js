import React from 'react';

function Layout({ children }) {
  return (
    <div className="layout">
      <header>
        <h1>PloGenius</h1>
      </header>
      <main>{children}</main>
      <footer>
        <p>&copy; 2024 PloGenius</p>
      </footer>
    </div>
  );
}

export default Layout;
