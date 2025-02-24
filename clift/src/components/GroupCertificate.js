import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  MenuItem,
  Button,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Box,
  IconButton,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { generateCertificate } from '../utils/certificateGenerator';

const GroupCertificate = () => {
  const [formData, setFormData] = useState({
    awardType: '',
    names: ''
  });

  const [previewData, setPreviewData] = useState([]);
  const [awardTypes, setAwardTypes] = useState([
    'Head Of Year 7 Commendation',
    'Academic Excellence',
    'Outstanding Achievement'
  ]);
  const [newAwardType, setNewAwardType] = useState('');
  const [showAddAward, setShowAddAward] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePreviewList = () => {
    const names = formData.names
      .split('\n')
      .filter(name => name.trim())
      .map(name => ({
        studentName: name.trim(),
        awardType: formData.awardType
      }));
    setPreviewData(names);
  };

  const handleUpdatePreview = (index, field, value) => {
    const updatedData = [...previewData];
    updatedData[index] = {
      ...updatedData[index],
      [field]: value
    };
    setPreviewData(updatedData);
  };

  const handleGenerateGroupCertificates = async () => {
    try {
      for (const entry of previewData) {
        const certificateData = {
          ...entry,
          signatoryName: localStorage.getItem('signatoryName') || '',
          position: localStorage.getItem('position') || '',
          date: new Date().toISOString().split('T')[0],
          certificateNumber: `SIS-${new Date().getFullYear()}-${String(Math.floor(Math.random() * 9999)).padStart(4, '0')}`
        };
        
        await generateCertificate(certificateData);
      }
    } catch (error) {
      console.error('Failed to generate group certificates:', error);
    }
  };

  const handleAddAwardType = () => {
    if (newAwardType) {
      setAwardTypes(prev => [...prev, newAwardType]);
      setNewAwardType('');
      setShowAddAward(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          Group Award Details
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={10}>
            <TextField
              select
              fullWidth
              label="Award Type"
              name="awardType"
              value={formData.awardType}
              onChange={handleChange}
              required
            >
              {awardTypes.map(award => (
                <MenuItem key={award} value={award}>
                  {award}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={2}>
            <IconButton 
              onClick={() => setShowAddAward(true)}
              sx={{ mt: 1 }}
            >
              <AddIcon />
            </IconButton>
          </Grid>
          
          {showAddAward && (
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  label="New Award Type"
                  value={newAwardType}
                  onChange={(e) => setNewAwardType(e.target.value)}
                />
                <Button onClick={handleAddAwardType}>Add</Button>
              </Box>
            </Grid>
          )}

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Enter Names (one per line)"
              name="names"
              value={formData.names}
              onChange={handleChange}
              multiline
              rows={6}
              required
            />
          </Grid>
        </Grid>

        <Box sx={{ mt: 3, mb: 3, display: 'flex', gap: 2 }}>
          <Button 
            variant="contained" 
            onClick={handlePreviewList}
            disabled={!formData.awardType || !formData.names}
          >
            Preview List
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleGenerateGroupCertificates}
            disabled={previewData.length === 0}
          >
            Generate Group Certificates
          </Button>
        </Box>

        {previewData.length > 0 && (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Award Type</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {previewData.map((row, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <TextField
                        fullWidth
                        value={row.studentName}
                        onChange={(e) => handleUpdatePreview(index, 'studentName', e.target.value)}
                      />
                    </TableCell>
                    <TableCell>
                      <TextField
                        fullWidth
                        value={row.awardType}
                        onChange={(e) => handleUpdatePreview(index, 'awardType', e.target.value)}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Container>
  );
};

export default GroupCertificate;