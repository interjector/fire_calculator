/**
 * Google Apps Script for VIBE FIRE Calculator Feedback
 * 
 * Setup Instructions:
 * 1. Go to script.google.com
 * 2. Create a new project
 * 3. Replace the default code with this script
 * 4. Create a Google Sheet and get its ID from the URL
 * 5. Replace YOUR_SHEET_ID below with your actual sheet ID
 * 6. Deploy as web app (execute as me, access to anyone)
 * 7. Copy the web app URL and add it to your Streamlit secrets
 */

// Replace with your Google Sheet ID
const SHEET_ID = '1liB5nwc0oEBRPu9J1YSO1pNDYHV9_Ofr4nDmSXbJ0z8';

// Test function you can run manually in the script editor
function testFeedbackSubmission() {
  // Simulate a POST request with test data
  const testEvent = {
    postData: {
      contents: JSON.stringify({
        timestamp: new Date().toISOString(),
        type: "Test",
        feedback: "This is a test feedback submission",
        email: "test@example.com",
        app: "VIBE FIRE Calculator"
      })
    },
    parameter: {}
  };
  
  console.log('Running test with simulated data...');
  const result = doPost(testEvent);
  console.log('Test result:', result.getContent());
  return result;
}

// Simple GET test function
function doGet(e) {
  return ContentService
    .createTextOutput("Google Apps Script is working!")
    .setMimeType(ContentService.MimeType.TEXT);
}

function doPost(e) {
  try {
    // Log the incoming request for debugging
    console.log('Received POST request:', e);
    
    // Parse the incoming data (handle both JSON and form data)
    let data;
    if (e.postData.type === 'application/json') {
      data = JSON.parse(e.postData.contents);
    } else {
      // Handle form data
      data = e.parameter;
    }
    console.log('Parsed data:', data);
    
    // Open the spreadsheet
    const sheet = SpreadsheetApp.openById(SHEET_ID).getActiveSheet();
    
    // Add headers if this is the first row
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        'Timestamp',
        'Type', 
        'Feedback',
        'Email',
        'App',
        'User Agent'
      ]);
    }
    
    // Get user agent from headers for additional context
    const userAgent = (e.parameter && e.parameter.HTTP_USER_AGENT) || 'Unknown';
    
    // Append the feedback data
    sheet.appendRow([
      data.timestamp,
      data.type,
      data.feedback,
      data.email,
      data.app,
      userAgent
    ]);
    
    console.log('Successfully added feedback to sheet');
    
    // Optional: Send email notification for critical feedback
    if (data.type === 'Bug Report') {
      // Uncomment and configure if you want email notifications
      // MailApp.sendEmail({
      //   to: 'your-email@gmail.com',
      //   subject: 'New Bug Report - VIBE FIRE Calculator',
      //   body: `New bug report received:\n\nType: ${data.type}\nFeedback: ${data.feedback}\nEmail: ${data.email}\nTimestamp: ${data.timestamp}`
      // });
    }
    
    // Return success with proper headers
    return ContentService
      .createTextOutput(JSON.stringify({status: 'success', message: 'Feedback received'}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    // Log error for debugging
    console.error('Error processing feedback:', error);
    
    return ContentService
      .createTextOutput(JSON.stringify({status: 'error', message: error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  // Handle GET requests (for testing)
  return ContentService
    .createTextOutput('Feedback webhook is working!')
    .setMimeType(ContentService.MimeType.TEXT);
}