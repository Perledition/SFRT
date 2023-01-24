let animationFrame, recorder
const recordButton = document.getElementById("record-button");
const recordIcon = document.getElementById("record-icon")
const waveform = document.getElementById("waveform");
let recorderState = false;
let chunks = [];

function setupCanvas() {
  canvasCtx = waveform.getContext("2d");
  canvasCtx.strokeStyle = "white";
}

function clearCanvas() {
  canvasCtx = waveform.getContext("2d");
  canvasCtx.clearCanvas();
  // setupCanvas();
}

function animate(analyser) {
  animationFrame = requestAnimationFrame(() => {
    animate(analyser);
  });

  const bufferLength = analyser.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);
  analyser.getByteTimeDomainData(dataArray);

  canvasCtx.clearRect(0, 0, waveform.width, waveform.height);
  canvasCtx.beginPath();

  let sliceWidth = waveform.width * 1.0 / bufferLength;
  let x = 0;

  for (let i = 0; i < bufferLength; i++) {
    let v = dataArray[i] / 128.0;
    let y = v * waveform.height / 2;

    if (i === 0) {
      canvasCtx.moveTo(x, y);
    } else {
      canvasCtx.lineTo(x, y);
    }

    x += sliceWidth;
  }

  canvasCtx.lineTo(waveform.width, waveform.height / 2);
  canvasCtx.stroke();
}

async function toggleRecording() {
  if (recorder && recorder.state === "recording") {
    recorder.stop();
    recordIcon.textContent = "mic";
    recordButton.style.backgroundColor = "#2CC700";
    canvasCtx.clearRect(0, 0, waveform.width, waveform.height);
    // stop the animation
    cancelAnimationFrame(animationFrame);
  } else {
    // start recording
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
    recorder.addEventListener("dataavailable", event => chunks.push(event.data));
    recordIcon.textContent = "stop_circle";
    recordButton.style.backgroundColor = "red";
    setStopEvent();

    // set up the canvas for the waveform animation
    setupCanvas();

    // create an analyser node to visualize the audio
    const context = new AudioContext();
    const source = context.createMediaStreamSource(stream);
    const analyser = context.createAnalyser();
    source.connect(analyser);
    animate(analyser);

    recorder.start();
  }
}
recordButton.addEventListener("click", toggleRecording);

function setStopEvent() {  
  recorder.addEventListener("stop", (event) => {
    console.log("test")
    // const audioBlob = new Blob(chunks, { type: "audio/webm" });
    const fileName = `recording-${new Date().toISOString()}.webm`;
    file = new Blob(chunks)
    chunks = [];
    // Create a new FormData object
    const formData = new FormData();
    // Append the file to the FormData
    formData.append('file', file);
    // Send the file to the API endpoint
    fetch('http://localhost:3004/api/v1/record/voicemail', {
      method: 'POST',
      body: formData
    }).then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    }).then((data) => {
        const tableWrapper = document.getElementById("recording-output");
        console.log(data, tableWrapper)
        tableWrapper.innerHTML = data.extract ?? '';
        console.log(data);
    }).catch((err) => {
      console.log(err);
    });
  });
}