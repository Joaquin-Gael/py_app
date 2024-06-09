import flet as ft
from pathlib import Path
import pytube as yt
import re
import os

BASE_DIR = Path(__file__).parent
CARPETA_DESCARGAS = Path(Path.home() / 'Downloads').resolve()

def clean_name(name):
    caracteres_especiales = r'|/\\\"?<>'
    try:
        for char in caracteres_especiales:
            if name.find(char):
                return re.sub(r'|/\\"?<>', '_', name)
        return name
    except Exception as err:
        print(f'Error clean name: {err}')

async def toggle_visibility(e, urlObjet: ft.TextField, page: ft.Page) -> None:
    try:
        urlObjet.visible = not urlObjet.visible
        await page.update_async()
    except Exception as err:
        print(f'Toggle visibility Error: {err}')

path_user:str = ''

text_path = ft.Text(f'La carpeta por defecto es\n{CARPETA_DESCARGAS}')

progres_text = ft.Text(
    '0%',
    visible=False
)

progres_bar = ft.ProgressBar(
    width=600,
    visible=False
)

title_video = ft.Text('Title:')

img_video = ft.Image(
        src=f"https://www.golpumptechnology.com/wp-content/uploads/2023/05/Imagen_por_defecto.webp",
        width=300,
        height=250,
        fit=ft.ImageFit.CONTAIN,
    )

icon_status = ft.Icon()

info_banner = ft.Banner(open=False,content=ft.Text(''))

button_style = ft.ButtonStyle(
        color={
                    ft.MaterialState.HOVERED: ft.colors.WHITE,
                    ft.MaterialState.FOCUSED: ft.colors.BLUE,
                    ft.MaterialState.DEFAULT: ft.colors.BLACK,
                },
        overlay_color="#00796B",
        elevation=2,
        padding=10,
        shape=ft.RoundedRectangleBorder(radius=10),
    )

