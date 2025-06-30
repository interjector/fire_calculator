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
const SHEET_ID = 'YOUR_SHEET_ID_HERE';

function doPost(e) {
  try {
    // Parse the incoming data
    const data = JSON.parse(e.postData.contents);
    
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
    const userAgent = e.parameter.HTTP_USER_AGENT || 'Unknown';
    
    // Append the feedback data
    sheet.appendRow([
      data.timestamp,
      data.type,
      data.feedback,
      data.email,
      data.app,
      userAgent
    ]);
    
    // Optional: Send email notification for critical feedback
    if (data.type === 'Bug Report') {
      // Uncomment and configure if you want email notifications
      // MailApp.sendEmail({
      //   to: 'your-email@gmail.com',
      //   subject: 'New Bug Report - VIBE FIRE Calculator',
      //   body: `New bug report received:\n\nType: ${data.type}\nFeedback: ${data.feedback}\nEmail: ${data.email}\nTimestamp: ${data.timestamp}`
      // });
    }
    
    return ContentService
      .createTextOutput('Success')
      .setMimeType(ContentService.MimeType.TEXT);
      
  } catch (error) {
    // Log error for debugging
    console.error('Error processing feedback:', error);
    
    return ContentService
      .createTextOutput('Error: ' + error.toString())
      .setMimeType(ContentService.MimeType.TEXT);
  }
}

function doGet(e) {
  // Handle GET requests (for testing)
  return ContentService
    .createTextOutput('Feedback webhook is working!')
    .setMimeType(ContentService.MimeType.TEXT);
}