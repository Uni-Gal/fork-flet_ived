import multiprocessing
import os
import time

import flet as ft
from flet_ivid_hks import VideoContainer

video_ext = [
    '.mp4', '.avi', '.mpg', '.mov',
    '.flv', ".mxf", ".mpeg", ".mkv",
    ".ogg", ".3gp", ".wmv", ".h264",
    ".m4v", ".webm"
]


# 返回文件后缀名
def return_file_ext(filename):
    return os.path.splitext(filename)[-1].lower()


# 判断传入文件是否为视频
def is_match_video_ext(filename):
    if return_file_ext(filename) in video_ext:
        return True


class VideoGrid(object):

    def __init__(self):
        self.cur_video_obj = None

    def main(self, page: ft.Page):
        page.title = "GridView Example"
        page.theme_mode = ft.ThemeMode.LIGHT

        # page.vertical_alignment = ft.MainAxisAlignment.CENTER
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

        video_grid = ft.GridView(
            expand=1,
            runs_count=3,
            max_extent=130,
            child_aspect_ratio=1.7778,
            spacing=30,
            run_spacing=20,
        )

        def close_dlg(e):
            dlg_modal.open = False
            self.cur_video_obj = None
            page.update()

        def create_video_obj(cur_video_key):

            def listview_update():
                for index, frame in enumerate(vcc.all_frames_of_video[:7]):
                    lvv.controls.append(
                        ft.Image(
                            src_base64=frame,
                            expand=True,
                            fit=ft.ImageFit.COVER
                        )
                    )
                lvv.update()

            vcc = VideoContainer(
                cur_video_key,
                border_radius=10,
                expand=True,
                play_after_loading=False,
                video_play_button=True,
                padding=ft.padding.only(bottom=16),
                exec_after_full_loaded=listview_update
            )

            lvv = ft.ListView()

            return ft.Column(
                controls=[
                    vcc,
                    ft.Stack(
                        controls=[
                            ft.Container(
                                bgcolor=ft.colors.BLACK54,
                                height=60,
                                content=lvv
                            )
                        ]

                    )
                ],
            )

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("调整素材首尾"),
            content=None,
            actions=[
                ft.TextButton("返回", on_click=close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

        def open_dlg_modal(e):
            print(e.control.key)
            self.cur_video_obj = create_video_obj(e.control.key)
            time.sleep(0.1)

            dlg_modal.content = self.cur_video_obj
            page.dialog = dlg_modal

            dlg_modal.open = True
            page.update()

        page.add(
            ft.Container(
                content=video_grid,
                bgcolor=ft.colors.BLACK12,
                padding=20,
                height=210,
                border_radius=10,
            )
        )

        video_dir = r"C:\Users\Administrator\Desktop\同合杉天MCN\output\.cache"

        count = 100

        for file in os.listdir(video_dir):
            count = count - 1
            if count == 0:
                break
            if is_match_video_ext(file):
                video_grid.controls.append(
                    VideoContainer(
                        os.path.join(video_dir, file),
                        border_radius=10,
                        expand=True,
                        play_after_loading=False,
                        on_click=open_dlg_modal,
                        video_progress_bar=False,
                        key=os.path.join(video_dir, file),
                        only_show_cover=True,
                    )
                )

        video_grid.update()

        # page.update()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    bm = VideoGrid()

    ft.app(target=bm.main, view=ft.FLET_APP_WEB)
