export default {
    template: `
    <div>
        <div :id="getPdfContentId()" style="display: none;">
            <canvas :id="getPdfCanvasId()" width="100%"></canvas>
            <div :id="getTextLayerId()" class="textLayer"></div>
        </div>
    </div>
    `,
    props: {
      path: String,
    },
    data() {
      return {
        id: this.uuidv4(),
        num_pages: 1,
        current_page: 1,
        pdf: null,
        is_rendering: false,
      };
    },
    mounted(){
      var self = this;
      this.$nextTick(function () {
        self.canvas = $("#" + self.getPdfCanvasId()).get(0);
        self.canvas_ctx = self.canvas.getContext('2d');
        this._loadPdf();
      })
    },
    created() {
      window.addEventListener("resize", this._showPage);
    },
    methods: {
      /*
       * IDs for multi component support
       */
      uuidv4() {
        return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, c =>
          (+c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> +c / 4).toString(16)
        );
      },      
      getPdfContentId(){
        return "pdf-contents-" + this.id;
      },
      getPdfCanvasId(){
        return "pdf-canvas-" + this.id;
      },
      getTextLayerId(){
        return "text-layer-" + this.id;
      },

      open_page(current_page){
        var old_current_page = this.current_page;

        this.current_page = current_page;
        this.current_page = Math.max(this.current_page, 1);
        this.current_page = Math.min(this.current_page, this.num_pages);

        if (this.current_page != old_current_page) {
          this._showPage();
        } else {
          this.$emit("change_current_page", this.current_page);
        }
      },

      refresh() {
        this._showPage();
      },
      

      /*
       * Private functions
       */
      _loadPdf() {
        var self = this;
        PDFJS.getDocument({ url: this.path }).promise.then(function (pdf_doc) {
            self.pdf_doc = pdf_doc;
            self.num_pages = self.pdf_doc.numPages;
            self.current_page = 1;
            self.$emit("change_num_pages", self.num_pages);
            self.$emit("change_current_page", self.current_page);

            $("#" + self.getPdfContentId()).show();
            self._showPage();

            var text_layer = document.getElementById(self.getPdfContentId());
            text_layer.addEventListener('selectstart', () => {
              $(document).one('mouseup', function() {
                var selection = this.getSelection();
                self.$emit("change_selected_text", selection.toString());
              });
            });

        }).catch(function (error) {
            alert(error.message);
        });
      },

      _showPage() {
        var self = this;
        if (self.is_rendering) {
            console.log("Already rendering. Skipping page " + self.current_page + "...");
            return;
        }
        
        self.is_rendering = true;
        self.$emit("change_is_rendering", self.is_rendering);
      
        // Fetch the page
        self.pdf_doc.getPage(self.current_page).then(function (page) {
            var width = $("#" + self.getPdfContentId()).width();

            self.canvas.width = width;

            let viewport = page.getViewport({
                scale: 1,
            });
      
            let scale = self.canvas.width / viewport.width;
            viewport = page.getViewport({
                scale: scale
            });
      
            self.canvas.height = viewport.height;
            var renderContext = {
                canvasContext: self.canvas_ctx,
                viewport: viewport
            };
      
            page.render(renderContext).promise.then(function () {
                return page.getTextContent();
            }).then(function (textContent) {
                var canvas_offset = $("#" + self.getPdfCanvasId()).offset();
                var cumulative_offset = { left: 0, top: 0 };

                // Traverse all ancestor elements with position styles affecting layout
                $("#" + self.getPdfContentId()).parents().each(function () {
                    var element = $(this);
                    var position = element.css("position");
                    if (position === "relative" || position === "absolute" || position === "fixed") {
                        var element_offset = element.offset();
                        if (element_offset) {
                            cumulative_offset.left += element_offset.left;
                            cumulative_offset.top += element_offset.top;
                        }
                    }
                });

                $("#" + self.getTextLayerId()).html('');
                document.getElementById(self.getTextLayerId()).style.setProperty('--scale-factor', viewport.scale);

                // Adjust text layer position relative to cumulative q-card offsets
                $("#" + self.getTextLayerId()).css({ 
                    left: (canvas_offset.left - cumulative_offset.left) + 'px', 
                    top: (canvas_offset.top - cumulative_offset.top) + 'px' 
                });

                PDFJS.renderTextLayer({
                    textContentSource: textContent,
                    container: $("#" + self.getTextLayerId()).get(0),
                    viewport: viewport,
                    textDivs: []
                });

            }).finally(function () {
                self.is_rendering = false;
                self.$emit("change_is_rendering", self.is_rendering);
                self.$emit("change_current_page", self.current_page);
            });
        });
      }
    },
  };