import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

function Navbar() {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          PloGenius
        </Typography>
        <Box>
          <Button color="inherit" component={RouterLink} to="/">Home</Button>
          <Button color="inherit" component={RouterLink} to="/plogrid">PLO Grid</Button>
          <Button color="inherit" component={RouterLink} to="/tree">Tree</Button>
          <Button color="inherit" component={RouterLink} to="/tree_api">Tree API</Button>
          <Button color="inherit" component={RouterLink} to="/game">Game</Button>
          <Button color="inherit" component={RouterLink} to="/about">About</Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;