/* Namespace global seguro */
window.DanielCreuxVideo = class {

    constructor(selector, options = {}) {
        this.root = (typeof selector === "string")
            ? document.querySelector(selector)
            : selector;

        if (!this.root) {
            console.error("danielcreux|video: root element not found");
            return;
        }

        this.videoSrc = options.src || this.root.dataset.danielcreuxVideo;
        this.buildStructure();
        this.attachEvents();
        this.setupAutoHide();

        if (this.videoSrc) {
            this.video.src = this.videoSrc;
        }

        if (options.resolutionsJson) {
            this.loadResolutions(options.resolutionsJson);
        }
    }

    /* --------------------------
        CREAR ESTRUCTURA VISUAL
    ----------------------------*/
    buildStructure() {
        this.root.classList.add("danielcreux-video-contenedor");

        this.video = document.createElement("video");
        this.video.controls = false;

        this.controls = document.createElement("div");
        this.controls.className = "danielcreux-video-controles";

        this.controls.innerHTML = `
        <button data-act="rebobinar">⏮️</button>
        <button data-act="menos10">-10</button>
        <button data-act="play">▶️</button>
        <button data-act="pause">⏸️</button>
        <button data-act="mas10">+10</button>

        <input type="range" min="0" max="1" step="0.02" value="1"
               class="danielcreux-video-volumen" data-act="volumen">

        <div class="danielcreux-video-tiempo" data-act="tiempo">00:00</div>

        <select data-act="resoluciones"></select>

        <button data-act="fullscreen">⛶</button>
        <button data-act="pip">🗔</button>
        `;

        this.root.appendChild(this.video);
        this.root.appendChild(this.controls);

        this.btns = this.controls.querySelectorAll("button");
        this.volumen = this.controls.querySelector("[data-act=volumen]");
        this.tiempoDiv = this.controls.querySelector("[data-act=tiempo]");
        this.resolSelect = this.controls.querySelector("[data-act=resoluciones]");
        this.fullscreenBtn = this.controls.querySelector("[data-act=fullscreen]");
        this.pipBtn = this.controls.querySelector("[data-act=pip]");
    }

    /* --------------------------
        ASIGNAR EVENTOS
    ----------------------------*/
    attachEvents() {
        this.btns.forEach(btn => {
            btn.onclick = async () => {
                let action = btn.dataset.act;

                switch(action){
                    case "rebobinar": this.video.currentTime = 0; break;
                    case "menos10": this.video.currentTime -= 10; break;
                    case "play": this.video.play(); break;
                    case "pause": this.video.pause(); break;
                    case "mas10": this.video.currentTime += 10; break;
                    case "fullscreen":
                        if (!document.fullscreenElement) {
                            await this.root.requestFullscreen();
                        } else {
                            await document.exitFullscreen();
                        }
                        break;
                    case "pip":
                        try {
                            if (document.pictureInPictureElement) {
                                await document.exitPictureInPicture();
                            } else {
                                await this.video.requestPictureInPicture();
                            }
                        } catch(e) {
                            console.error("Picture-in-Picture no soportado", e);
                        }
                        break;
                }
            };
        });

        this.volumen.oninput = () => { this.video.volume = this.volumen.value; };

        let lastSecond = -1;
        this.video.addEventListener("timeupdate", () => {
            let s = Math.floor(this.video.currentTime);
            if (s !== lastSecond) {
                lastSecond = s;
                this.tiempoDiv.textContent = this.formatTime(s);
            }
        });

        this.resolSelect.onchange = async () => {
            let base = this.resolSelect.value;
            const variantes = [
                base,
                base.replace(/\.MP4$/i, ".mp4"),
                base.replace(/\.mp4$/i, ".MP4")
            ];

            let newSrc = null;
            for (const v of variantes) {
                try {
                    const test = await fetch(v, { method: "HEAD" });
                    if (test.ok) { newSrc = v; break; }
                } catch (e) {}
            }

            if (!newSrc) {
                console.error("Ninguna variante válida encontrada:", base);
                alert("Esa resolución no existe en el servidor.");
                return;
            }

            let t = this.video.currentTime;
            let paused = this.video.paused;
            this.video.src = newSrc;

            this.video.onloadeddata = () => {
                this.video.currentTime = t;
                if (!paused) this.video.play();
            };
        };
    }

    formatTime(sec) {
        let min = Math.floor(sec / 60);
        let s   = sec % 60;
        return `${String(min).padStart(2,"0")}:${String(s).padStart(2,"0")}`;
    }

    /* --------------------------
        AUTO OCULTAR CONTROLES ESTILO YOUTUBE
    ----------------------------*/
    setupAutoHide() {
        const show = () => this.controls.classList.add("mostrar");
        const hide = () => { if (!this.video.paused) this.controls.classList.remove("mostrar"); };

        let timer;

        this.root.addEventListener("mousemove", () => {
            show();
            clearTimeout(timer);
            timer = setTimeout(hide, 2500);
        });

        this.controls.addEventListener("mouseenter", () => clearTimeout(timer));
        this.controls.addEventListener("mouseleave", () => timer = setTimeout(hide, 2500));

        this.video.addEventListener("pause", show);
        this.video.addEventListener("play", () => {
            clearTimeout(timer);
            timer = setTimeout(hide, 2500);
        });

        show();
    }

    async loadResolutions(url) {
        try {
            const res = await fetch(url);
            const data = await res.json();
            Object.entries(data).forEach(([label, obj]) => {
                let op = document.createElement("option");
                op.value = "output/" + obj.filename;
                op.textContent = label;
                this.resolSelect.appendChild(op);
            });
        } catch (e) {
            console.error("No se pudo cargar el archivo:", url, e);
        }
    }
};
