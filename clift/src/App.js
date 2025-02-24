import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import Navbar from './components/Navbar';
import SingleCertificate from './components/SingleCertificate'; 
import GroupCertificate from './components/GroupCertificate';
import FileImport from './components/FileImport';
import theme from './theme';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <BrowserRouter>
        <div className="app">
          <Navbar />
          <Routes>
            <Route path="/" element={<SingleCertificate />} />
            <Route path="/group" element={<GroupCertificate />} />
            <Route path="/import" element={<FileImport />} />
          </Routes>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
