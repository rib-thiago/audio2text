document.addEventListener("DOMContentLoaded", function() {
    // Carregar a transcrição do backend
    fetch('/transcription/')
        .then(response => response.json())
        .then(data => {
            document.getElementById("transcriptionText").value = data.transcription;
        });

    // Enviar a transcrição editada para o backend
    document.getElementById("saveButton").addEventListener("click", function() {
        const transcriptionText = document.getElementById("transcriptionText").value;

        fetch('/save/', {
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
