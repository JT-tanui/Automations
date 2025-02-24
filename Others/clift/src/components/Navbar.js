import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Navbar = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Certificate Generator
        </Typography>
        <Box>
          <Button 
            color="inherit" 
            component={RouterLink} 
            to="/"
          >
            Single Certificate
          </Button>
          <Button 
            color="inherit" 
            component={RouterLink} 
            to="/group"
          >
            Group Certificates
          </Button>
          <Button 
            color="inherit" 
            component={RouterLink} 
            to="/import"
          >
            Import File
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;