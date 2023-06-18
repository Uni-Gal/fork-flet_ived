import multiprocessing
import os
import time

import flet as ft
import flet.canvas as cv
from flet_core import ClipBehavior

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


class State:
    selector_x = -8
    selector_width = 400
    init_local_x = 0
    circle_radius = 8
    min_interval = 50
    last_x = -8
    last_width = 400


state = State()


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

        def move_left_start(e):
            state.init_local_x = e.local_x
            state.last_width = state.selector_width
            state.last_x = state.selector_x

        def move_left_update(e):
            if state.last_width - (e.local_x - state.init_local_x) < state.min_interval:
                state.selector_x = state.last_x + state.last_width - state.min_interval
                state.selector_width = state.min_interval
            elif state.last_x + (e.local_x - state.init_local_x) < 0:
                state.selector_x = -state.circle_radius
                state.selector_width = state.last_width + state.last_x + state.circle_radius
            else:
                state.selector_x = state.last_x + (e.local_x - state.init_local_x)
                state.selector_width = state.last_width - (e.local_x - state.init_local_x)

            bg_selector_item.shapes = [
                cv.Line(state.selector_x + state.circle_radius, 0,
                        state.selector_x + state.selector_width + state.circle_radius, 0,
                        paint=stroke_paint),
                cv.Line(state.selector_x + state.circle_radius, 60,
                        state.selector_x + state.selector_width + state.circle_radius, 60,
                        paint=stroke_paint),
                cv.Rect(0, 0, state.selector_x + state.circle_radius, 60, paint=bg_paint),
                cv.Rect(state.selector_x + state.selector_width + state.circle_radius, 0,
                        400 - state.selector_x - state.selector_width - state.circle_radius,
                        60,
                        paint=bg_paint),
            ]
            bg_selector_item.update()
            range_selector_left_item.left = state.selector_x
            range_selector_left_item.update()

        def move_left_end(e):
            print('左边拖拽结束，x=', state.selector_x, 'width=', state.selector_width)
            print('视频起始点占比=', (state.selector_x + state.circle_radius) / 400)
            print('视频时长跨度占比=', state.selector_width / 400)

        def move_right_start(e):
            state.init_local_x = e.local_x
            state.last_x = state.selector_x
            state.last_width = state.selector_width

        def move_right_update(e):
            if state.last_width + (e.local_x - state.init_local_x) <= state.min_interval:
                state.selector_width = state.min_interval
            elif state.selector_x + state.last_width + (
                    e.local_x - state.init_local_x) >= 400 - state.circle_radius:
                state.selector_width = 400 - state.circle_radius - state.selector_x
            else:
                state.selector_width = state.last_width + (e.local_x - state.init_local_x)
            bg_selector_item.shapes = [
                cv.Line(state.selector_x + state.circle_radius, 0,
                        state.selector_x + state.selector_width + state.circle_radius, 0,
                        paint=stroke_paint),
                cv.Line(state.selector_x + state.circle_radius, 60,
                        state.selector_x + state.selector_width + state.circle_radius, 60,
                        paint=stroke_paint),
                cv.Rect(0, 0, state.selector_x + state.circle_radius, 60, paint=bg_paint),
                cv.Rect(state.selector_x + state.selector_width + state.circle_radius, 0,
                        400 - state.selector_x - state.selector_width - state.circle_radius,
                        60,
                        paint=bg_paint),
            ]
            bg_selector_item.update()

            range_selector_right_item.left = state.selector_x + state.selector_width
            range_selector_right_item.update()
            # print('宽度变化：' + str(state.selector_width))

        def move_right_end(e):
            print('右边拖拽结束，x=', state.selector_x, 'width=', state.selector_width)
            print('视频起始点占比=', (state.selector_x + state.circle_radius) / 400)
            print('视频时长跨度占比=', state.selector_width / 400)

        bg_paint = ft.Paint(
            style=ft.PaintingStyle.FILL,
            color=ft.colors.with_opacity(0.88, ft.colors.BLUE_800)
        )

        stroke_paint = ft.Paint(
            stroke_width=2,
            style=ft.PaintingStyle.STROKE,
            color=ft.colors.BLUE_200,
        )

        fill_paint = ft.Paint(
            style=ft.PaintingStyle.FILL,
            color=ft.colors.with_opacity(0.88, ft.colors.BLUE_200)
        )

        bg_selector_item = cv.Canvas(
            [
                cv.Line(state.selector_x + state.circle_radius, 0,
                        state.selector_x + state.selector_width + state.circle_radius, 0,
                        paint=stroke_paint),
                cv.Line(state.selector_x + state.circle_radius, 60,
                        state.selector_x + state.selector_width + state.circle_radius, 60,
                        paint=stroke_paint),
                cv.Rect(0, 0, state.selector_x + state.circle_radius, 60, paint=bg_paint),
                cv.Rect(state.selector_x + state.selector_width + state.circle_radius, 0,
                        400 - state.selector_x - state.selector_width - state.circle_radius,
                        60,
                        paint=bg_paint),
            ],
            width=float("inf"),
            expand=True,
        )
        range_selector_left_item = ft.Container(
            left=state.selector_x,
            # bgcolor=ft.colors.RED,
            width=16,
            height=60,
            expand=False,
            content=cv.Canvas(
                [
                    cv.Line(state.circle_radius, 0, state.circle_radius, 60, paint=stroke_paint),
                    cv.Circle(state.circle_radius, 30, state.circle_radius, fill_paint),
                ],
                expand=False,
                content=ft.GestureDetector(
                    on_pan_start=move_left_start,
                    on_pan_update=move_left_update,
                    on_pan_end=move_left_end,
                )
            )
        )

        range_selector_right_item = ft.Container(
            width=16,
            # bgcolor=ft.colors.YELLOW,
            height=60,
            expand=False,
            left=state.selector_x + state.selector_width,
            content=cv.Canvas(
                [
                    cv.Line(state.circle_radius, 0, state.circle_radius, 60, paint=stroke_paint),
                    cv.Circle(state.circle_radius, 30, state.circle_radius, fill_paint),
                ],
                content=ft.GestureDetector(
                    on_pan_start=move_right_start,
                    on_pan_update=move_right_update,
                    on_pan_end=move_right_end,
                )
            )
        )

        def create_video_obj(cur_video_key):

            def listview_update():
                for index, frame in enumerate(vcc.all_frames_of_video[:7]):
                    lvv.controls.append(
                        ft.Image(
                            height=9999,
                            src_base64=frame,
                            fit=ft.ImageFit.COVER,
                            expand=True,
                        )
                    )
                lvv.update()

            vcc = VideoContainer(
                cur_video_key,
                border_radius=10,
                expand=True,
                play_after_loading=False,
                video_play_button=True,
                # padding=ft.padding.only(bottom=16),
                exec_after_full_loaded=listview_update
            )

            lvv = ft.Row(
                run_spacing=0,
                spacing=0
            )

            return ft.Container(
                height=300,
                content=ft.Column(
                    width=400,
                    controls=[
                        ft.Container(
                            width=400,
                            height=225,
                            content=vcc
                        ),
                        ft.Stack(
                            height=60,
                            visible=True,
                            clip_behavior=ClipBehavior.NONE,
                            controls=[
                                ft.Container(
                                    bgcolor=ft.colors.BLACK54,
                                    height=60,
                                    content=lvv
                                ),
                                bg_selector_item,
                                range_selector_left_item,
                                range_selector_right_item

                            ],
                        ),
                    ],
                ),
            )

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("调整素材首尾"),
            content=None,
            content_padding=ft.padding.all(24),
            actions=[
                ft.TextButton("返回", on_click=close_dlg),

            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
            # content_padding=0,
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

        video_dir = r"C:\Users\user\Desktop\test"

        count = 10

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
