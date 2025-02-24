import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  MenuItem,
  Button,
  Grid,
  Checkbox,
  FormControlLabel,
  IconButton,
  Box,
  Divider
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { generateCertificate } from '../utils/certificateGenerator';

const SingleCertificate = () => {
  const [formData, setFormData] = useState({
    awardType: '',
    studentName: '',
    signatoryName: '',
    position: '',
    awardDate: new Date().toISOString().split('T')[0],
    includeCertNumber: true
  });

  const [awardTypes, setAwardTypes] = useState([
    'Head Of Year 7 Commendation',
    'Academic Excellence',
    'Outstanding Achievement'
  ]);

  const [newAwardType, setNewAwardType] = useState('');
  const [showAddAward, setShowAddAward] = useState(false);

  const handleChange = (e) => {
    const { name, value, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'includeCertNumber' ? checked : value
    }));
  };

  const handleAddAwardType = () => {
    if (newAwardType) {
      setAwardTypes(prev => [...prev, newAwardType]);
      setNewAwardType('');
      setShowAddAward(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await generateCertificate({
        ...formData,
        date: formData.awardDate,
        certificateNumber: formData.includeCertNumber ? undefined : null
      });
    } catch (error) {
      console.error('Certificate generation failed:', error);
    }
  };

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <form onSubmit={handleSubmit}>
          {/* Award Details Section */}
          <Typography variant="h6" gutterBottom>
            Award Details
          </Typography>
          <Grid container spacing={2} sx={{ mb: 4 }}>
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
                label="Student Name"
                name="studentName"
                value={formData.studentName}
                onChange={handleChange}
                required
              />
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          {/* Signatory Details Section */}
          <Typography variant="h6" gutterBottom>
            Signatory Details
          </Typography>
          <Grid container spacing={2} sx={{ mb: 4 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Signatory Name"
                name="signatoryName"
                value={formData.signatoryName}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Position"
                name="position"
                value={formData.position}
                onChange={handleChange}
                required
              />
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          {/* Certificate Options Section */}
          <Typography variant="h6" gutterBottom>
            Certificate Options
          </Typography>
          <Grid container spacing={2} sx={{ mb: 4 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="date"
                label="Award Date"
                name="awardDate"
                value={formData.awardDate}
                onChange={handleChange}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.includeCertNumber}
                    onChange={handleChange}
                    name="includeCertNumber"
                  />
                }
                label="Include Certificate Number"
              />
            </Grid>
          </Grid>

          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            size="large"
          >
            Generate Certificate
          </Button>
        </form>
      </Paper>
    </Container>
  );
};

export default SingleCertificate;