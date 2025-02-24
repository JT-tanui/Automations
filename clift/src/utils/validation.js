export const validateCertificateData = (data) => {
  const errors = {};

  if (!data.studentName) {
    errors.studentName = 'Student name is required';
  } else if (data.studentName.length < 2) {
    errors.studentName = 'Student name must be at least 2 characters long';
  }

  if (!data.awardType) {
    errors.awardType = 'Award type is required';
  }

  if (!data.logo) {
    errors.logo = 'Logo is required';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

export const validateExcelData = (data) => {
  const requiredFields = ['studentName', 'awardType'];
  const errors = [];

  data.forEach((row, index) => {
    const rowErrors = {};
    requiredFields.forEach(field => {
      if (!row[field]) {
        rowErrors[field] = `${field} is required`;
      }
    });

    if (Object.keys(rowErrors).length > 0) {
      errors.push({
        row: index + 1,
        errors: rowErrors
      });
    }
  });

  return {
    isValid: errors.length === 0,
    errors
  };
};