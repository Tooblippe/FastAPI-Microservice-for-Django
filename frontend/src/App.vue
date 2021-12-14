<template>
  <v-app>
    <v-app-bar app color="primary" dark id="top">
      <div class="d-flex align-center">PDF Imager 2</div>
      <v-spacer></v-spacer>
    </v-app-bar>

    <v-main>
      <v-container class="ma-0 pa-0">
        <v-row class="ma-0 pa-0">
          <v-col class="ma-0 pa-0">
            <v-btn @click="clicked">Load Image</v-btn>
          </v-col>
          <v-col class="ma-0 pa-0">
            <canvas
              @mousedown="mg_cords"
              @mouseup="mg_cords_draw"
              ref="canvas"
              class="ma-0 pa-0 green"
            ></canvas>
          </v-col>
          <v-col class="grey ma-0 pa-0">
            <template class="caption" v-for="p in prediction">
              <ol
                :key="p.id"
                class="mt-1 pa-1 green text-h6"
                @click="prediction.splice(p.id, 1)"
              >
                -{{
                  p
                }}
              </ol>
            </template>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
// import HelloWorld from "./components/HelloWorld";

export default {
  name: "App",
  mounted() {
    console.log(this.axios.defaults);
    this.canvas = this.$refs.canvas;
    this.canvas_ctx = this.$refs.canvas.getContext("2d");
  },
  components: {
    // HelloWorld,
  },
  methods: {
    clicked: function () {
      this.axios
        .get("load_image/", {
          responseType: "arraybuffer",
        })
        .then((response) => {
          // console.log(response.data);
          // this.result.status = Buffer.from(response.data, "binary").toString(
          //   "base64"
          // );

          this.new_image =
            "data:image/jpg;base64, " +
            Buffer.from(response.data, "binary").toString("base64");

          console.log(this.canvas);
          let image = new Image();
          image.src = this.new_image;
          this.canvas.height = image.height + 10;
          this.canvas.width = image.width;
          console.log(this.canvas);
          let ctx = this.canvas.getContext("2d");
          ctx.drawImage(image, 10, 10);
        });
    },

    mg_cords(event) {
      console.log("mouse_down");
      let e = document.getElementById("top");
      console.log(e.offsetHeight);
      this.y_start = event.pageY - e.offsetHeight;
      this.x_start = event.pageX - event.currentTarget.offsetLeft;
    },

    mg_cords_draw(event) {
      console.log("mouse up");
      let e = document.getElementById("top");
      this.y_end = event.pageY - e.offsetHeight;
      this.x_end = event.pageX - event.currentTarget.offsetLeft;
      let x1 = this.x_start;
      let y1 = this.y_start;
      let x2 = this.x_end - this.x_start;
      let y2 = this.y_end - this.y_start;

      this.canvas_ctx.beginPath();
      this.canvas_ctx.strokeStyle = "#FF0000";
      this.canvas_ctx.rect(x1, y1, x2, y2);
      this.canvas_ctx.stroke();

      this.axios
        .post("words/", {
          x1: x1 - 5,
          y1: y1,
          width: x1 + x2,
          height: y1 + y2,
        })
        .then((response) => {
          this.prediction.push(
            `${response.data.prediction}-(${x1},${y1},${x1 + x2},${y1 + y2})`
          );
        });
    },
  },
  data: () => ({
    result: { status: "not clicked" },
    new_image: null,
    canvas: "",
    canvas_ctx: "",
    x_start: null,
    y_start: null,
    x_end: null,
    y_end: null,
    dragging: false,
    prediction: [],
  }),
};
</script>
