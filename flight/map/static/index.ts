function request_ODLC() {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "/odlc");
    xhr.send();
    xhr.responseType = "json";
    xhr.onload = () => {
        if (xhr.readyState == 4 && xhr.status == 200) {
            return xhr.response;
        } else {
            console.log(`Error: ${xhr.status}`);
        }
    };
}

function request_drone() {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "/drone");
    xhr.send();
    xhr.responseType = "json";
    xhr.onload = () => {
        if (xhr.readyState == 4 && xhr.status == 200) {
            return xhr.response;
        } else {
            console.log(`Error: ${xhr.status}`);
        }
    };
}

function convert_locations(odlc, drone_data) {
    // Convert the data into a format that can be used to place objects on the map

}

function place_objects(locations) {
    // Place the objects

}

function update_status() {
    let odlc_data = request_ODLC();
    let drone_data = request_drone();
    let locations = convert_locations(odlc_data, drone_data);
    place_objects(locations);
}
setInterval(update_status, 1000);

function draw() {
    const canvas: HTMLCanvasElement = document.createElement('canvas');
    const ctx: CanvasRenderingContext2D = canvas.getContext('2d')!;
    const img = new Image();
    img.onload = () => {
      ctx.drawImage(img, 0, 0);
    };
    img.src = "backdrop.png";
  }
  
  draw();