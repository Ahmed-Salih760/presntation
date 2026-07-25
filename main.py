import os
import flet as ft
import flet_video as fv

VIDEOS_DIR = "/storage/emulated/0/zydisk"

def main(page: ft.Page):
    page.padding = 0
    page.spacing = 0
    page.bgcolor = ft.Colors.BLACK
    page.full_screen = True

    # 1. إضافة أداة التحكم في الصلاحيات لواجهة التطبيق
    ph = ft.PermissionHandler()
    page.overlay.append(ph)

    def check_permissions_and_run():
        try:
            # نحاول التحقق من المجلد أو إنشائه
            if not os.path.exists(VIDEOS_DIR):
                os.makedirs(VIDEOS_DIR, exist_ok=True)
                
                page.add(
                    ft.Text(
                        f"تم إنشاء مجلد الفيديوهات:\n{VIDEOS_DIR}\n\nضع ملفات mp4 بداخله",
                        color=ft.Colors.WHITE,
                        size=18,
                        text_align=ft.TextAlign.CENTER
                    )
                )
                return
            
            # إذا نجح الوصول للمجلد دون أخطاء، ننتقل لتشغيل الفيديوهات
            load_app_logic()

        except PermissionError:
            # 2. إذا تم منع الوصول، نظهر زر لطلب الصلاحية بدلاً من انهيار التطبيق
            def request_storage(e):
                ph.request_permission(ft.PermissionType.STORAGE)

            page.add(
                ft.Column(
                    [
                        ft.Text("التطبيق بحاجة لصلاحية الوصول إلى التخزين لقراءة الفيديوهات.", color=ft.Colors.WHITE, size=18),
                        ft.ElevatedButton("منح الصلاحية", on_click=request_storage)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

    def on_permission_result(e: ft.PermissionEvent):
        # 3. بمجرد استجابة المستخدم لطلب الصلاحية
        if e.status == ft.PermissionStatus.GRANTED:
            page.controls.clear()
            check_permissions_and_run() # نعيد المحاولة
        else:
            page.add(ft.Text("لا يمكن تشغيل التطبيق بدون صلاحية التخزين.", color=ft.Colors.RED))

    ph.on_permission_result = on_permission_result

    def load_app_logic():
        videos = []

        for f in sorted(os.listdir(VIDEOS_DIR)):
            if f.lower().endswith(".mp4"):
                videos.append(os.path.join(VIDEOS_DIR, f))

        if not videos:
            page.add(
                ft.Text(
                    "لم يتم العثور على فيديوهات mp4 داخل zydisk",
                    color=ft.Colors.WHITE,
                    size=18
                )
            )
            return

        index = 0
        waiting = True

        player = fv.Video(
            expand=True,
            autoplay=False,
            show_controls=False,
        )

        async def load_video():
            player.playlist = [fv.VideoMedia(videos[index])]
            page.update()
            await page.sleep(0.5)
            player.play()
            await page.sleep(0.05)
            player.pause()
            player.seek(ft.Duration(milliseconds=0))

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
            player.playlist = [fv.VideoMedia(videos[index])]
            player.update()
            
            await page.sleep(0.5)
            player.play()
            await page.sleep(0.05)
            player.pause()
            player.seek(ft.Duration(milliseconds=0))

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

    # نقطة البداية الفعلية للتطبيق
    check_permissions_and_run()

ft.app(target=main)
