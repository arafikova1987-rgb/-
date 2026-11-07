# Инструменты монтажа — что стоит и как вызывать

Папка: `video-tools/` внутри репозитория. `.venv` и `node_modules` не хранятся
в git (см. `.gitignore`) — они эфемерны и пересобираются автоматически.

## Окружение

Эта сессия работает в облачном окружении **video-editing-network**
(персональное, привязано к репозиторию `arafikova1987-rgb/-`), а не в Default.
Так сделано, чтобы открыть доступ к нужным хостам (YouTube/TikTok/Instagram,
CDN для моделей и библиотек) не трогая настройки всех остальных проектов.

В нём настроен **setup-script**, который при каждом новом (свежем) контейнере
автоматически ставит все инструменты заново:
`.venv` + `pip install yt-dlp faster-whisper "av<19"` + `npm install remotion
@remotion/cli @remotion/renderer react react-dom hyperframes` в этой папке.
Если открываешь новую сессию и инструментов нет — значит контейнер ещё не
пересобрался со скриптом; просто подожди первого старта или попроси Claude
прогнать установку руками.

## 1. FFmpeg

Системный, уже стоит в образе: `/usr/bin/ffmpeg` (6.1.1, собран с `--enable-libass`
— субтитры через libass работают из коробки, отдельный `ffmpeg-full` не нужен).

```bash
ffmpeg -i IN.mp4 -vf "subtitles=sub.srt" OUT.mp4
```

## 2. faster-whisper (Whisper)

```bash
video-tools/.venv/bin/python -c "
from faster_whisper import WhisperModel
model = WhisperModel('small', device='cpu', compute_type='int8')
segments, info = model.transcribe('audio.wav', word_timestamps=True)
for s in segments:
    print(s.start, s.end, s.text)
"
```
Модели (`tiny`/`small`/`medium`/…) скачиваются при первом запуске с
huggingface.co — для этого в окружении открыты хосты
`huggingface.co`, `cdn-lfs.huggingface.co`, `cdn-lfs-us-1.hf.co`,
`cas-server.xethub.hf.co`, `us.aws.cdn.hf.co`.

## 3. yt-dlp

```bash
video-tools/.venv/bin/yt-dlp "ССЫЛКА_НА_РОЛИК"
```
**Важное ограничение:** метаданные (название, описание, субтитры) и короткие
файлы скачиваются нормально. Сама видеодорожка с YouTube отдаётся с
динамических поддоменов вида `rr4---sn-xxxxx.googlevideo.com`, которые нельзя
заранее прописать в список разрешённых хостов (нет wildcard-доступа в
песочнице) — поэтому полноценная закачка видео с YouTube в этом облачном
контейнере не гарантирована. Для TikTok/Instagram/Vimeo основные хосты уже
открыты и стоит попробовать первым делом.

## 4. Remotion

```bash
cd video-tools
npx remotion render path/to/Root.jsx <composition-id> \
  --browser-executable=/opt/pw-browsers/chromium \
  --output=out.mp4
```
Рендерер использует предустановленный Chromium из `/opt/pw-browsers/chromium`
(отдельно Remotion свой Chrome не ставит).

## 5. HyperFrames

```bash
cd video-tools
npx hyperframes init my-video
cd my-video
npm run render
```
Шаблоны по умолчанию подключают GSAP с `cdn.jsdelivr.net` — хост открыт в
окружении.

## 6. Piratex MCP

На момент установки (2026-11-07) коннектор **не подключён** — инструментов
`trending_now` / `xray_video` в сессии нет. Подключить может только владелец
аккаунта:

- в приложении Claude: Настройки → Коннекторы → «Добавить свой коннектор»,
  адрес `https://piratex.ai/api/mcp`, затем войти на piratex.ai и нажать
  «Разрешить»;
- в терминале (если установлен Claude Code CLI):
  ```bash
  claude mcp add --transport http piratex https://piratex.ai/api/mcp
  claude mcp login piratex
  ```

Назначение: `trending_now` — что залетает в нише (Reels/TikTok/Shorts) прямо
сейчас; `xray_video` — речь слово в слово, описание и топ комментариев по
ссылке на конкретный ролик. Оба тратят кредиты тарифа — вызывать только по
запросу.

## Проверка после установки (2026-11-07)

| Инструмент | Версия | Работает? |
|---|---|---|
| FFmpeg | 6.1.1 (libass) | ✅ вшил субтитр в тестовое видео |
| faster-whisper | 1.2.1 | ✅ распознал тестовую речь с таймкодами слов |
| yt-dlp | 2026.10.26 | ⚠️ метаданные/описание — да; сама видеодорожка с YouTube — нет (см. выше) |
| Remotion | 4.0.541 | ✅ собрал тестовый mp4 |
| HyperFrames | 0.9.20 | ✅ отрендерил демо-проект в mp4 |
| Piratex MCP | — | ❌ не подключён, нужно подключить вручную |
