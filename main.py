import flet as ft
from pathlib import Path
import re, os, requests, pytube as yt, random

BASE_DIR = Path(__file__).parent
CARPETA_DESCARGAS = Path(Path.home() / 'Downloads').resolve()
URL_BASE = r'http://127.0.0.1:8000'

def reemplazar_o_agregar(diccionario:dict, clave:int, nuevo_valor):
    """
    Reemplaza el valor asociado a la clave dada en el diccionario o agrega una nueva entrada si la clave no existe.
    """
    diccionario[clave] = nuevo_valor

class UserToken:
    def __init__(self, token=None):
        self.token = token

    def token_exist(self):
        return self.token in tokenList

    def save(self):
        reemplazar_o_agregar(tokenList, 0, self)

class AuthorizationToken:
    def __init__(self, access=None, refresh=None):
        self.access = access
        self.refresh = refresh

    def refresh_credentials(self):
        try:
            responce = requests.post(
                'http://127.0.0.1:8000/api/token/refresh/app/',
                json={
                    "refresh": self.refresh
                }
            )
            if responce.status_code == 200:
                serialized = dict(responce.json())
                self.access = serialized['access']
                self.refresh = serialized['refresh']
                self.save()
        except Exception as err:
            print(f'Error al usar refresh: {err}')

    def save(self):
        reemplazar_o_agregar(credentials, 0, self)

class UserData:
    def __init__(self, id, username, email, img_user):
        self.id = id
        self.username = username
        self.email = email
        self.img_user = img_user

    def save(self):
        reemplazar_o_agregar(userList, 0, self)

    @staticmethod
    def get_user_list():
        return list(userList.values())


userList:dict[int,UserData]={}
tokenList:dict[int,UserToken]={}
credentials:dict[int,AuthorizationToken]={}

def get_user_data(access:str,refresh:str,id:int):
    try:
        responce = requests.get(
            f'http://127.0.0.1:8000/api/users/{id}',
            headers={
                'Authorization':f'Bearer {access}'
            }
        )
        if responce.status_code == 200:
            serialized = dict(responce.json())
            user = UserData(id=serialized['id'], username=serialized['username'], email=serialized['email'],
                            img_user=serialized['img_user'])
            user.save()

            return userList[0]

    except Exception as err:
        print(f'Error: {err}')


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
        page.update()
    except Exception as err:
        print(f'Toggle visibility Error: {err}')

path_user:str = ''

userTokenInput = ft.TextField(
                            text_size=20,
                            autofocus=True,
                            width=250,
                            bgcolor='#d7e3ff',
                            color='#001b3f'
                        )

text_path = ft.Container(
    content=ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(f'La carpeta seleccionada es:',color='#fdfbff')
                ]
            ),
            ft.Row(
                controls=[
                    ft.Text(f'{CARPETA_DESCARGAS}',size=20)
                ]
            )
        ]
    )
)

progres_text = ft.Text(
    '0%',
    visible=False
)

progres_bar = ft.ProgressBar(
    width=600,
    visible=False
)

title_video = ft.Text('Title:',size=15)

img_user = ft.CircleAvatar(
    foreground_image_url='',
    content=ft.Text("FF"),
    background_image_url='#E3C567'
)

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

    def login(e, token: str):
        token_user = UserToken(token=token)
        try:
            responce = requests.post(
                'http://127.0.0.1:8000/api/login/',
                json={
                    'token': token
                }
            )
            if responce.status_code == 200:
                if not token_user.token_exist():
                    token_user.save()
                    print('Enlistado')
                else:
                    print('Ya existe')
                serialized = dict(responce.json())
                tokens = AuthorizationToken(access=serialized['access'], refresh=serialized['refresh'])
                tokens.save()
                user = get_user_data(access=tokens.access, id=serialized['id'], refresh=tokens.refresh)
                login_app.visible = False
                content.visible = True
                img_user.foreground_image_url = ''.join([URL_BASE,userList[0].img_user])
                img_user.content.value = userList[0].username[0:1]
                page.appbar.leading = ft.Row(
                    controls=[
                        img_user,
                        ft.Text(userList[0].username)
                    ]
                )
                page.update()

        except Exception as err:
            print(f'Error responce: {err}')

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
        text_path.content.controls[1].controls[0].value = e.path
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
    page.window_height = 700
    page.window_resizable = False
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.overlay.append(file_picker)
    page.banner = info_banner
    page.appbar = ft.AppBar(
        leading='',
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
            audio = audio.download(
                output_path=path_user if path_user and isinstance(path_user, str) else CARPETA_DESCARGAS,
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

    def upload_video(video,url:str):
        try:
            with requests.Session() as session:
                session.headers.update({'Authorization': f'Bearer {credentials[0].access}'})
                response = session.post(
                    'http://127.0.0.1:8000/api/videos/',
                    json={"titulo": video.title, "usuario": userList[0].id,"url_yt":url}
                )
                if response.status_code == 200:
                    serializer = dict(response.json())
                    print(serializer)
        except Exception as err:
            print(f'Error al subir el video al server:{err}')
    async def Descargar_video_(e):
        try:
            video = yt.YouTube(url.value, on_progress_callback=progres_data)
            title_video.value = f'Title: {video.title}'
            img_video.src = video.thumbnail_url
            page.update()
            stream = video.streams.get_highest_resolution()
            video_down = stream.download(
                output_path=path_user if path_user and isinstance(path_user, str) else CARPETA_DESCARGAS,
                filename_prefix='Video descargado_',
                filename=clean_name(video.title),
                max_retries=200,
                skip_existing=False,
                timeout=500
            )
            upload_video(video,url.value)
            paths, _ = os.path.splitext(video_down)
            os.rename(video_down, paths + '.mp4')
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
                    on_click=lambda e:close_object(e)
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
                        on_click=Descargar_video_,
                        bgcolor='#fdfbff',
                        color='#035ebc'
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
        ),
        visible = False
    )

    login_app = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            'Ingrese su token de Seguridad:',
                            size=20
                        )
                    ]
                ),
                ft.Row(
                    controls=[
                        userTokenInput
                    ]
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            'Enviar',
                            on_click=lambda e: login(e,userTokenInput.value)
                        )
                    ]
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        visible=True
    )

    app = ft.Container(
        content=ft.Stack(
            controls=[
                content,
                login_app
            ]
        )
    )

    page.add(app)

if __name__ == '__main__':
    ft.app(target=main,upload_dir=Path(BASE_DIR / 'uploads') if path_user is None or '' or not isinstance(path_user,str) else path_user)
