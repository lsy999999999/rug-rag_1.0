"""
Simple Document Converter - Convert legacy formats for Docling
"""

import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.table import Table

console = Console()


class DocumentConverter:
    DOCLING_SUPPORTED = {".pdf", ".docx", ".pptx", ".xlsx"}
    CONVERTIBLE = {".doc": ".docx", ".xls": ".xlsx", ".ppt": ".pptx"}
    CLEANUP = {".DS_Store", ".rar", ".zip", ".tmp"}

    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.log = []
        self.cleanup_commands = []

    def scan_files(self):
        files_by_ext = defaultdict(list)
        for file_path in self.data_dir.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                files_by_ext[ext].append(file_path)
        return dict(files_by_ext)

    def show_analysis(self, files_by_ext):
        table = Table(title="📁 File Analysis")
        table.add_column("Extension", style="cyan")
        table.add_column("Count", justify="right", style="magenta")
        table.add_column("Action", style="yellow")

        for ext, files in sorted(files_by_ext.items()):
            count = len(files)
            if ext in self.DOCLING_SUPPORTED:
                action = "✅ Keep"
            elif ext in self.CONVERTIBLE:
                action = f"🔄 Convert to {self.CONVERTIBLE[ext]}"
            elif ext in self.CLEANUP:
                action = "📝 Log for cleanup"
            else:
                action = "❓ Skip"

            table.add_row(ext or "(no ext)", str(count), action)

        console.print(table)

    def convert_doc_to_docx(self, doc_path):
        result = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "docx",
                "--outdir",
                str(doc_path.parent),
                str(doc_path),
            ],
            capture_output=True,
        )

        if result.returncode == 0:
            self.log.append(f"✅ {doc_path.name} → {doc_path.stem}.docx")
            self.cleanup_commands.append(f"rm '{doc_path}'")
            return True
        return False

    def convert_xls_to_xlsx(self, xls_path):
        import pandas as pd

        df = pd.read_excel(xls_path)
        xlsx_path = xls_path.with_suffix(".xlsx")
        df.to_excel(xlsx_path, index=False)

        self.log.append(f"✅ {xls_path.name} → {xlsx_path.name}")
        self.cleanup_commands.append(f"rm '{xls_path}'")
        return True

    def convert_ppt_to_pptx(self, ppt_path):
        result = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pptx",
                "--outdir",
                str(ppt_path.parent),
                str(ppt_path),
            ],
            capture_output=True,
        )

        if result.returncode == 0:
            self.log.append(f"✅ {ppt_path.name} → {ppt_path.stem}.pptx")
            self.cleanup_commands.append(f"rm '{ppt_path}'")
            return True
        return False

    def process_files(self, files_by_ext):
        # Install dependencies
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pandas", "openpyxl"]
        )

        # Convert files
        for ext, files in files_by_ext.items():
            if ext not in self.CONVERTIBLE:
                continue

            for file_path in track(files, description=f"Converting {ext} files"):
                if ext == ".doc":
                    self.convert_doc_to_docx(file_path)
                elif ext == ".xls":
                    self.convert_xls_to_xlsx(file_path)
                elif ext == ".ppt":
                    self.convert_ppt_to_pptx(file_path)

        # Log cleanup files (don't delete)
        for ext, files in files_by_ext.items():
            if ext in self.CLEANUP:
                for file_path in files:
                    self.log.append(f"📝 Cleanup needed: {file_path.name}")
                    self.cleanup_commands.append(f"rm '{file_path}'")

    def save_log(self):
        # Save conversion log
        log_file = Path("convert.log")
        with open(log_file, "w") as f:
            for entry in self.log:
                f.write(f"{entry}\n")
        console.print(f"📄 Log saved: {log_file}")

        # Save cleanup script
        if self.cleanup_commands:
            cleanup_file = Path("cleanup.sh")
            with open(cleanup_file, "w") as f:
                f.write("#!/bin/bash\n")
                f.write("# Run this script to remove original and cleanup files\n")
                f.write("# Review the commands below before running!\n\n")
                for cmd in self.cleanup_commands:
                    f.write(f"{cmd}\n")
            cleanup_file.chmod(0o755)
            console.print(f"🗑️  Cleanup script: {cleanup_file}")
            console.print("   Review and run: ./cleanup.sh")

    def run(self):
        console.print(Panel("🔧 Document Converter", style="blue"))

        files_by_ext = self.scan_files()
        self.show_analysis(files_by_ext)

        if input("\n🚀 Convert files? (y/N): ").lower() == "y":
            self.process_files(files_by_ext)

            if self.log:
                console.print("\n📋 Conversion Log:")
                for entry in self.log[-10:]:  # Show last 10
                    console.print(entry)
                self.save_log()

            console.print("\n✅ Conversion done! Check cleanup.sh to remove originals.")


if __name__ == "__main__":
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    converter = DocumentConverter(data_dir)
    converter.run()


