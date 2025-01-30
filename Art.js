import * as tf from '@tensorflow/tfjs';
import * as tmImage from '@teachablemachine/image';

// URLs del modelo y metadatos
const modelURL = "https://storage.googleapis.com/model-art/Modelo/model.json";
const metadataURL = "https://storage.googleapis.com/model-art/Modelo/metadata.json";

let model, webcam, maxPredictions;

const labels = [
    "Autoretrato", 
    "La Calle de", 
    "Minas sobre", 
    "Popocatepetl"
];

const audioFiles = {
    "Autoretrato": "https://storage.googleapis.com/model-art/Audios/4.wav",
    "La Calle de": "https://storage.googleapis.com/model-art/Audios/1.wav",
    "Minas sobre": "https://storage.googleapis.com/model-art/Audios/8.wav",
    "Popocatepetl": "https://storage.googleapis.com/model-art/Audios/2.wav"
};

async function init() {
    console.log("Cargando modelo...");
    model = await tmImage.load(modelURL, metadataURL);
    maxPredictions = model.getTotalClasses();
    console.log("Modelo cargado correctamente.");

    const flip = true;
    webcam = new tmImage.Webcam(300, 300, flip);
    await webcam.setup();
    await webcam.play();
    document.getElementById("webcam-container").appendChild(webcam.canvas);
    
    window.requestAnimationFrame(loop);
}

async function loop() {
    webcam.update();
    await predict();
    window.requestAnimationFrame(loop);
}

async function predict() {
    const prediction = await model.predict(webcam.canvas);
    let maxProbability = 0;
    let bestMatch = "";

    prediction.forEach((result, index) => {
        if (result.probability > maxProbability) {
            maxProbability = result.probability;
            bestMatch = labels[index];
        }
    });

    console.log(`Predicción: ${bestMatch} con probabilidad ${maxProbability}`);

    if (audioFiles[bestMatch] && maxProbability > 0.7) {
        playAudio(audioFiles[bestMatch]);
    }
}

function playAudio(url) {
    const audio = new Audio(url);
    audio.play()
        .then(() => console.log("Reproduciendo:", url))
        .catch(error => console.error("Error al reproducir audio:", error));
}

window.onload = () => init();
