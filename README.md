# New-project-hjjnn
<p align="center">
  <img src="mascot/mascot.svg" alt="Project mascot: a happy little cell with a bow" width="200">
</p>

## Mascot

Meet our mascot, a happy little cell with a bow.

- `mascot/mascot.svg`: vector version that scales to any size (use this one)
- `mascot/original.jpg`: the original hand-drawn artwork, signed "@ the itty bitty cells"

## Video: How cancer hides

`video/how-cancer-hides.mp4` is a 30-second vertical (9:16, 1080×1920) explainer starring Muse.
It has on-screen captions and subtitles but no audio, so the voiceover can be added in an editor.

- `video/cancer-tricks.html`: the animation source. Open it in a browser to watch it loop.
- `video/render.js`: renders the HTML to MP4 frame by frame (needs Playwright and ffmpeg):
  `node video/render.js "$PWD/video/cancer-tricks.html" "$PWD/video/how-cancer-hides.mp4"`
