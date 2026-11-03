"""
TXD Texture Studio - SAMP / CRMP / GTA San Andreas
Interface gráfica para visualizar e exportar texturas TXD para PNG.

Dependências:
    pip install rwfury pillow

Observação:
    Este programa utiliza a API demonstrada de rwfury:
    Txd.from_file(path), txd.textures e tex.to_rgba().
"""
from __future__ import annotations

import json
import logging
import re
import tkinter as tk
from collections import Counter
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk
from rwfury import Txd

APP_TITLE = "TXD Texture Studio"
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def safe_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\\\|?*\\x00-\\x1f]', "_", str(name or "texture"))
    return name.strip(" .") or "texture"


def get_texture_image(texture, mip_level: int = 0) -> Image.Image:
    """Retorna um mipmap como imagem RGBA."""
    mipmaps, _has_alpha = texture.to_rgba()
    if not mipmaps:
        raise ValueError("A textura não possui dados RGBA.")

    if mip_level < 0 or mip_level >= len(mipmaps):
        raise IndexError("Nível de mipmap indisponível.")

    width = max(1, int(texture.width) >> mip_level)
    height = max(1, int(texture.height) >> mip_level)
    raw = bytes(mipmaps[mip_level])
    expected = width * height * 4

    if len(raw) != expected:
        raise ValueError(
            f"Dados RGBA inválidos no mipmap {mip_level}: "
            f"esperado {expected} bytes, recebido {len(raw)}."
        )

    return Image.frombytes("RGBA", (width, height), raw)


