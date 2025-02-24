// src/components/CertificateTemplate.js
import React from 'react';
import { Paper, Typography } from '@mui/material';

const CertificateTemplate = ({ data }) => {
  return (
    <Paper 
      style={{
        width: '800px',
        height: '600px',
        margin: '20px auto',
        padding: '40px',
        background: '#fff',
        position: 'relative'
      }}
    >
      <div style={{ textAlign: 'center' }}>
        <img 
          src="/assets/logo.png" 
          alt="Logo" 
          style={{ width: '100px', marginBottom: '20px' }}
        />
        <Typography variant="h3">
          Certificate of Achievement
        </Typography>
        <Typography variant="h4">
          {data?.studentName || 'Student Name'}
        </Typography>
        <Typography variant="h5">
          {data?.awardType || 'Award Type'}
        </Typography>
        {/* Add more certificate content */}
      </div>
    </Paper>
  );
};

export default CertificateTemplate;