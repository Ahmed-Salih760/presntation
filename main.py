import os
import flet as ft
import flet_video as fv
import flet_permission_handler as fph


VIDEOS_DIR = "/storage/emulated/0/zydisk"


def main(page: ft.Page):

    page.padding = 0
    page.spacing = 0
    page.bgcolor = ft.Colors.BLACK
    page.full_screen = True

    # عنصر غير مرئي (service) مسؤول عن طلب إذن التخزين وقت التشغيل.
    # التصريح بالإذن في pyproject.toml وحده لا يكفي على أندرويد 6+،
    # لازم نطلبه فعلياً هنا وإلا نحصل على نفس PermissionError.
    ph = fph.PermissionHandler()
    page.services.append(ph)

    async def open_settings(e):
        await ph.open_app_settings()

    def show_message(text, with_settings_button=False):
        page.add(
            ft.Text(
                text,
                color=ft.Colors.WHITE,
                size=18,
                text_align=ft.TextAlign.CENTER,
            )
        )
        if with_settings_button:
            page.add(
                ft.ElevatedButton(
                    "فتح إعدادات التطبيق",
                    on_click=open_settings,
                )
            )

    async def start():

        status = await ph.request(fph.Permission.STORAGE)

        if status != fph.PermissionStatus.GRANTED:
            show_message(
                "التطبيق يحتاج إذن الوصول إلى التخزين لعرض الفيديوهات.\n"
                "امنح الإذن من الزر بالأسفل ثم أعد فتح التطبيق.",
                with_settings_button=True,
            )
            return

        if not os.path.exists(VIDEOS_DIR):
            os.makedirs(VIDEOS_DIR, exist_ok=True)

            show_message(
                f"تم إنشاء مجلد الفيديوهات:\n{VIDEOS_DIR}\n\nضع ملفات mp4 بداخله"
            )
            return

        videos = []

        for f in sorted(os.listdir(VIDEOS_DIR)):
            if f.lower().endswith(".mp4"):
                videos.append(
                    os.path.join(VIDEOS_DIR, f)
                )

        if not videos:
            show_message("لم يتم العثور على فيديوهات mp4 داخل zydisk")
            return

        index = 0
        waiting = True

        player = fv.Video(
            expand=True,
            autoplay=False,
            show_controls=False,
        )

        async def load_video():

            player.playlist = [
                fv.VideoMedia(videos[index])
            ]

            page.update()

            await page.sleep(0.5)

            player.play()

            await page.sleep(0.05)

            player.pause()

            player.seek(
                ft.Duration(milliseconds=0)
            )

        async def next_slide():

            nonlocal waiting

            if waiting:

                waiting = False

                player.play()

        async def completed(e):

            nonlocal index
            nonlocal waiting

            index += 1

            if index >= len(videos):
                index = 0

            waiting = True

            player.playlist = [
                fv.VideoMedia(videos[index])
            ]

            player.update()

            await page.sleep(0.5)

            player.play()

            await page.sleep(0.05)

            player.pause()

            player.seek(
                ft.Duration(milliseconds=0)
            )

        player.on_complete = completed

        async def tap(e):
            await next_slide()

        detector = ft.GestureDetector(

            on_tap=tap,

            content=ft.Container(
                expand=True,
                bgcolor=ft.Colors.TRANSPARENT
            )
        )

        stack = ft.Stack(

            expand=True,

            controls=[

                player,

                detector

            ]
        )

        page.add(stack)

        page.run_task(load_video)

    page.run_task(start)


ft.app(target=main)
