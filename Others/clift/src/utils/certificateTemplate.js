export const generateTemplate = (data) => {
  // You can put your full HTML template here with placeholders
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        .certificate {
          width: 1000px;
          margin: 0 auto;
          padding: 20px;
          text-align: center;
          border: 10px solid #0055a4;
        }
        /* Add more styles here */
      </style>
    </head>
    <body>
      <div class="certificate">
        <h1>Certificate of Achievement</h1>
        <p>This is to certify that</p>
        <h2>${data.studentName}</h2>
        <p>has successfully completed</p>
        <h3>${data.awardType}</h3>
        <div class="footer">
          <p>Certificate Number: ${data.certificateNumber}</p>
          <div class="signature">
            <p>${data.signatoryName}</p>
            <p>${data.position}</p>
            <p>${data.date}</p>
          </div>
        </div>
      </div>
    </body>
    </html>
  `;
};