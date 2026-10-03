from pathlib import Path
from urllib.parse import quote
from zipfile import ZipFile, ZIP_DEFLATED
import re
import shutil

from mkdocs.exceptions import PluginError

def natural_key(value):
    return [
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", str(value))
    ]

def label(value):
    return re.sub(r"^\d+[-_ ]*", "", value).replace("-", " ")

def note_title(path):
    text = path.read_text(encoding="utf-8-sig")
    match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1) if match else label(path.stem)

def md_link(text, path):
    safe_text = text.replace("[", r"\[").replace("]", r"\]")
    return f"[{safe_text}]({quote(str(path), safe='/')})"

def cards(items):
    lines = ['<div class="grid cards" markdown>', ""]
    for title, description, target in items:
        lines.append(
            f"- **{md_link(title, target)}**\n\n"
            f"    {description}\n"
        )
    lines.append("</div>")
    return "\n".join(lines)

def write_page(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def on_config(config):
    root = Path(config.config_file_path).parent
    source = root / "notes"
    docs = Path(config["docs_dir"])

if not source.exists():
        raise PluginError("Create the notes folder and add a Markdown note.")

files = sorted(
        source.rglob("*.md"),
        key=lambda p: natural_key(p.relative_to(source)),
    )

if not files:
        raise PluginError("No .md files were found inside notes.")

groups = {}

for file in files:
        parts = file.relative_to(source).parts
        if len(parts) != 3 or file.name.lower() == "index.md":
            raise PluginError(
                f"Invalid note path: {file.relative_to(source)}. "
                "Use notes/course/chapter/session.md; "
                "index.md is reserved."
            )

course, chapter, _ = parts
        groups.setdefault(course, {}).setdefault(chapter, []).append(file)

docs.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, docs / "notes", dirs_exist_ok=True)
    shutil.copytree(root / "web", docs / "assets", dirs_exist_ok=True)

navigation = [{"خانه": "index.md"}]
    home_cards = []

for course, chapters in groups.items():
        course_name = label(course)
        course_index = f"notes/{course}/index.md"
        course_nav = [{"نمای کلی": course_index}]
        chapter_cards = []
        session_count = sum(len(items) for items in chapters.values())

home_cards.append((
            course_name,
            f"{len(chapters)} فصل · {session_count} جلسه",
            course_index,
        ))

for chapter, sessions in chapters.items():
            chapter_name = label(chapter)
            chapter_index = f"notes/{course}/{chapter}/index.md"
            chapter_nav = [{"نمای کلی": chapter_index}]
            session_cards = []

chapter_cards.append((
                chapter_name,
                f"{len(sessions)} جلسه برای مطالعه",
                f"{chapter}/index.md",
            ))

for file in sessions:
                title = note_title(file)
                relative = file.relative_to(source).as_posix()
                destination = docs / "notes" / relative
                content = file.read_text(encoding="utf-8-sig")

# This marker activates sharing and reading history.
                write_page(
                    destination,
                    content + '\n\n<div data-note-page></div>\n',
                )

chapter_nav.append({title: f"notes/{relative}"})
                session_cards.append((
                    title,
                    "بازکردن جزوه و شروع مطالعه",
                    file.name,
                ))

write_page(
                docs / chapter_index,
                f"# {chapter_name}\n\n"
                f"درس {course_name} · {len(sessions)} جلسه\n\n"
                + cards(session_cards),
            )

course_nav.append({chapter_name: chapter_nav})

write_page(
            docs / course_index,
            f"# {course_name}\n\n"
            "از اینجا فصل موردنظرت را انتخاب کن.\n\n"
            + cards(chapter_cards),
        )

navigation.append({course_name: course_nav})

downloads = docs / "downloads"
    downloads.mkdir(exist_ok=True)

with ZipFile(
        downloads / "notes.zip", "w", compression=ZIP_DEFLATED
    ) as archive:
        for file in sorted(source.rglob("*")):
            if file.is_file():
                archive.write(file, file.relative_to(source).as_posix())

home = (
        "# جزوهخانهٔ من\n\n"
        '<div class="study-hero" markdown>\n\n'
        "## هر جلسه، یک قدم جلوتر 🌱\n\n"
        "اینجا قرار نیست همهچیز را یکروزه یاد بگیری؛ "
        "فقط کافی است از جلسهٔ بعدی شروع کنی.\n\n"
        f"**{len(groups)} درس · {len(files)} جلسهٔ ثبتشده**\n\n"
        '<a id="continue-reading" class="md-button" hidden>'
        "ادامهٔ آخرین مطالعه</a>\n\n"
        "</div>\n\n"
        "## درسها\n\n"
        + cards(home_cards)
        + "\n\n---\n\n"
        "[دریافت نسخهٔ کامل جزوهها](downloads/notes.zip)"
        "{ .md-button }\n"
    )

write_page(docs / "index.md", home)
    config["nav"] = navigation
    return config
