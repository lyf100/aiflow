import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
import './index.css';

// 挂载 React 应用
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
