# flet_ivid_hks
A package tool that provide basic video player for flet. Its super easy to use, its built to be used as a normal `flet` control.

## installation
To install, just type:

```
pip install flet_ivid_hks --upgrade
```

## usage

To start show your video inside your `flet` app, you can just import the `VideoContainer` control and use its properties, for example:

```python
from flet_ivid_hks import VideoContainer # import the package
import flet


def main (page:flet.Page):
    page.bgcolor = "black"
    vc = VideoContainer("yourvideo.mp4", border_radius=18, expand=True) # This is a VideoContainer
    page.add(flet.Row([vc], alignment="center"))

    vc.play() # call `play` function to make the video start playing.

    # Call `vc.pause()` to stop the video from playing.

flet.app(target=main)
```

## Note
`Note`: **You should know that this built to be used for basic small or normal usage, its can NOT be used for big production cases, if you do so it will be a RAM consuming and slow for biger videos..**