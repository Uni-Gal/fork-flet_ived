from flet_core import ClipBehavior, Container

from flet_ivid_hks import VideoContainer
import flet as ft
import flet.canvas as cv


class State:
    selector_x = -8
    selector_width = 400
    init_local_x = 0
    circle_radius = 8
    min_interval = 50
    last_x = -8
    last_width = 400


state = State()


def float2gtd(
        dur: float
) -> float:
    return round(dur, 4)


def indices_for_n_parts(lst, n):
    """给定一个列表和整数N，输出列表每N个元素的索引"""

    # 确保N不会大于列表长度，如果N大于列表长度，则每个元素都是等分点
    n = min(n, len(lst))

    # 计算每一部分的长度
    step = len(lst) / float(n)

    # 创建一个索引列表，使用round函数来保证索引是整数
    indices = [round(step * i) for i in range(n)]

    return indices


class ClipContainer(Container):

    def __init__(
            self,
            video_path,
            show_timecode=False
    ):
        super().__init__()
        self.video_path = video_path

        self.clip_ui_container = None
        self.vc = None
        self.show_timecode = show_timecode

        self.clip_ui()

        self.start_time = 0
        self.end_time = 0

    def clip_ui(
            self
    ):

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

            # 即拖即显
            cur_frame = int((state.selector_x + state.circle_radius) / 400 * self.vc.frame_length)
            self.vc.image_frames_viewer.src_base64 = self.vc.all_frames_of_video[cur_frame]
            self.vc.image_frames_viewer.update()

            cur_timecode = float2gtd(
                (state.selector_x + state.circle_radius) / 400 * self.vc.vid_duration
            )

            timecode_st.value = "start：" + str(
                cur_timecode
            ) + "s"
            timecode_st.update()

            self.start_time = cur_timecode

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

            # 即拖即显
            cur_frame = int(
                (state.selector_x + state.circle_radius + state.selector_width) / 400 * self.vc.frame_length)
            self.vc.image_frames_viewer.src_base64 = self.vc.all_frames_of_video[cur_frame - 1]
            self.vc.image_frames_viewer.update()

            cur_timecode = float2gtd(
                (state.selector_x + state.circle_radius + state.selector_width) / 400 * self.vc.vid_duration
            )

            timecode_ed.value = "end：" + str(
                cur_timecode
            ) + "s"
            timecode_ed.update()

            self.end_time = cur_timecode

        def move_right_end(e):
            print('右边拖拽结束，x=', state.selector_x, 'width=', state.selector_width)
            print('视频起始点占比=', (state.selector_x + state.circle_radius) / 400)
            print('视频时长跨度占比=', state.selector_width / 400)

        bg_paint = ft.Paint(
            style=ft.PaintingStyle.FILL,
            color=ft.colors.with_opacity(0.64, ft.colors.BLUE_800)
        )

        stroke_paint = ft.Paint(
            stroke_width=2,
            style=ft.PaintingStyle.STROKE,
            color=ft.colors.BLUE_200,
        )

        fill_paint = ft.Paint(
            style=ft.PaintingStyle.FILL,
            color=ft.colors.with_opacity(0.95, ft.colors.BLUE_200)
        )

        bg_selector_item = cv.Canvas(
            [
                cv.Line(
                    state.selector_x + state.circle_radius,
                    0,
                    state.selector_x + state.selector_width + state.circle_radius,
                    0,
                    paint=stroke_paint
                ),
                cv.Line(
                    state.selector_x + state.circle_radius,
                    60,
                    state.selector_x + state.selector_width + state.circle_radius,
                    60,
                    paint=stroke_paint
                ),
                cv.Rect(
                    0,
                    0,
                    state.selector_x + state.circle_radius,
                    60,
                    paint=bg_paint
                ),
                cv.Rect(
                    state.selector_x + state.selector_width + state.circle_radius,
                    0,
                    400 - state.selector_x - state.selector_width - state.circle_radius,
                    60,
                    paint=bg_paint
                ),
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
                    cv.Line(
                        state.circle_radius,
                        0,
                        state.circle_radius,
                        60,
                        paint=stroke_paint
                    ),
                    cv.Circle(
                        state.circle_radius,
                        30,
                        state.circle_radius,
                        fill_paint
                    ),
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

        def timeline_frames_update():

            indices_index_list = indices_for_n_parts(self.vc.all_frames_of_video, 5)

            for index, frame in enumerate(indices_index_list):
                timeline_frames.controls.append(
                    ft.Image(
                        height=float("inf"),
                        src_base64=self.vc.all_frames_of_video[frame],
                        fit=ft.ImageFit.COVER,
                        expand=True,
                    )
                )
            timeline_frames.update()

            timecode_ed.value = "end：" + str(
                float2gtd(self.vc.vid_duration)
            ) + "s"

            self.end_time = float2gtd(self.vc.vid_duration)

            self.content.update()

        self.vc = VideoContainer(
            self.video_path,
            # border_radius=10,
            width=400,
            expand=True,
            play_after_loading=False,
            video_play_button=True,
            exec_after_full_loaded=timeline_frames_update
        )

        timeline_frames = ft.Row(
            run_spacing=0,
            spacing=0
        )

        timecode_st = ft.Text(
            "start：0s"
        )

        timecode_ed = ft.Text(
            "end：∞s"
        )

        timecode_area = ft.Container(
            content=ft.Row(
                controls=[
                    timecode_st,
                    timecode_ed,
                ],
                alignment=ft.MainAxisAlignment.START
            ),
            padding=24,
            visible=False
        )

        if self.show_timecode:
            timecode_area.visible = True

        self.content = ft.Container(
            height=300,
            content=ft.Column(
                width=400,
                controls=[
                    ft.Container(
                        width=400,
                        height=225,
                        content=self.vc
                    ),
                    ft.Stack(
                        height=60,
                        visible=True,
                        clip_behavior=ClipBehavior.NONE,
                        controls=[
                            ft.Container(
                                bgcolor=ft.colors.BLACK54,
                                height=60,
                                content=timeline_frames
                            ),
                            bg_selector_item,
                            range_selector_left_item,
                            range_selector_right_item
                        ],
                    ),
                    timecode_area
                ],
            ),
        )
