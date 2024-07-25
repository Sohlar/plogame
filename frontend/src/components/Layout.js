import React from 'react';

import Navbar from './Navbar';
import { Box, Container, Typography } from '@mui/material';

function Layout({ children }) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Container component="main" sx={{ flexGrow: 1, py: 3 }}>
        {children}
      </Container>
      <Box component="footer" sx={{ py: 3, px: 2, mt: 'auto', backgroundColor: 'background.paper' }}>
        <Typography variant="body2" color="text.secondary" align="center">
          © {new Date().getFullYear()} PloGenius
        </Typography>
      </Box>
    </Box>
  );
}

export default Layout;

