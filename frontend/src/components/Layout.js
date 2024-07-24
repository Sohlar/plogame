import React from 'react';

function Layout({ children }) {
  return (
    <div className="layout">
      <header>
        <h1>PloGenius</h1>
      </header>
      <main>{children}</main>
      <footer>
        <p>&copy; 202 PloGenius</p>
      </footer>
    </div>
  );
}

export default Layout;
