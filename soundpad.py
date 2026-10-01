import os
import threading
import customtkinter as ctk
import pygame
import keyboard
from tkinterdnd2 import TkinterDnD, DND_FILES

# Ses motorunu hazırla
pygame.mixer.init()

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SoundpadApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("Soundpad")
        self.geometry("520x620")
        self.minsize(450, 500)

        # Ses kayıtları listesi: [{'name': ..., 'path': ..., 'hotkey': ...}]
        self.sound_items = []
        self.listening_for_index = None

        self.setup_ui()
        self.setup_dnd()

    def setup_ui(self):
        # Üst Başlık & Bırakma Alanı
        self.drop_frame = ctk.CTkFrame(self, height=90, corner_radius=10, border_width=2, border_color="#3B8ED0")
        self.drop_frame.pack(fill="x", padx=20, pady=15)
        self.drop_frame.pack_propagate(False)

        self.drop_label = ctk.CTkLabel(
            self.drop_frame,
            text="Ses Dosyalarını Buraya Sürükleyip Bırakın\n(.mp3, .wav, .ogg)",
            font=("Segoe UI", 13, "bold"),
            text_color="#9CA3AF"
        )
        self.drop_label.pack(expand=True)

        # Liste Alanı (Kaydırılabilir)
        self.list_frame = ctk.CTkScrollableFrame(self, label_text="Ses Listesi ve Kısayollar")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Alt Kontrol Barı
        self.bottom_bar = ctk.CTkFrame(self, height=45)
        self.bottom_bar.pack(fill="x", padx=20, pady=(0, 15))

        self.stop_btn = ctk.CTkButton(
            self.bottom_bar,
            text="Sesi Durdur (ESC)",
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self.stop_all_sounds
        )
        self.stop_btn.pack(side="right", padx=10, pady=8)

        # Global ESC ile sesi durdur
        keyboard.add_hotkey("esc", self.stop_all_sounds)

    def setup_dnd(self):
        # Sürükle bırak olayını pencereye bağla
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.on_file_drop)

    def on_file_drop(self, event):
        raw_paths = event.data
        # Windows path ayrıştırma (süslü parantezli yollar için temizlik)
        paths = self.parse_drop_paths(raw_paths)

        valid_extensions = (".mp3", ".wav", ".ogg")
        for path in paths:
            if path.lower().endswith(valid_extensions) and os.path.exists(path):
                self.add_sound_entry(path)

    def parse_drop_paths(self, raw_data):
        paths = []
        current = ""
        in_curly = False
        for char in raw_data:
            if char == "{":
                in_curly = True
            elif char == "}":
                in_curly = False
            elif char == " " and not in_curly:
                if current.strip():
                    paths.append(current.strip())
                current = ""
            else:
                current += char
        if current.strip():
            paths.append(current.strip())
        return paths

    def add_sound_entry(self, file_path):
        name = os.path.basename(file_path)
        item_data = {
            "name": name,
            "path": file_path,
            "hotkey": None,
            "btn_hotkey": None
        }
        idx = len(self.sound_items)
        self.sound_items.append(item_data)
        self.render_row(item_data, idx)

    def render_row(self, item, idx):
        row = ctk.CTkFrame(self.list_frame, corner_radius=6)
        row.pack(fill="x", pady=4, padx=5)

        # Oynat butonu ve Ses İsmi
        play_btn = ctk.CTkButton(
            row,
            text=f"▶  {item['name'][:22]}",
            anchor="w",
            width=200,
            command=lambda p=item["path"]: self.play_sound(p)
        )
        play_btn.pack(side="left", padx=8, pady=6)

        # Kısayol Tuşu Belirleme Butonu
        hotkey_btn = ctk.CTkButton(
            row,
            text="Tuş Ata",
            width=90,
            fg_color="#374151",
            hover_color="#4B5563",
            command=lambda i=idx: self.start_listening_hotkey(i)
        )
        hotkey_btn.pack(side="right", padx=8, pady=6)
        item["btn_hotkey"] = hotkey_btn

    def start_listening_hotkey(self, index):
        if self.listening_for_index is not None:
            return

        self.listening_for_index = index
        target_btn = self.sound_items[index]["btn_hotkey"]
        target_btn.configure(text="Tuşa Basın...", fg_color="#F59E0B")

        # Tuş yakalama arka planda thread ile bekletilir
        threading.Thread(target=self._capture_key, args=(index,), daemon=True).start()

    def _capture_key(self, index):
        key_event = keyboard.read_event(suppress=False)
        while key_event.event_type != keyboard.KEY_DOWN:
            key_event = keyboard.read_event(suppress=False)

        assigned_key = key_event.name.lower()

        # UI güncellemesini ana thread üzerinde yap
        self.after(0, lambda: self.bind_hotkey(index, assigned_key))

    def bind_hotkey(self, index, key):
        item = self.sound_items[index]

        # Eski kısayol varsa kaldır
        if item["hotkey"]:
            try:
                keyboard.remove_hotkey(item["hotkey"])
            except KeyError:
                pass

        item["hotkey"] = key
        item["btn_hotkey"].configure(text=f"[{key.upper()}]", fg_color="#10B981")

        # Yeni global kısayolu kaydet
        keyboard.add_hotkey(key, lambda p=item["path"]: self.play_sound(p))
        self.listening_for_index = None

    def play_sound(self, file_path):
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Oynatma hatası: {e}")

    def stop_all_sounds(self):
        pygame.mixer.music.stop()


if __name__ == "__main__":
    app = SoundpadApp()
    app.mainloop()