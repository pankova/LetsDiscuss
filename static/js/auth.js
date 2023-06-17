function handleCredentialResponse(response) {
  console.log("Encoded JWT ID token: " + response.credential);

  const data = {
    'token': response.credential
  };

  fetch('/process_data', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => {
      console.error('Error: /process_data ', error);
    });
}

window.onload = function () {

  // Make a request to the API endpoint
  fetch('/api/client-id')
    .then(response => response.json())
    .then(data => {
      var clientId = data.client_id;

      google.accounts.id.initialize({
        client_id: clientId,
        callback: handleCredentialResponse
      });

      google.accounts.id.renderButton(
        document.getElementById("buttonDiv"),
        { theme: "outline", size: "large" }  // Customization attributes
      );

      google.accounts.id.prompt(); // Also display the One Tap dialog
    })
    .catch(error => {
      console.error('Error: /api/client-id ', error);
    });
}
