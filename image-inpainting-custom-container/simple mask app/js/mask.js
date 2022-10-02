//helper function to get the correct mouse position when painting a mask.
function getMousePos(canvas, evt) {
  var rect = canvas.getBoundingClientRect();
  return {
    x: evt.clientX - rect.left,
    y: evt.clientY - rect.top
  };
}

//start with a mask the is fully black, also called by the reset mask button
function fill_black(canvasElement,context){
  //set to draw mode
  context.globalCompositeOperation = 'source-over'
  context.fillStyle = "black";
  context.fillRect(0, 0, canvas.width, canvas.height);
  //reset to erase mode
  context.globalCompositeOperation = 'destination-out';
}

//on page load, the Brush Size, here called lineWidth, is set to 25
var lineWidth = 25;
function drawOnImage(canvasElement,context) {
    //set to erase mode, so that we create the "hole" in the mask when the mouse is down
    context.globalCompositeOperation = 'destination-out';

    let isDrawing;
    canvasElement.onmousedown = (e) => {
      isDrawing = true;
      context.beginPath();
      lineWidth = $('#brush_size').val();
      if (Number.isInteger(Number.parseInt(lineWidth))){
        lineWidth = Number.parseInt(lineWidth);
          if (lineWidth < 0) {lineWidth=0;}
          if (lineWidth > 100) { lineWidth = 100; }
      }
      context.lineWidth = lineWidth;
      context.strokeStyle = "white";//any color but black, to make a shape, to remove out.
      context.lineJoin = "round";
      context.lineCap = "round";
      pos = getMousePos(canvas, e);
      context.moveTo(pos.x, pos.y);
    };
    
    canvasElement.onmousemove = (e) => {
      if (isDrawing) {      
        pos = getMousePos(canvas, e);
        context.lineTo(pos.x, pos.y);
        context.stroke();      
      }
    };
    
    canvasElement.onmouseup = function () {
      isDrawing = false;
      context.closePath();
    };
  }

//when saving the mask,
//change transparent pixels to white, as expected by the SD Inpainting function
const trans_to_white = (canvas,ctx) => {
  //ctx.drawImage(img, 0, 0);
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = imageData.data;
  for (let i = 0; i < data.length; i += 4) {
    if(data[i] == 0 && data[i+1] == 0 & data[i+2] == 0 && data[i+3] == 255){
      //already black, do nothing
    }else{
      //set to white
      data[i] = 255;
      data[i+1] = 255;
      data[i+2] = 255;
      data[i+3] = 255;
    }
  }
  ctx.putImageData(imageData, 0, 0);
};


//load button functionality once the buttons have been loaded onto the page.
  $( document ).ready(function() {

    //enable the upload image button
    const image_input = document.querySelector("#upload_button");
    image_input.addEventListener("change", function() {
      const reader = new FileReader();
      reader.addEventListener("load", () => {
        const uploaded_image = reader.result;
        $("#bg_img").attr("src", uploaded_image);
      });
      reader.readAsDataURL(this.files[0]);
    });
    
    //set up the Canvas element to draw the mask.
    const canvasElement = document.getElementById("canvas");
    const context = canvasElement.getContext("2d");
    fill_black(canvasElement,context);
    drawOnImage(canvasElement,context);

    //enable the mask reset, which is just setting every pixel to black
    $("#reset_button").click(function(){
      fill_black(canvasElement,context);
    })

    //save the mask, first change the transparent pixels to white, as SD Inpainting requires.
    $("#save_button").click(function(){
      trans_to_white(canvasElement,context)
      let downloadLink = document.createElement('a');
      downloadLink.setAttribute('download', 'mask.png');
      let canvas = document.getElementById('canvas');
      canvas.toBlob(function(blob) {
        let url = URL.createObjectURL(blob);
        downloadLink.setAttribute('href', url);
        downloadLink.click();
      });
    })

  });
  