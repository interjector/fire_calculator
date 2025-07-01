// Simple Google Apps Script webhook for feedback
const SHEET_ID = '1liB5nwc0oEBRPu9J1YSO1pNDYHV9_Ofr4nDmSXbJ0z8';

function doGet(e) {
  // If no parameters, just return status
  if (!e.parameter || Object.keys(e.parameter).length === 0) {
    return ContentService.createTextOutput("Webhook is working!");
  }
  
  // Handle feedback submission via GET parameters
  try {
    const data = e.parameter;
    console.log('Feedback received via GET:', data);
    
    // Open sheet
    const sheet = SpreadsheetApp.openById(SHEET_ID).getActiveSheet();
    
    // Add headers if needed
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(['Timestamp', 'Type', 'Feedback', 'Email', 'App']);
    }
    
    // Add data
    sheet.appendRow([
      data.timestamp || new Date().toISOString(),
      data.type || 'Unknown',
      data.feedback || 'No feedback',
      data.email || 'Anonymous',
      data.app || 'Unknown'
    ]);
    
    return ContentService
      .createTextOutput(JSON.stringify({status: 'success'}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    console.error('Error in doGet:', error);
    return ContentService
      .createTextOutput(JSON.stringify({status: 'error', message: error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doPost(e) {
  try {
    console.log('POST received:', e);
    
    // Get data from form parameters
    const data = e.parameter || {};
    
    // Open sheet
    const sheet = SpreadsheetApp.openById(SHEET_ID).getActiveSheet();
    
    // Add headers if needed
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(['Timestamp', 'Type', 'Feedback', 'Email', 'App']);
    }
    
    // Add data
    sheet.appendRow([
      data.timestamp || new Date().toISOString(),
      data.type || 'Unknown',
      data.feedback || 'No feedback',
      data.email || 'Anonymous',
      data.app || 'Unknown'
    ]);
    
    return ContentService
      .createTextOutput(JSON.stringify({status: 'success'}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    console.error('Error:', error);
    return ContentService
      .createTextOutput(JSON.stringify({status: 'error', message: error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}