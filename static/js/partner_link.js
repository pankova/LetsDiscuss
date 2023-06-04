const copyBtn = document.getElementById('copy-btn');
const partnerLink = document.getElementById('partner-link').innerText;

copyBtn.addEventListener('click', () => {

    // Copy the selected text to the clipboard
    navigator.clipboard.writeText(partnerLink)
        .then(() => console.log("Text copied to clipboard"))
        .catch(err => console.error("Failed to copy text: ", err));

    // Show a message to the user indicating that the link has been copied
    alert('Partner link copied to clipboard!');
});