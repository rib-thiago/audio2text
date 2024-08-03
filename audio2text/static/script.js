document.addEventListener("DOMContentLoaded", function() {
    fetch('/transcription/')
        .then(response => response.json())
        .then(data => {
            document.getElementById("transcriptionText").value = data.transcription;
        });

    document.getElementById("saveButton").addEventListener("click", function() {
        const transcriptionText = document.getElementById("transcriptionText").value;

        fetch('/transcription/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ transcription: transcriptionText }),
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        });
    });
});
