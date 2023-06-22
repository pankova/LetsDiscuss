function handleCredentialResponse(response) {
  console.log("Encoded JWT ID token: " + response.credential);

  const data = {
    "token": response.credential
  };
  console.log("handleCredentialResponse response.credential: ", response.credential);
  const body = JSON.stringify(data);
  console.log("handleCredentialResponse body: ", body);

  fetch('/process_data', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: body
  })
    .then(response => {
      if (response.redirected) {
        window.location.href = response.url;
      } else {
        console.error('Error: /process_data there was no redirect with response code ', response.status);
      }
    })
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
