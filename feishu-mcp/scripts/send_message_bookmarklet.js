// Feishu Message Sender - Run this in your browser console while on Feishu
// Press F12, go to Console tab, paste this code and press Enter

async function sendFeishuMessage(chatName, message) {
    console.log(`Sending to ${chatName}: ${message}`);

    // Find chat by name
    const chatElements = document.querySelectorAll('[class*="chat"], [class*="conversation"]');
    let found = false;

    for (const elem of chatElements) {
        if (elem.innerText.includes(chatName)) {
            elem.click();
            found = true;
            await new Promise(r => setTimeout(r, 1000));
            break;
        }
    }

    if (!found) {
        console.error(`Chat "${chatName}" not found`);
        return;
    }

    // Find input field
    const input = document.querySelector('[contenteditable="true"]');
    if (!input) {
        console.error('Input field not found');
        return;
    }

    // Send message
    input.click();
    await new Promise(r => setTimeout(r, 300));
    input.textContent = message;
    await new Promise(r => setTimeout(r, 300));

    // Press Enter to send
    const enterEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        code: 'Enter',
        keyCode: 13,
        which: 13,
        bubbles: true
    });
    input.dispatchEvent(enterEvent);

    console.log('✓ Message sent!');
}

// Example usage:
// sendFeishuMessage('Hany', 'Testing Feishu Pro automation!');

// Run it now:
sendFeishuMessage('Hany', 'Testing Feishu Pro - working with existing browser!');
