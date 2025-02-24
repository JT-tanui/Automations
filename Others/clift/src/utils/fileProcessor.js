import * as XLSX from 'xlsx';
import * as pdfjsLib from 'pdfjs-dist';

// Set worker source using local path
pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

// Download worker file to public folder
fetch(`https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`)
  .then(response => response.text())
  .then(worker => {
    // Create a Blob with the worker code
    const blob = new Blob([worker], { type: 'application/javascript' });
    // Create a URL for the blob
    const workerUrl = URL.createObjectURL(blob);
    // Set the worker source
    pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;
  })
  .catch(error => console.error('Failed to load PDF.js worker:', error));

let certificateCounter = 1;

export const generateCertificateNumber = () => {
  const year = new Date().getFullYear();
  const number = String(certificateCounter++).padStart(4, '0');
  return `SIS-${year}-${number}`;
};

export const processExcelFile = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
        const jsonData = XLSX.utils.sheet_to_json(firstSheet);
 
        // Process and validate the data
        const processedData = jsonData.map((row) => ({
          studentName: row.studentName || row['Student Name'] || row.Name || '',
          awardType: row.awardType || row['Award Type'] || row.Award || '',
          certificateNumber: generateCertificateNumber()
        }));

        resolve(processedData);
      } catch (error) {
        reject(new Error('Failed to process Excel file: ' + error.message));
      }
    };

    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsArrayBuffer(file);
  });
};

export const processPDFFile = async (file) => {
  try {
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    const data = [];

    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const textContent = await page.getTextContent();
      const text = textContent.items.map(item => item.str).join(' ');

      // Try to extract name and award type from PDF content
      const nameMatch = text.match(/Name:\s*([^\n]+)/);
      const awardMatch = text.match(/Award:\s*([^\n]+)/);

      if (nameMatch || awardMatch) {
        data.push({
          studentName: nameMatch ? nameMatch[1].trim() : '',
          awardType: awardMatch ? awardMatch[1].trim() : '',
          certificateNumber: generateCertificateNumber()
        });
      }
    }

    return data;
  } catch (error) {
    throw new Error('Failed to process PDF file: ' + error.message);
  }
};

export const processFile = async (file) => {
  const fileType = file.name.split('.').pop().toLowerCase();
  
  switch (fileType) {
    case 'xlsx':
    case 'xls':
      return processExcelFile(file);
    case 'pdf':
      return processPDFFile(file);
    default:
      throw new Error('Unsupported file type');
  }
};