class TxdTextureStudio:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1050x700")
        self.root.minsize(850, 560)

        self.txd = None
        self.txd_path: Path | None = None
        self.textures = []
        self.preview_photo = None
        self.current_image = None
        self.mip_var = tk.IntVar(value=0)
        self.export_all_mips_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Abra um arquivo TXD para começar.")
        self.info_var = tk.StringVar(value="Nenhuma textura selecionada.")

        self._build_ui()

    def _build_ui(self):
        toolbar = ttk.Frame(self.root, padding=10)
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="Abrir TXD", command=self.open_txd).pack(side="left")
        ttk.Button(toolbar, text="Exportar selecionada", command=self.export_selected).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(toolbar, text="Exportar todas", command=self.export_all).pack(
            side="left", padx=(8, 0)
        )

        ttk.Checkbutton(
            toolbar,
            text="Exportar todos os mipmaps",
            variable=self.export_all_mips_var
        ).pack(side="left", padx=14)

        main = ttk.Panedwindow(self.root, orient="horizontal")
        main.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        left = ttk.Frame(main, padding=6)
        right = ttk.Frame(main, padding=10)
        main.add(left, weight=1)
        main.add(right, weight=3)

        ttk.Label(left, text="Texturas do TXD", font=("Arial", 11, "bold")).pack(
            anchor="w", pady=(0, 6)
        )

        list_frame = ttk.Frame(left)
        list_frame.pack(fill="both", expand=True)

        self.texture_list = tk.Listbox(list_frame, exportselection=False)
        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.texture_list.yview
        )
        self.texture_list.configure(yscrollcommand=scrollbar.set)
        self.texture_list.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.texture_list.bind("<<ListboxSelect>>", self.on_select)

        ttk.Label(right, text="Pré-visualização", font=("Arial", 12, "bold")).pack(
            anchor="w"
        )

        self.preview = tk.Label(
            right,
            text="A pré-visualização aparecerá aqui",
            background="#252525",
            foreground="white",
            anchor="center"
        )
        self.preview.pack(fill="both", expand=True, pady=10)

        mip_row = ttk.Frame(right)
        mip_row.pack(fill="x")
        ttk.Label(mip_row, text="Mipmap:").pack(side="left")
        self.mip_spin = ttk.Spinbox(
            mip_row, from_=0, to=0, width=5, textvariable=self.mip_var,
            command=self.refresh_preview
        )
        self.mip_spin.pack(side="left", padx=6)
        ttk.Button(mip_row, text="Atualizar", command=self.refresh_preview).pack(
            side="left"
        )

        ttk.Label(right, textvariable=self.info_var).pack(anchor="w", pady=(8, 0))

        status = ttk.Label(
            self.root, textvariable=self.status_var, relief="sunken", anchor="w",
            padding=(8, 4)
        )
        status.pack(fill="x", side="bottom")

    def open_txd(self):
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo TXD",
            filetypes=[("RenderWare Texture Dictionary", "*.txd"), ("Todos os arquivos", "*.*")]
        )
        if not filename:
            return

        try:
            loaded = Txd.from_file(filename)
            textures = list(loaded.textures)
        except Exception as exc:
            messagebox.showerror("Erro ao abrir TXD", str(exc))
            return

        self.txd = loaded
        self.txd_path = Path(filename)
        self.textures = textures
        self.texture_list.delete(0, tk.END)

        for index, texture in enumerate(self.textures):
            name = getattr(texture, "name", "") or f"Textura {index + 1}"
            self.texture_list.insert(tk.END, f"{index + 1:03d} | {name}")

        self.preview.configure(image="", text="Selecione uma textura")
        self.preview_photo = None
        self.info_var.set(f"{self.txd_path.name} — {len(self.textures)} textura(s)")
        self.status_var.set(f"TXD carregado: {self.txd_path}")
        if self.textures:
            self.texture_list.selection_set(0)
            self.texture_list.event_generate("<<ListboxSelect>>")

    def selected_index(self):
        selection = self.texture_list.curselection()
        return selection[0] if selection else None

    def on_select(self, _event=None):
        index = self.selected_index()
        if index is None:
            return
        self.mip_var.set(0)
        try:
            texture = self.textures[index]
            mipmaps, has_alpha = texture.to_rgba()
            self.mip_spin.configure(to=max(0, len(mipmaps) - 1))
            image = get_texture_image(texture, 0)
            self.current_image = image
            self._show_image(image)

            name = getattr(texture, "name", "") or f"Textura {index + 1}"
            self.info_var.set(
                f"{name} | {texture.width}x{texture.height} | "
                f"{len(mipmaps)} mipmap(s) | Alpha: {'sim' if has_alpha else 'não'}"
            )
            self.status_var.set(f"Visualizando textura {index + 1}/{len(self.textures)}")
        except Exception as exc:
            self.current_image = None
            self.preview.configure(image="", text=f"Não foi possível visualizar:\n{exc}")
            self.preview_photo = None
            self.info_var.set("Erro ao ler textura.")

    def _show_image(self, image: Image.Image):
        self.root.update_idletasks()
        max_w = max(250, self.preview.winfo_width() - 24)
        max_h = max(200, self.preview.winfo_height() - 24)
        display = image.copy()
        display.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

        # Fundo quadriculado para facilitar a visualização da transparência.
        checker = Image.new("RGB", display.size, "#b8b8b8")
        pixels = checker.load()
        tile = 12
        for y in range(display.height):
            for x in range(display.width):
                if ((x // tile) + (y // tile)) % 2:
                    pixels[x, y] = (225, 225, 225)
        checker.paste(display, mask=display.getchannel("A"))
        self.preview_photo = ImageTk.PhotoImage(checker)
        self.preview.configure(image=self.preview_photo, text="")

    def refresh_preview(self):
        index = self.selected_index()
        if index is None:
            return
        try:
            image = get_texture_image(self.textures[index], int(self.mip_var.get()))
            self.current_image = image
            self._show_image(image)
        except Exception as exc:
            messagebox.showwarning("Mipmap indisponível", str(exc))

    def _export_one(self, texture, output_dir: Path, used_names: Counter):
        original_name = getattr(texture, "name", "") or "texture"
        base = safe_filename(original_name)
        used_names[base.lower()] += 1
        if used_names[base.lower()] > 1:
            base = f"{base}_{used_names[base.lower()]}"

        mipmaps, has_alpha = texture.to_rgba()
        levels = range(len(mipmaps)) if self.export_all_mips_var.get() else range(min(1, len(mipmaps)))
        files = []

        for level in levels:
            image = get_texture_image(texture, level)
            filename = f"{base}_mip{level}.png" if self.export_all_mips_var.get() else f"{base}.png"
            destination = output_dir / filename
            image.save(destination, "PNG", optimize=True)
            files.append({
                "file": filename,
                "width": image.width,
                "height": image.height,
                "mipmap": level
            })

        return {
            "name": str(original_name),
            "width": int(texture.width),
            "height": int(texture.height),
            "has_alpha": bool(has_alpha),
            "mipmap_count": len(mipmaps),
            "files": files
        }

    def export_selected(self):
        index = self.selected_index()
        if index is None:
            messagebox.showinfo("Selecionar textura", "Selecione uma textura primeiro.")
            return
        output = filedialog.askdirectory(title="Escolher pasta de exportação")
        if not output:
            return

        try:
            result = self._export_one(
                self.textures[index], Path(output), Counter()
            )
            self.status_var.set(f"Textura exportada para {output}")
            messagebox.showinfo("Exportação concluída", f"{len(result['files'])} arquivo(s) exportado(s).")
        except Exception as exc:
            messagebox.showerror("Erro na exportação", str(exc))

    def export_all(self):
        if not self.textures:
            messagebox.showinfo("TXD vazio", "Abra um TXD que contenha texturas.")
            return
        output = filedialog.askdirectory(title="Escolher pasta de exportação")
        if not output:
            return

        output_dir = Path(output)
        output_dir.mkdir(parents=True, exist_ok=True)
        used_names = Counter()
        report = {
            "source": str(self.txd_path) if self.txd_path else None,
            "texture_count": len(self.textures),
            "success": 0,
            "failed": 0,
            "textures": []
        }

        for index, texture in enumerate(self.textures, start=1):
            try:
                report["textures"].append(
                    self._export_one(texture, output_dir, used_names)
                )
                report["success"] += 1
                self.status_var.set(f"Exportando {index}/{len(self.textures)}...")
                self.root.update_idletasks()
            except Exception as exc:
                report["failed"] += 1
                report["textures"].append({
                    "name": str(getattr(texture, "name", "texture")),
                    "error": str(exc)
                })

        report_path = output_dir / "txd_report.json"
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        summary = (
            f"Texturas: {report['texture_count']}\n"
            f"Sucesso: {report['success']}\n"
            f"Falhas: {report['failed']}\n\n"
            f"Relatório: {report_path}"
        )
        self.status_var.set("Exportação finalizada.")
        messagebox.showinfo("Exportação concluída", summary)


def main():
    root = tk.Tk()
    TxdTextureStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
