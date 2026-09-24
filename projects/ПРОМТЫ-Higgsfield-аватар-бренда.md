# Промты: Higgsfield, аватар бренда

Библиотека @aa.rashchupkina, август 2026. Двенадцать промтов, четыре раздела,
два якоря. Промты генерации пишутся на английском.

**Статус: рабочий метод бренда Infinity Story.** Любая генерация изображений и
видео для аккаунта собирается по этим промтам и по формуле из промта 12.

## Правило применения в Infinity Story

Аудит показал, что подписки бренду даёт лицо основательницы, а не красивая
картинка. Поэтому генерация занимает строго свою территорию:

**Можно:** фоны под наложение реального фото вещи, предметные кадры фактуры,
заставки рубрик, баннеры и обложки подборок, атмосферные кадры сезона, оживление
статичных кадров для сториз.

**Нельзя:** заменять Алёну в кадре, показывать сгенерированную одежду как нашу
вещь, изображать посадку на фигуре, подставлять генерацию в доказательные
форматы (ткань, швы, размеры). Там, где зрительница проверяет качество, работает
только камера.

---

## Раздел 01. Два якоря

Якоря копируются без изменений в начало каждого промта. Именно они дают одного и
того же человека и один и тот же визуальный язык от кадра к кадру. Меняется
только сцена.

### Якорь персонажа

Правится один раз под нужную внешность. [Уточнить: править ли под внешность
Алёны или оставить обобщённый образ. Если аватар похож на Алёну, но это не она,
в доказательных форматах он не используется вообще.]

```
CHARACTER ANCHOR:
a woman in her early thirties, warm light skin with natural texture,
soft minimal makeup, straight dark brown hair past the shoulders with a
centre part, calm confident expression, natural eyebrows, delicate thin
gold hoop earrings, no other jewellery
```

По-русски: женщина слегка за тридцать, тёплый светлый тон кожи с натуральной
текстурой, лёгкий макияж, прямые тёмно-русые волосы ниже плеч с пробором
посередине, спокойное уверенное выражение, естественные брови, тонкие золотые
серьги-кольца, других украшений нет.

### Якорь стиля

Не правится: это визуальный язык бренда.

```
STYLE ANCHOR:
soft diffused natural daylight, warm neutral palette of cream, sand,
peach and soft brown, gentle film grain, shallow depth of field,
85mm portrait lens, editorial minimalism, quiet calm mood,
no harsh shadows, no saturated colours
```

По-русски: мягкий рассеянный дневной свет, тёплая нейтральная палитра: крем,
песок, персик, мягкий коричневый. Лёгкое плёночное зерно, малая глубина
резкости, портретный объектив 85 мм, эдиториальный минимализм, спокойное тихое
настроение, без жёстких теней и насыщенных цветов.

### Негатив

Дописывается в поле negative prompt.

```
NEGATIVE:
extra fingers, deformed hands, warped fabric seams, plastic skin,
over-sharpened, heavy HDR, neon colours, cluttered background,
text, watermark, distorted logo, duplicated limbs
```

---

## Раздел 02. Создание аватара

### Промт 01. Лист персонажа

Первое, что генерируется. Из него берётся референс для всего остального.

```
CHARACTER ANCHOR + STYLE ANCHOR +
character reference sheet, same woman repeated in one image,
four views: front portrait, three-quarter portrait, profile, waist-up front,
plain warm cream background, even soft light, neutral expression,
consistent face across all four views, no props
```

Дальше в Higgsfield лучший кадр сохраняется как референс персонажа и
подставляется во все следующие генерации. Без этого шага лицо будет плыть.

### Промт 02. Портрет для аватара профиля

```
CHARACTER ANCHOR + STYLE ANCHOR +
close-up portrait, head and shoulders, looking slightly off camera,
wearing a plain cream knit top, warm peach background wall,
soft window light from the left, subtle skin texture visible,
shot on 85mm at f2, editorial fashion portrait
```

Формат 1:1 для профиля, 4:5 для ленты.

### Промт 03. Кадр для обложки рилса

```
CHARACTER ANCHOR + STYLE ANCHOR +
full body, standing relaxed near a large window,
wearing simple neutral beige clothing with no visible branding,
minimal interior with cream walls and light wooden floor,
soft morning light, negative space on the [left / right / bottom] for text,
vertical composition, 9:16
```

