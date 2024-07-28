import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import './App.css';
import Layout from './components/Layout.js';
import Home from './components/Home.js';
import About from './components/About.js';
import Game from './components/Game.js';
import Grid from './components/Grid.js';
import Plogrid from './components/plogrid.js';
import Tree from './components/Tree.js';
import Tree_api from './components/Tree_api.js';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#3f51b5',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
    },
    h2: {
      fontWeight: 700,
    },
    h3: {
      fontWeight: 600,
    },
  },
});


function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/plogrid" element={<Plogrid />} />
            <Route path="/grid" element={<Grid />} />
            <Route path="/about" element={<About />} />
            <Route path="/game" element={<Game />} />
            <Route path="/tree" element={<Tree />} />
            <Route path="/tree_api" element={<Tree_api />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