async def main(page: ft.Page) -> None:
    global path_user

    def close_object(e):
        info_banner.open = False
        page.update()

    def progres_data(stream, chink, bytes_remaining):
        progres_bar.visible = True
        progres_text.visible = True
        page.update()
        try:
            _total = stream.filesize
            _bytes_downloaded = _total - bytes_remaining
            porcent = (_bytes_downloaded/_total)
            progres_bar.value = porcent
            progres_text.value = porcent*100
            page.update()
        except Exception as err:
            print(f'Error en descarga: {err}')
            progres_bar.visible = False
            progres_text.visible = False
            page.update()

    async def print_path(e: ft.FilePickerResultEvent):
        global path_user
        path_user = e.path
        text_path.value = e.path
        page.update()
        print(f'Carpetas seleccionadas: {path_user}')

    def activate_mp3(e):
        Descargar_video.visible = False
        Descargar_audio.visible = True
        page.update()

    def activate_mp4(e):
        Descargar_audio.visible = False
        Descargar_video.visible = True
        page.update()

    file_picker = ft.FilePicker(on_result=print_path)
    page.window_width = 800
    page.window_height = 600
    page.window_resizable = False
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.overlay.append(file_picker)
    page.banner = info_banner
    page.appbar = ft.AppBar(
        title=ft.Text(
            'Descargar Videos',
            color='#009485'
        ),
        center_title=True,
        actions=[
            ft.PopupMenuButton(
                scale=1.3,
                data="Menu",
                items=[
                    ft.PopupMenuItem(
                        icon=ft.icons.DOWNLOAD,
                        text='.mp3',
                        on_click=activate_mp3
                    ),
                    ft.PopupMenuItem(
                        icon=ft.icons.DOWNLOAD,
                        text='.mp4',
                        on_click=activate_mp4
                    )
                ]
            )
        ]
    )

    url = ft.TextField(
        text_size=20,
        autofocus=True,
        width=250,
        visible=False,
        bgcolor='#006e63'
    )

    async def Descargar_audio_(e):
        try:
            audio_data = yt.YouTube(url.value, on_progress_callback=progres_data)
            title_video.value = f'Title: {audio_data.title}'
            img_video.src = audio_data.thumbnail_url
            page.update()
            audio = audio_data.streams.filter(only_audio=True).first()
            if path_user is not None or '' or not isinstance(path_user,str):
                audio = audio.download(
                    output_path=path_user,
                    filename_prefix='Audio descargado_',
                    filename=clean_name(audio_data.title),
                    max_retries=200,
                    skip_existing=False,
                    timeout=500
                )
                paths,_ = os.path.splitext(audio)
                os.rename(audio,paths + '.mp3')
                url.value = ''
                info_banner.open = True
                info_banner.content = ft.Text('Descarga finalizada')
                info_banner.leading = ft.Icon(ft.icons.FAVORITE)
                info_banner.actions = [
                    ft.ElevatedButton(
                        'Cerrar',
                        on_click=close_object
                    )
                ]
                icon_status.name = ft.icons.DOWNLOAD_DONE
                page.update()
            else:
                audio = audio.download(
                    output_path=CARPETA_DESCARGAS,
                    filename_prefix='Audio descargado_',
                    filename=clean_name(audio_data.title),
                    max_retries=200,
                    skip_existing=False,
                    timeout=500
                )
                paths, _ = os.path.splitext(audio)
                os.rename(audio, paths + '.mp3')
                url.value = ''
                info_banner.open = True
                info_banner.content = ft.Text('Descarga finalizada')
                info_banner.leading = ft.Icon(ft.icons.FAVORITE)
                info_banner.actions = [
                    ft.ElevatedButton(
                        'Cerrar',
                        on_click=close_object
                    )
                ]
                icon_status.name = ft.icons.DOWNLOAD_DONE
                page.update()
        except Exception as err:
            print(f'Error descarga audio: {err}')

    async def Descargar_video_(e):
        try:
            video = yt.YouTube(url.value, on_progress_callback=progres_data)
            title_video.value = f'Title: {video.title}'
            img_video.src = video.thumbnail_url
            page.update()
            stream = video.streams.get_highest_resolution()
            if path_user is not None or '' or not isinstance(path_user, str):
                video = stream.download(
                    output_path=path_user,
                    filename_prefix='Video descargado_',
                    filename=clean_name(video.title),
                    max_retries=200,
                    skip_existing=False,
                    timeout=500
                )
                paths,_ = os.path.splitext(video)
                os.rename(video,paths + '.mp4')
                url.value = ''
                info_banner.open = True
                info_banner.content = ft.Text('Descarga finalizada')
                info_banner.leading = ft.Icon(ft.icons.FAVORITE)
                info_banner.actions = [
                    ft.ElevatedButton(
                        'Cerrar',
                        on_click=close_object
                    )
                ]
                icon_status.name = ft.icons.DOWNLOAD_DONE
                page.update()
            else:
                video = stream.download(
                    output_path=CARPETA_DESCARGAS,
                    filename_prefix='Video descargado_',
                    filename=clean_name(video.title),
                    max_retries=200,
                    skip_existing=False,
                    timeout=500
                )
                paths, _ = os.path.splitext(video)
                os.rename(video, paths + '.mp4')
                url.value = ''
                info_banner.open = True
                info_banner.content = ft.Text('Descarga finalizada')
                info_banner.leading = ft.Icon(ft.icons.FAVORITE)
                info_banner.actions = [
                    ft.ElevatedButton(
                        'Cerrar',
                        on_click=close_object
                    )
                ]
                icon_status.name = ft.icons.DOWNLOAD_DONE
                page.update()
        except Exception as err:
            print(f'Error descarga: {err}')
            icon_status.name = ft.icons.ALARM
            info_banner.open = True
            info_banner.content = ft.Text(f'Ocurrio un error en la descarga\n{err}')
            info_banner.leading = ft.Icon(ft.icons.ALARM)
            info_banner.actions = [
                ft.ElevatedButton(
                    'Cerrar',
                    on_click=lambda e:close_object(e, info_banner)
                )
            ]
            page.update()
    async def on_search_click(e):
        await toggle_visibility(e, url, page)

    page.bottom_appbar = ft.BottomAppBar(
        bgcolor='#009485',
        shape=ft.NotchShape.CIRCULAR,
        content=ft.Row(
            controls=[
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.icons.SEARCH,
                    icon_color='#dfeceb',
                    on_click=on_search_click,
                    bgcolor='#006e63'
                ),
                url,
            ]
        ),
    )

    Descargar_audio = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        'Descargar mp3',
                        icon=ft.icons.DOWNLOAD,
                        on_click=Descargar_audio_
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        ],
        visible=False
    )

    Descargar_video = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        'Descargar',
                        icon=ft.icons.DOWNLOAD,
                        on_click=Descargar_video_
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        ]
    )

    content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            'Selecciona una carpeta para guardar los videos',
                            icon=ft.icons.UPLOAD_FILE,
                            on_click=lambda e: file_picker.get_directory_path(initial_directory=CARPETA_DESCARGAS),
                            style=button_style
                        ),
                        text_path
                    ]
                ),
                ft.Stack(
                    controls=[
                        ft.Container(
                            content=Descargar_video
                        ),
                        ft.Container(
                            content=Descargar_audio
                        )
                    ]
                ),
                ft.Row(
                    controls=[
                        progres_text,
                        progres_bar,
                        icon_status
                    ]
                ),
                ft.Row(
                    controls=[
                        img_video
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Row(
                    controls=[
                        title_video
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ]
        )
    )

    page.add(content)

if __name__ == '__main__':
    ft.app(target=main,upload_dir=Path(BASE_DIR / 'uploads') if path_user is None or '' or not isinstance(path_user,str) else path_user)
