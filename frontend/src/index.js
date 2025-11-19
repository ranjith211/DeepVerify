import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import Admin from './Admin';

const root = ReactDOM.createRoot(document.getElementById('root'));

// Simple routing based on URL path
const path = window.location.pathname;

root.render(
  <React.StrictMode>
    {path === '/admin' ? <Admin /> : <App />}
  </React.StrictMode>
);
