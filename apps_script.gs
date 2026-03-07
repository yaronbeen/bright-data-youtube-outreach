/**
 * YouTube Outreach Email Sender
 *
 * HOW TO USE:
 * 1. Open your Google Sheet with the outreach data
 * 2. Go to Extensions > Apps Script
 * 3. Delete everything in the editor and paste this entire script
 * 4. Click Save (floppy disk icon)
 * 5. Go back to your spreadsheet - you'll see a new "Outreach" menu
 * 6. Use Outreach > Send All Pending Emails to start sending
 *
 * SHEET FORMAT (columns A-F):
 *   A: channel_name
 *   B: email
 *   C: subscribers
 *   D: subject
 *   E: body
 *   F: status (leave empty - script fills this in)
 *
 * Row 1 = headers. Data starts at row 2.
 */

// ── CONFIG ──────────────────────────────────────────────────
const SENDER_NAME = "Yaron Been";           // Your display name
const DELAY_SECONDS = 45;                   // Delay between emails (avoid spam flags)
const SHEET_NAME = "Sheet1";                // Name of the tab with your data
const STATUS_COL = 6;                       // Column F = status
const DRY_RUN = false;                      // Set to true to test without actually sending
// ─────────────────────────────────────────────────────────────

/**
 * Adds "Outreach" menu to the spreadsheet
 */
function onOpen() {
  SpreadsheetApp.getUi().createMenu("Outreach")
    .addItem("Send All Pending Emails", "sendAllEmails")
    .addItem("Send Next 5 Emails", "sendNext5")
    .addItem("Send Test Email to Myself", "sendTestEmail")
    .addSeparator()
    .addItem("Reset All Statuses", "resetStatuses")
    .addItem("Check Gmail Daily Quota", "checkQuota")
    .addToUi();
}

/**
 * Send ALL pending emails (status is empty)
 */
function sendAllEmails() {
  sendEmails(999);
}

/**
 * Send next 5 pending emails only
 */
function sendNext5() {
  sendEmails(5);
}

/**
 * Core sending function
 */
function sendEmails(maxToSend) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sheet) {
    SpreadsheetApp.getUi().alert("Sheet '" + SHEET_NAME + "' not found. Check SHEET_NAME in the script.");
    return;
  }

  var data = sheet.getDataRange().getValues();
  var sentCount = 0;
  var errorCount = 0;
  var skippedCount = 0;

  // Start from row 2 (index 1) to skip headers
  for (var i = 1; i < data.length && sentCount < maxToSend; i++) {
    var row = data[i];
    var channelName = row[0];
    var email = row[1];
    var subscribers = row[2];
    var subject = row[3];
    var body = row[4];
    var status = row[5];

    // Skip if already sent or has any status
    if (status && status.toString().trim() !== "") {
      skippedCount++;
      continue;
    }

    // Skip if no email
    if (!email || email.toString().trim() === "") {
      sheet.getRange(i + 1, STATUS_COL).setValue("NO EMAIL");
      skippedCount++;
      continue;
    }

    // Skip if no body
    if (!body || body.toString().trim() === "") {
      sheet.getRange(i + 1, STATUS_COL).setValue("NO BODY");
      skippedCount++;
      continue;
    }

    try {
      // Convert plain text body to HTML (preserve line breaks)
      var htmlBody = body.toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\n/g, "<br>")
        .replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1">$1</a>')
        .replace(/roaspig\.com/g, '<a href="https://roaspig.com">roaspig.com</a>');

      if (DRY_RUN) {
        Logger.log("DRY RUN - Would send to: " + email + " | Subject: " + subject);
        sheet.getRange(i + 1, STATUS_COL).setValue("DRY RUN - " + new Date().toLocaleDateString());
      } else {
        GmailApp.sendEmail(email.toString().trim(), subject, body, {
          name: SENDER_NAME,
          htmlBody: htmlBody
        });

        sheet.getRange(i + 1, STATUS_COL).setValue("SENT - " + new Date().toLocaleDateString());
        Logger.log("Sent to: " + channelName + " (" + email + ")");
      }

      sentCount++;

      // Delay between emails to avoid spam triggers
      if (sentCount < maxToSend && i < data.length - 1) {
        Utilities.sleep(DELAY_SECONDS * 1000);
      }

    } catch (e) {
      sheet.getRange(i + 1, STATUS_COL).setValue("ERROR: " + e.message);
      Logger.log("Error sending to " + email + ": " + e.message);
      errorCount++;
    }
  }

  // Summary
  var msg = "Done!\n\n" +
    "Sent: " + sentCount + "\n" +
    "Errors: " + errorCount + "\n" +
    "Skipped: " + skippedCount;

  SpreadsheetApp.getUi().alert(msg);
}

/**
 * Send a test email to yourself to preview formatting
 */
function sendTestEmail() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  var data = sheet.getDataRange().getValues();

  // Find first row with data
  if (data.length < 2) {
    SpreadsheetApp.getUi().alert("No data found in sheet.");
    return;
  }

  var row = data[1]; // First data row
  var subject = "[TEST] " + row[3];
  var body = row[4];
  var myEmail = Session.getActiveUser().getEmail();

  var htmlBody = body.toString()
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\n/g, "<br>")
    .replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1">$1</a>')
    .replace(/roaspig\.com/g, '<a href="https://roaspig.com">roaspig.com</a>');

  GmailApp.sendEmail(myEmail, subject, body, {
    name: SENDER_NAME,
    htmlBody: htmlBody
  });

  SpreadsheetApp.getUi().alert("Test email sent to " + myEmail + "\n\nCheck your inbox to preview how it looks.");
}

/**
 * Reset all statuses to empty (careful - allows re-sending)
 */
function resetStatuses() {
  var ui = SpreadsheetApp.getUi();
  var response = ui.alert(
    "Reset All Statuses",
    "This will clear all status values, allowing emails to be sent again.\n\nAre you sure?",
    ui.ButtonSet.YES_NO
  );

  if (response !== ui.Button.YES) return;

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  var lastRow = sheet.getLastRow();

  if (lastRow > 1) {
    sheet.getRange(2, STATUS_COL, lastRow - 1, 1).clearContent();
    ui.alert("All statuses cleared.");
  }
}

/**
 * Check remaining Gmail quota for the day
 */
function checkQuota() {
  var remaining = MailApp.getRemainingDailyQuota();
  SpreadsheetApp.getUi().alert(
    "Gmail Daily Quota\n\n" +
    "Emails remaining today: " + remaining + "\n\n" +
    "Free Gmail: 100/day\n" +
    "Google Workspace: 1,500/day"
  );
}
