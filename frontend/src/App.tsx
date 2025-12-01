/**
 * Componente principal de la aplicación
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import MovieDetailPage from './pages/MovieDetailPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/movie/:movieId" element={<MovieDetailPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;