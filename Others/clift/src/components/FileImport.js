import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Box,
  Alert
} from '@mui/material';
import { processFile } from '../utils/fileProcessor';
import { generateCertificate } from '../utils/certificateGenerator';

const FileImport = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileData, setFileData] = useState([]);
  const [status, setStatus] = useState({ error: null, success: false });
  const [showPreview, setShowPreview] = useState(false);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      handleFileProcess(file);
    }
  };

  const handleFileProcess = async (file) => {
    try {
      setStatus({ loading: true, error: null, success: false });
      const data = await processFile(file);
      setFileData(data);
      setStatus({ loading: false, error: null, success: true });
    } catch (error) {
      setStatus({ loading: false, error: error.message, success: false });
    }
  };

  const handleUpdateData = (index, field, value) => {
    const updatedData = [...fileData];
    updatedData[index] = {
      ...updatedData[index],
      [field]: value
    };
    setFileData(updatedData);
  };

  const handleGenerateCertificates = async () => {
    try {
      for (const entry of fileData) {
        const certificateData = {
          ...entry,
          signatoryName: localStorage.getItem('signatoryName') || '',
          position: localStorage.getItem('position') || '',
          date: new Date().toISOString().split('T')[0]
        };
        await generateCertificate(certificateData);
      }
      setStatus({ success: true, error: null, message: 'Certificates generated successfully' });
    } catch (error) {
      setStatus({ success: false, error: error.message });
    }
  };

  const handlePreview = () => {
    if (fileData.length > 0) {
      setShowPreview(true);
    }
  };

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          File Import
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <TextField
            fullWidth
            value={selectedFile?.name || ''}
            placeholder="No file selected"
            InputProps={{ readOnly: true }}
          />
          <Button
            variant="contained"
            component="label"
          >
            Choose File
            <input
              type="file"
              hidden
              accept=".xlsx,.xls,.pdf"
              onChange={handleFileSelect}
            />
          </Button>
        </Box>

        {status.error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {status.error}
          </Alert>
        )}

        {status.success && status.message && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {status.message}
          </Alert>
        )}

        {fileData.length > 0 && (
          <Box sx={{ display: 'flex', gap: 2, mb: 3, justifyContent: 'center' }}>
            <Button
              variant="contained"
              color="primary"
              onClick={handlePreview}
            >
              Preview List
            </Button>
            <Button
              variant="contained"
              color="secondary"
              onClick={handleGenerateCertificates}
              disabled={!showPreview}
            >
              Generate Certificates
            </Button>
          </Box>
        )}

        {showPreview && fileData.length > 0 && (
          <TableContainer sx={{ mb: 3 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Award Type</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {fileData.map((row, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <TextField
                        fullWidth
                        value={row.studentName}
                        onChange={(e) => handleUpdateData(index, 'studentName', e.target.value)}
                      />
                    </TableCell>
                    <TableCell>
                      <TextField
                        fullWidth
                        value={row.awardType}
                        onChange={(e) => handleUpdateData(index, 'awardType', e.target.value)}
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

export default FileImport;