Место под текст задаётся словами negative space: без него тезис некуда ставить.

### Промт 04. Сезонное настроение

```
CHARACTER ANCHOR + STYLE ANCHOR +
editorial mood shot, [autumn / spring] atmosphere,
wearing layered neutral tones, soft oversized silhouette without branding,
[warm indoor setting with linen curtains / quiet street with soft
overcast light], calm introspective mood, film photography feel
```

Одежда описывается силуэтом и тоном, а не конкретной вещью из ассортимента.

### Промт 05. Кадр в движении

```
CHARACTER ANCHOR + STYLE ANCHOR +
candid moment, walking through a bright minimal space,
fabric moving naturally, hair in motion,
slight motion blur on the background, sharp on the subject,
warm neutral wardrobe, unposed natural gesture, 9:16 vertical
```

---

## Раздел 03. Сцены без модели

Самая безопасная и самая недооценённая часть: здесь генерация не конкурирует с
реальной вещью и работает в полную силу.

### Промт 06. Фон под наложение

```
STYLE ANCHOR +
empty minimal interior, cream plaster walls, light oak floor,
one soft shadow from a window frame on the wall,
no furniture except a simple wooden stool,
wide empty space in the centre of the frame,
warm neutral colour grade, [4:5 / 9:16]
```

### Промт 07. Предметный кадр ткани

```
STYLE ANCHOR +
extreme close-up of [linen / wool / cotton] fabric folds,
natural texture and weave visible, warm sand colour,
soft raking light from the side revealing the surface,
macro lens, shallow focus, no stitching or garment construction visible
```

Кадр про фактуру и настроение. Реальные швы и посадка снимаются камерой.

### Промт 08. Заставка рубрики

```
STYLE ANCHOR +
flat minimal composition, warm peach paper background,
a few simple objects arranged with generous space:
[folded fabric / a pair of scissors / spools of thread],
soft top-down light, subtle shadows, negative space in the upper third,
1:1 square
```

Одна и та же заставка каждую неделю делает рубрику узнаваемой.

### Промт 09. Баннер настроения

```
STYLE ANCHOR +
wide atmospheric shot, warm minimal space filled with soft daylight,
sheer curtain moving slightly, dust particles in the light beam,
no people, no garments,
generous empty area on the left for typography, 16:9
```

---

## Раздел 04. Видео и починка

### Промт 10. Оживление кадра

Берётся готовое изображение и промт движения.

```
subtle natural motion, fabric swaying gently in a light breeze,
soft hair movement, slow almost imperceptible camera push in,
everything else static, no scene change, no new objects,
loopable, 3 to 5 seconds
```

Меньше движения значит меньше артефактов. Резкие жесты ломают лицо и руки.

### Промт 11. Починка неудачной генерации

Не переписывать промт целиком. Менять по одному:

| Что не так | Что добавить или убрать |
| --- | --- |
| Лицо поплыло | Подставить референс персонажа и убрать половину деталей сцены |
| Пластиковая кожа | Добавить natural skin texture, film grain, убрать sharp |
| Кривые руки | Убрать руки из кадра или сменить кадрирование на waist-up |
| Слишком глянцево | Добавить overcast light, matte finish, muted colours |
| Цвета ушли в холод | Добавить warm colour grade, golden neutral tones |
| Фон перегружен | Добавить minimal empty background, negative space |

Правило: одна правка на генерацию. Иначе непонятно, что сработало.

### Промт 12. Сборка промта под новую задачу

Собирается по формуле, в этом порядке:

1. CHARACTER ANCHOR, если в кадре человек
2. STYLE ANCHOR
3. Что происходит: поза, действие, кадрирование
4. Где: пространство, поверхности, предметы
5. Свет: откуда, какой, мягкий или направленный
6. Оптика: фокусное, глубина резкости
7. Композиция: где пустое место под текст, формат
8. NEGATIVE в отдельное поле

Пропущенный пункт 5 или 6 это девяносто процентов неудачных кадров.

**Перед первой генерацией** прогоняется промт 01 и сохраняется референс
персонажа. Все остальные промты без него дадут разных людей, и вся серия
развалится.
