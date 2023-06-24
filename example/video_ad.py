import multiprocessing

import flet as ft
from flet_ivid_hks.clip_container import ClipContainer


class VideoAd(object):

    def __init__(self):
        self.cur_video_obj = None

    def main(self, page: ft.Page):
        page.title = "Video Clip Example"
        page.theme_mode = ft.ThemeMode.LIGHT

        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        page.window_width = 560
        page.window_height = 650

        page.window_max_width = 560
        page.window_max_height = 850

        page.window_min_width = 560
        page.window_min_height = 650

        page.window_top = 200
        page.window_left = 400

        page.padding = 50
        page.update()

        cur_video_key = r"C:\Users\Administrator\Desktop\89446442254606336.mp4"

        vcc = ClipContainer(
            cur_video_key,
            show_timecode=True
        )

        page.add(
            ft.Container(
                content=vcc,
                bgcolor=ft.colors.BLACK12,
                padding=20,
            )
        )


if __name__ == '__main__':
    multiprocessing.freeze_support()
    bm = VideoAd()

    ft.app(target=bm.main, view=ft.FLET_APP_WEB)
