import re

from flet import Container
from flet_core.control import OptionalNumber
from flet_core.types import BlendMode
from flet_core.image import Image
from flet_core.stack import Stack
from flet_core.row import Row
import threading
import flet
import os
import cv2
import base64
import time


class VideoContainer(Container):
    """This will show a video you choose."""

    def __init__(
            self,
            video_path: str,
            play_after_loading=False,
            video_frame_fit_type: flet.ImageFit = None,
            video_progress_bar=True,
            video_play_button=False,
            exec_after_full_loaded=None,
            only_show_cover=False,
            content=None,
            ref=None,
            key=None,
            width=None,
            height=None,
            left=None,
            top=None,
            right=None,
            bottom=None,
            expand=None,
            col=None,
            opacity=None,
            rotate=None,
            scale=None,
            offset=None,
            aspect_ratio=None,
            animate_opacity=None,
            animate_size=None,
            animate_position=None,
            animate_rotation=None,
            animate_scale=None,
            animate_offset=None,
            on_animation_end=None,
            tooltip=None,
            visible=None,
            disabled=None,
            data=None,
            padding=None,
            margin=None,
            alignment=None,
            bgcolor=None,
            gradient=None,
            blend_mode=BlendMode.NONE,
            border=None,
            border_radius=None,
            image_src=None,
            image_src_base64=None,
            image_repeat=None,
            image_fit=None,
            image_opacity: OptionalNumber = None,
            shape=None,
            clip_behavior=None,
            ink=None,
            animate=None,
            blur=None,
            shadow=None,
            url=None,
            url_target=None,
            theme=None,
            theme_mode=None,
            on_click=None,
            on_long_press=None,
            on_hover=None
    ):
        super().__init__(content, ref, key, width, height, left, top, right, bottom, expand, col, opacity, rotate,
                         scale, offset, aspect_ratio, animate_opacity, animate_size, animate_position, animate_rotation,
                         animate_scale, animate_offset, on_animation_end, tooltip, visible, disabled, data, padding,
                         margin, alignment, bgcolor, gradient, blend_mode, border, border_radius, image_src,
                         image_src_base64, image_repeat, image_fit, image_opacity, shape, clip_behavior, ink, animate,
                         blur, shadow, url, url_target, theme, theme_mode, on_click, on_long_press, on_hover)

        self.__cur_play_frame = 0
        self.__video_pause_button = None
        self.__video_play_button = None
        self.__video_is_play = False
        self.vid_duration = None
        self.fps = 0
        self.__video_is_full_loaded = None
        self.video_frames = None
        self.exec_after_full_loaded = exec_after_full_loaded

        if not os.path.isfile(video_path):
            raise FileNotFoundError("Cannot find the video at the path you set.")

        self.all_frames_of_video = []
        self.__video_played = False
        self.video_progress_bar = video_progress_bar
        self.video_play_button = video_play_button

        if video_frame_fit_type is None:
            self.video_frame_fit_type = flet.ImageFit.CONTAIN

        # generate the UI
        self.__ui()

        if only_show_cover:
            self.read_video_cover(video_path)
            return

        # start a video reader.
        if play_after_loading:
            print("Please wait the video is loading..\nThis will take a time based on your video size...")
            self.read_the_video(video_path)
        else:
            threading.Thread(target=self.read_the_video, args=[video_path], daemon=True).start()

        self.audio_path = None
        self.__audio_path = None

        # get video info
        self.get_video_duration(video_path)
        self.__frame_per_sleep = 1.0 / self.fps

    def show_play(self):
        self.__video_is_play = False
        self.__video_play_button.visible = True
        self.__video_pause_button.visible = False
        self.__video_play_button.update()
        self.__video_pause_button.update()

    def show_pause(self):
        self.__video_is_play = True
        self.__video_play_button.visible = False
        self.__video_pause_button.visible = True
        self.__video_play_button.update()
        self.__video_pause_button.update()

    def __ui(self):
        # the video tools control
        self.video_tool_stack = Stack(expand=True)
        self.content = self.video_tool_stack

        self.image_frames_viewer = Image(expand=True, visible=False, fit=self.video_frame_fit_type)
        self.video_tool_stack.controls.append(Row([self.image_frames_viewer], alignment=flet.MainAxisAlignment.CENTER))

        self.__video_progress_bar = Container(height=2, width=1, bgcolor=flet.colors.BLUE_200)
        self.video_tool_stack.controls.append(Row([self.__video_progress_bar], alignment=flet.MainAxisAlignment.START))

        def play_video(e):
            print(e)
            if self.__video_is_play:
                self.pause()
                self.show_play()
            else:
                self.show_pause()
                self.play()

        self.__video_play_button = flet.IconButton(
            icon=flet.icons.SMART_DISPLAY,
            icon_color=flet.colors.WHITE54,
            icon_size=60,
            data=0,
            style=flet.ButtonStyle(
                elevation=4,
            ),
            on_click=play_video,
            visible=True
        )
        self.__video_pause_button = flet.IconButton(
            icon=flet.icons.PAUSE_PRESENTATION,
            icon_color=flet.colors.WHITE54,
            icon_size=60,
            data=0,
            style=flet.ButtonStyle(
                elevation=4,
            ),
            on_click=play_video,
            visible=False
        )
        self.video_tool_stack.controls.append(
            flet.Container(
                content=flet.Row(
                    controls=[
                        self.__video_play_button,
                        self.__video_pause_button
                    ]
                ),
                padding=flet.padding.only(25, 10, 10, 10),
                left=0,
                bottom=0,
            ),
        )

        if not self.video_progress_bar:
            self.__video_progress_bar.visible = False

        if not self.video_play_button:
            self.__video_play_button.visible = False

    def update_video_progress(self, frame_number):
        if not self.video_progress_bar:
            return
        percent_of_progress = frame_number / self.video_frames * 1

        if self.width:
            self.__video_progress_bar.width = percent_of_progress * 1 * self.width
        else:
            self.__video_progress_bar.width = percent_of_progress * 1 * self.page.width

        if self.__video_progress_bar.page is not None:
            try:
                self.__video_progress_bar.update()
            except Exception as e:
                pattern = r"control with ID '(.*)' not found"
                match = re.search(pattern, e.args[0])
                if not match:
                    print(e)
                return

    def update(self):
        self.image_frames_viewer.fit = self.video_frame_fit_type
        self.__video_progress_bar.visible = self.video_progress_bar
        return super().update()

    def play(self):
        """Play the video. (it's not blocking, because its on thread)."""
        if self.page is None:
            raise Exception("The control must be on page first.")

        self.__video_played = True
        threading.Thread(target=self.__play, daemon=True).start()

    def __play(self):
        self.image_frames_viewer.visible = True

        num = self.__cur_play_frame
        video_frames_len = len(self.all_frames_of_video)

        for index, i in enumerate(self.all_frames_of_video[self.__cur_play_frame:-1]):
            if not self.__video_played:
                self.__cur_play_frame = self.__cur_play_frame + index
                break
            if index + self.__cur_play_frame == video_frames_len - 2:
                self.__cur_play_frame = 0

            # update video progress bar
            threading.Thread(target=self.update_video_progress, args=[num], daemon=True).start()

            self.image_frames_viewer.src_base64 = i

            try:
                self.image_frames_viewer.update()
            except Exception as e:
                pattern = r"control with ID '(.*)' not found"
                match = re.search(pattern, e.args[0])
                if not match:
                    print(e)
                return

            time.sleep(self.__frame_per_sleep)
            num += 1

        self.show_play()

    def pause(self):
        self.__video_played = False

    def read_video_cover(self, video_path):
        video = cv2.VideoCapture(video_path)
        frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
        slice_frame_num = frame_count / 2
        video.set(cv2.CAP_PROP_POS_FRAMES, slice_frame_num)
        success, frame = video.read()
        _, buffer = cv2.imencode('.jpg', frame)
        encoded_frame = base64.b64encode(buffer).decode('utf-8')

        if self.image_frames_viewer.src_base64 is None:
            self.image_frames_viewer.src_base64 = encoded_frame
            self.image_frames_viewer.visible = True
            if self.image_frames_viewer.page is not None:
                self.image_frames_viewer.update()

        video.release()

    def read_the_video(self, video_path):
        # Open the video file
        video = cv2.VideoCapture(video_path)

        # Iterate over each frame and encode it
        success, frame = video.read()

        while success:
            # Encode the frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)

            # Base64 encode the buffer
            encoded_frame = base64.b64encode(buffer).decode('utf-8')

            # Store the base64-encoded frame in the list
            self.all_frames_of_video.append(encoded_frame)

            # check if the image is shown
            if self.image_frames_viewer.src_base64 is None:
                self.image_frames_viewer.src_base64 = encoded_frame
                self.image_frames_viewer.visible = True
                if self.image_frames_viewer.page is not None:
                    self.image_frames_viewer.update()

            success, frame = video.read()

        # Release the video object
        video.release()

        self.__video_is_full_loaded = True
        # exec callback
        if self.exec_after_full_loaded:
            self.exec_after_full_loaded()
        return self.all_frames_of_video

    def get_video_duration(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error opening video file")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        self.fps = fps

        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.video_frames = total_frames

        duration = total_frames / fps
        self.vid_duration = duration

        cap.release()
