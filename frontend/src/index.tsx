/**
 * Punto de entrada de la aplicación React
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Si quieres medir el rendimiento de tu app, puedes pasar una función
// para registrar resultados (por ejemplo: reportWebVitals(console.log))
// o enviarlos a un endpoint de análisis. Más info: https://bit.ly/CRA-vitals
reportWebVitals();