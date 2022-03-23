import StreetViewAPI
import PySimpleGUI as sg
import threading
'''
https://github.com/ronaldoussoren/py2app/issues/358
fixed the issue with multiprocessing and py2app
'''
import sys
sys.frozen = False

THREAD_END = "-END-"

res_data = ['1920x600', '1920x1200']


def the_thread(window, s, e, k):
    """
    The thread that communicates with the application through the window's events.

    Once a second wakes and sends a new event and associated value to the window
    """
    StreetViewAPI.set_GOOGLE_STREETVIEW_API_KEY(k)
    window.write_event_value(
        THREAD_END, StreetViewAPI.construct_video(s, e))


def main():
    """
    The demo will display in the multiline info about the event and values dictionary as it is being
    returned from window.read()
    Every time "Start" is clicked a new thread is started
    Try clicking "Dummy" to see that the window is active while the thread stuff is happening in the background
    """
    sg.theme("Black")
    sg.user_settings_filename(path='.')

    layout = [
        [sg.T("API Key: ", font="Any 16"), sg.Input(
            sg.user_settings_get_entry('-APIKEY-', ''), key="-API-", focus=True, do_not_clear=True, font="Any 16")],
        [sg.Radio(res_data[0], "RES", default=True,
                  key="-RES-", font="Any 16")],
        [sg.Radio(res_data[1], "RES", default=False, font="Any 16")],
        [sg.Text("Console:", font="Any 16")],
        [
            sg.Multiline(
                size=(90, 40),
                key="-ML-",
                autoscroll=True,
                reroute_stdout=True,
                write_only=True,
                reroute_cprint=True,
            )
        ],
        [sg.T("起點座標： ", font="Any 16"), sg.Input(
            key="-START-", focus=True, do_not_clear=True, font="Any 16")],
        [sg.T("終點座標： ", font="Any 16"), sg.Input(
            key="-END-", focus=True, do_not_clear=True, font="Any 16")],
        [sg.Button("Run", bind_return_key=True, font="Any 16"),
         sg.Button("Exit", font="Any 16")],
        [sg.T("下載完成檔案會儲存於Movies資料夾的StreetViewVideos中", font="Any 16")]
    ]

    window = sg.Window("GoogleStreetView Video Generator", layout)

    while True:  # Event Loop
        event, values = window.read()
        sg.cprint(event, values)
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        if event.startswith("Run"):
            sg.user_settings_set_entry('-APIKEY-', values["-API-"])
            s = values["-START-"]
            e = values["-END-"]
            k = values["-API-"]
            threading.Thread(
                target=the_thread, args=(window, s, e, k), daemon=True
            ).start()
        if event == THREAD_END:
            sg.cprint(f"下載圖資結束，請按下\"Exit\"鈕退出或是繼續下載", colors="white on green")

    window.close()


if __name__ == "__main__":
    main()
