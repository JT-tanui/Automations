import html2pdf from 'html2pdf.js';
import { validateCertificateData } from './validation';
import { generateCertificateNumber } from './fileProcessor';

export const generateCertificate = async (data) => {
  // Validate the data
  const validation = validateCertificateData(data);
  if (!validation.isValid) {
    throw new Error(JSON.stringify(validation.errors));
  }

  // Add certificate number if not present
  const certificateData = {
    ...data,
    certificateNumber: data.certificateNumber || generateCertificateNumber()
  };

  // Define styles inline to ensure they are included in the PDF
  const template = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Sandford International School Certificate</title>
        <style>
            body {
                margin: 0;
                padding: 20px;
                font-family: Arial, sans-serif;
                background-color: white;
            }
            .certificate {
                width: 100%;
                max-width: 800px;
                margin: 0 auto;
                text-align: center;
            }
            .school-name {
                font-size: 48px;
                color: #0066ff;
                margin-bottom: 10px;
            }
            .subtitle {
                font-size: 36px;
                color: #0066ff;
                margin-bottom: 30px;
            }
            .logo {
                width: 150px;
                margin: 20px auto;
            }
            .logo img {
                width: 100%;
                height: auto;
            }
            .awarded-text {
                font-size: 24px;
                color: #0066ff;
                margin: 20px 0;
            }
            .student-name {
                font-size: 36px;
                margin: 20px 0;
                font-weight: bold;
            }
            .award-text {
                font-size: 24px;
                color: #0066ff;
                margin: 20px auto;
                max-width: 80%;
                line-height: 1.4;
            }
            .signature-section {
                display: flex;
                justify-content: space-between;
                margin-top: 60px;
                padding: 0 40px;
            }
            .signature {
                text-align: left;
            }
            .signature-line {
                width: 200px;
                border-top: 1px solid #0066ff;
                margin-bottom: 5px;
            }
            .signatory-name {
                color: #0066ff;
                font-weight: 500;
            }
            .position {
                color: #0066ff;
                font-size: 12px;
                font-weight: 400;
            }
            .date {
                text-align: right;
                margin-top: 20px;
            }
            .cert-number {
                position: absolute;
                top: 20px;
                right: 20px;
                font-size: 14px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="certificate">
            <div class="cert-number">SIS-${certificateData.certificateNumber}</div>
            <h1 class="school-name">Sandford International School</h1>
            <h2 class="subtitle">Head Of Year 7 Commendation</h2>
            <div class="logo">
                <img src="/assets/logo.png" alt="School Logo">
            </div>
            <p class="awarded-text">This Certificate is Awarded to</p>
            <div class="student-name">${certificateData.studentName}</div>
            <p class="award-text">
                Awarded for <br>${certificateData.awardType}
            </p>
            <div class="signature-section">
                <div class="signature">
                    <div class="signature-line"></div>
                    <div class="signatory-name">${certificateData.signatoryName}</div>
                    <div class="position">${certificateData.position}</div>
                </div>
                <div class="date">issued on ${certificateData.date}</div>
            </div>
        </div>
    </body>
    </html>
  `;

  const options = {
    margin: 0,
    filename: `${certificateData.studentName}_certificate.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { 
      scale: 2,
      useCORS: true,
      logging: true,
      allowTaint: true
    },
    jsPDF: { 
      unit: 'mm', 
      format: 'a4', 
      orientation: 'landscape'
    }
  };

  try {
    await html2pdf().from(template).set(options).save();
    return certificateData.certificateNumber;
  } catch (error) {
    console.error('Certificate generation error:', error);
    throw new Error('Failed to generate certificate: ' + error.message);
  }
};