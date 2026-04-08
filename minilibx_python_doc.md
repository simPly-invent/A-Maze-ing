# Documentation MiniLibX — Adaptée pour Python (École 42)

> Traduction et adaptation de la doc originale de harm-smits.  
> Tous les exemples C ont été réécrits en Python avec la binding `mlx` Python (même API, même logique).

---

## Table des matières

1. [Introduction](#1-introduction)
2. [Bien démarrer](#2-bien-démarrer)
3. [Les couleurs](#3-les-couleurs)
4. [Les événements](#4-les-événements)
5. [Les hooks](#5-les-hooks)
6. [Les boucles](#6-les-boucles)
7. [Les images](#7-les-images)
8. [La synchronisation (Sync)](#8-la-synchronisation-sync)
9. [Épilogue](#9-épilogue)
10. [Prototypes (référence complète)](#10-prototypes-référence-complète)

---

## 1. Introduction

MiniLibX est une petite bibliothèque graphique qui te permet de faire les choses les plus basiques pour afficher quelque chose à l'écran, sans avoir besoin de connaître X-Window ou Cocoa. Elle fournit : une création de fenêtres simple, un outil de dessin minimaliste, des fonctions pour manipuler les images, et un système de gestion d'événements.

### X-Window

X-Window est un système graphique orienté réseau pour Unix. C'est utilisé par exemple pour les connexions à des bureaux distants (TeamViewer en est un exemple classique).

### macOS

Sur macOS, l'accès graphique à l'écran passe par le framework natif d'Apple, qui gère l'écran, le système de fenêtres, le clavier et la souris. MiniLibX s'enregistre auprès de ce framework pour fonctionner.

---

## 2. Bien démarrer

### Installation

#### Sur Linux

La version Linux de MiniLibX est disponible ici : [minilibx-linux (GitHub 42Paris)](https://github.com/42Paris/minilibx-linux).

Elle nécessite `xorg`, `x11` et `zlib`. Sur Ubuntu :

```bash
sudo apt-get update && sudo apt-get install xorg libxext-dev zlib1g-dev libbsd-dev
```

Lance ensuite le script `configure` dans le dossier du repo.

Pour la version Python, installe la binding :

```bash
pip install mlx  # ou le nom exact du paquet fourni par ton école
```

#### Sur Windows 10 (WSL2)

WSL2 n'a pas de couche graphique native. Il faut passer par **Xming** (ou VcXsrv) et configurer la variable `DISPLAY` :

```bash
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
```

#### Sur Windows 11 (WSLg)

WSLg supporte nativement les applis graphiques Linux. Suis le guide officiel Microsoft pour activer WSLg, puis compile et lance directement.

---

### Initialisation

En C, on inclut `<mlx.h>` et on appelle `mlx_init()`.  
En Python, on importe le module et on appelle la même fonction.

**C (original) :**
```c
#include <mlx.h>

int main(void)
{
    void *mlx;
    mlx = mlx_init();
}
```

**Python (adapté) :**
```python
import mlx

mlx_ptr = mlx.init()
```

`mlx.init()` établit la connexion au système graphique et retourne un pointeur vers l'instance MLX. Si ça retourne `None`, l'initialisation a échoué.

---

### Créer une fenêtre

Sans fenêtre, rien n'est affiché. On crée une fenêtre avec `mlx_new_window`, puis on lance la boucle avec `mlx_loop`.

**C (original) :**
```c
mlx = mlx_init();
mlx_win = mlx_new_window(mlx, 1920, 1080, "Hello world!");
mlx_loop(mlx);
```

**Python (adapté) :**
```python
import mlx

mlx_ptr = mlx.init()
win     = mlx.new_window(mlx_ptr, 1920, 1080, "Hello world!")
mlx.loop(mlx_ptr)
```

La fenêtre reste ouverte indéfiniment (tu peux la tuer avec `CTRL+C` dans le terminal).

---

### Écrire des pixels dans une image

`mlx_pixel_put` est **très lent** car il force un rafraîchissement immédiat de la fenêtre. La bonne pratique : écrire dans un buffer image, puis pousser l'image entière dans la fenêtre.

#### Créer une image

**C :**
```c
img = mlx_new_image(mlx, 1920, 1080);
```

**Python :**
```python
img = mlx.new_image(mlx_ptr, 1920, 1080)
```

#### Récupérer l'adresse mémoire de l'image

En C, on utilise une struct pour stocker les métadonnées de l'image (bpp, line_length, endian).  
En Python, `mlx_get_data_addr` retourne directement ces valeurs (selon la binding, souvent sous forme de tuple ou d'objet).

**C (original) :**
```c
typedef struct s_data {
    void *img;
    char *addr;
    int  bits_per_pixel;
    int  line_length;
    int  endian;
} t_data;

img.addr = mlx_get_data_addr(img.img, &img.bits_per_pixel, &img.line_length, &img.endian);
```

**Python (adapté) :**
```python
# La binding Python retourne généralement un objet ou un tuple
addr, bpp, line_length, endian = mlx.get_data_addr(img)
```

> **Note :** En Python, pas besoin de passer des pointeurs — les valeurs sont retournées directement.

#### Calculer l'offset d'un pixel

Les lignes ne sont pas alignées sur la largeur en pixels, donc on utilise `line_length` :

```
offset = y * line_length + x * (bits_per_pixel // 8)
```

#### Écrire un pixel dans l'image (équivalent de `mlx_pixel_put` rapide)

**C :**
```c
void my_mlx_pixel_put(t_data *data, int x, int y, int color)
{
    char *dst;
    dst = data->addr + (y * data->line_length + x * (data->bits_per_pixel / 8));
    *(unsigned int*)dst = color;
}
```

**Python :**
```python
import ctypes

def pixel_put(addr, x, y, color, line_length, bpp):
    offset = y * line_length + x * (bpp // 8)
    # addr est un objet ctypes ou bytearray selon la binding
    ctypes.cast(addr + offset, ctypes.POINTER(ctypes.c_uint32))[0] = color
```

> **Astuce :** Utilise deux images en alternance pour éviter le screen-tearing (double buffering).

---

### Pousser l'image dans la fenêtre

**C :**
```c
mlx_put_image_to_window(mlx, mlx_win, img.img, 0, 0);
```

**Python :**
```python
mlx.put_image_to_window(mlx_ptr, win, img, 0, 0)
```

#### Exemple complet : afficher un pixel rouge en (5, 5)

**C (original) :**
```c
my_mlx_pixel_put(&img, 5, 5, 0x00FF0000);
mlx_put_image_to_window(mlx, mlx_win, img.img, 0, 0);
mlx_loop(mlx);
```

**Python (adapté) :**
```python
import mlx
import ctypes

def pixel_put(addr, x, y, color, line_length, bpp):
    offset = y * line_length + x * (bpp // 8)
    ctypes.cast(addr + offset, ctypes.POINTER(ctypes.c_uint32))[0] = color

mlx_ptr = mlx.init()
win     = mlx.new_window(mlx_ptr, 1920, 1080, "Hello world!")
img     = mlx.new_image(mlx_ptr, 1920, 1080)
addr, bpp, line_length, endian = mlx.get_data_addr(img)

pixel_put(addr, 5, 5, 0x00FF0000, line_length, bpp)

mlx.put_image_to_window(mlx_ptr, win, img, 0, 0)
mlx.loop(mlx_ptr)
```

> `0x00FF0000` = rouge pur en format `ARGB(0, 255, 0, 0)`.

---

### Exercices

- Dessine des carrés, cercles, triangles et hexagones en calculant les pixels à la main.
- Fais des dégradés et un arc-en-ciel en jouant avec les composantes RGB.
- Génère des textures avec des boucles imbriquées.

---

## 3. Les couleurs

Les couleurs sont représentées sous forme d'entier (`int`). Le format utilisé est **TRGB** : `0xTTRRGGBB`.

| Lettre | Description       |
|--------|-------------------|
| `T`    | Transparence      |
| `R`    | Composante rouge  |
| `G`    | Composante verte  |
| `B`    | Composante bleue  |

Exemples :

| Couleur | Représentation TRGB |
|---------|---------------------|
| Rouge   | `0x00FF0000`        |
| Vert    | `0x0000FF00`        |
| Bleu    | `0x000000FF`        |

---

### Encoder et décoder une couleur

#### Méthode 1 : Décalage de bits (BitShifting)

En Python, les entiers n'ont pas de taille fixe donc c'est encore plus simple qu'en C :

**C (original) :**
```c
int create_trgb(int t, int r, int g, int b)
{
    return (t << 24 | r << 16 | g << 8 | b);
}
```

**Python :**
```python
def create_trgb(t: int, r: int, g: int, b: int) -> int:
    return (t << 24) | (r << 16) | (g << 8) | b

def get_t(trgb: int) -> int:
    return (trgb >> 24) & 0xFF

def get_r(trgb: int) -> int:
    return (trgb >> 16) & 0xFF

def get_g(trgb: int) -> int:
    return (trgb >> 8) & 0xFF

def get_b(trgb: int) -> int:
    return trgb & 0xFF
```

#### Méthode 2 : Conversion via bytes

**Python (équivalent de la conversion char/int du C) :**
```python
import struct

def create_trgb_bytes(t: int, r: int, g: int, b: int) -> int:
    # On pack dans l'ordre little-endian : b, g, r, t
    return struct.unpack('<I', bytes([b, g, r, t]))[0]

def get_components_bytes(trgb: int):
    raw = struct.pack('<I', trgb)
    b, g, r, t = raw
    return t, r, g, b
```

> En Python la méthode par décalage de bits est généralement préférable, elle est plus lisible.

---

### Exercices

- Écris `add_shade(distance: float, color: int) -> int` : `0.0` = pas d'ombrage, `1.0` = noir complet.
- Écris `get_opposite(color: int) -> int` : inverse les composantes RGB.

---

## 4. Les événements

Les événements sont la base de toute application interactive avec MiniLibX. Un hook = une fonction appelée automatiquement quand un événement se produit.

### Événements supportés sur macOS (Cocoa/OpenGL)

```python
ON_KEYDOWN  = 2
ON_KEYUP    = 3
ON_MOUSEDOWN = 4
ON_MOUSEUP  = 5
ON_MOUSEMOVE = 6
ON_EXPOSE   = 12
ON_DESTROY  = 17
```

---

### Tableau des événements X11

| Code | Événement          | Code | Événement           |
|------|--------------------|------|---------------------|
| `2`  | KeyPress           | `14` | NoExpose            |
| `3`  | KeyRelease         | `15` | VisibilityNotify    |
| `4`  | ButtonPress        | `16` | CreateNotify        |
| `5`  | ButtonRelease      | `17` | DestroyNotify       |
| `6`  | MotionNotify       | `18` | UnmapNotify         |
| `7`  | EnterNotify        | `19` | MapNotify           |
| `8`  | LeaveNotify        | `20` | MapRequest          |
| `9`  | FocusIn            | `22` | ConfigureNotify     |
| `10` | FocusOut           | `25` | ResizeRequest       |
| `12` | Expose             | `28` | PropertyNotify      |

---

### Tableau des masques X11

| Masque       | Description          |
|--------------|----------------------|
| `0`          | NoEventMask          |
| `1 << 0`     | KeyPressMask         |
| `1 << 1`     | KeyReleaseMask       |
| `1 << 2`     | ButtonPressMask      |
| `1 << 3`     | ButtonReleaseMask    |
| `1 << 4`     | EnterWindowMask      |
| `1 << 5`     | LeaveWindowMask      |
| `1 << 6`     | PointerMotionMask    |
| `1 << 15`    | ExposureMask         |
| `1 << 17`    | StructureNotifyMask  |

---

### S'abonner à un événement avec `mlx_hook`

**C (original) :**
```c
void mlx_hook(mlx_win_list_t *win_ptr, int x_event, int x_mask, int (*f)(), void *param);
```

**Python (adapté) :**
```python
mlx.hook(win, x_event, x_mask, callback_function, param)
```

#### Prototypes des callbacks selon l'événement

| Événement     | Code | Signature Python du callback            |
|---------------|------|-----------------------------------------|
| ON_KEYDOWN    | 2    | `def f(keycode: int, param) -> int`     |
| ON_KEYUP      | 3    | `def f(keycode: int, param) -> int`     |
| ON_MOUSEDOWN  | 4    | `def f(button, x, y, param) -> int`     |
| ON_MOUSEUP    | 5    | `def f(button, x, y, param) -> int`     |
| ON_MOUSEMOVE  | 6    | `def f(x, y, param) -> int`             |
| ON_EXPOSE     | 12   | `def f(param) -> int`                   |
| ON_DESTROY    | 17   | `def f(param) -> int`                   |

---

### Aliases de hooks

- `mlx.expose_hook(win, f, param)` → alias de `mlx_hook` sur l'événement `12`
- `mlx.key_hook(win, f, param)` → alias sur `KeyRelease` (`3`)
- `mlx.mouse_hook(win, f, param)` → alias sur `ButtonPress` (`4`)

---

### Exemple : fermer la fenêtre à chaque appui de touche

**C (original) :**
```c
int close(int keycode, t_vars *vars)
{
    mlx_destroy_window(vars->mlx, vars->win);
    return (0);
}

int main(void)
{
    t_vars vars;
    vars.mlx = mlx_init();
    vars.win = mlx_new_window(vars.mlx, 1920, 1080, "Hello world!");
    mlx_hook(vars.win, 2, 1L<<0, close, &vars);
    mlx_loop(vars.mlx);
}
```

**Python (adapté) :**
```python
import mlx

def on_keypress(keycode, vars_dict):
    mlx.destroy_window(vars_dict['mlx'], vars_dict['win'])
    return 0

vars_dict = {}
vars_dict['mlx'] = mlx.init()
vars_dict['win'] = mlx.new_window(vars_dict['mlx'], 1920, 1080, "Hello world!")

mlx.hook(vars_dict['win'], 2, 1 << 0, on_keypress, vars_dict)
mlx.loop(vars_dict['mlx'])
```

---

### Exercices

- Appuyer sur `ESC` ferme la fenêtre.
- Redimensionner la fenêtre affiche un message dans le terminal.
- Cliquer sur la croix rouge ferme la fenêtre.
- Maintenir une touche plus de X secondes affiche un message.
- La souris entre dans la fenêtre → `"Bonjour !"`, quitte → `"Au revoir !"`.

---

## 5. Les hooks

En informatique, le *hooking* désigne l'ensemble des techniques permettant d'intercepter des appels de fonctions, des messages ou des événements entre composants logiciels. Le code qui gère ces interceptions s'appelle un hook.

MiniLibX est entièrement basé sur ce mécanisme.

---

### Hook sur les événements clavier

**C (original) :**
```c
int key_hook(int keycode, t_vars *vars)
{
    printf("Hello from key_hook!\n");
    return (0);
}

int main(void)
{
    t_vars vars;
    vars.mlx = mlx_init();
    vars.win = mlx_new_window(vars.mlx, 640, 480, "Hello world!");
    mlx_key_hook(vars.win, key_hook, &vars);
    mlx_loop(vars.mlx);
}
```

**Python (adapté) :**
```python
import mlx

def key_hook(keycode, param):
    print("Hello from key_hook!")
    return 0

mlx_ptr = mlx.init()
win = mlx.new_window(mlx_ptr, 640, 480, "Hello world!")
mlx.key_hook(win, key_hook, None)
mlx.loop(mlx_ptr)
```

---

### Hook sur les événements souris

```python
mlx.mouse_hook(win, mouse_hook, param)
```

Codes des boutons souris (macOS) :

| Code | Bouton         |
|------|----------------|
| `1`  | Clic gauche    |
| `2`  | Clic droit     |
| `3`  | Clic molette   |
| `4`  | Scroll haut    |
| `5`  | Scroll bas     |

---

### Exercices

- Afficher le keycode de chaque touche pressée.
- Afficher la position de la souris à chaque déplacement.
- Afficher l'angle de déplacement de la souris lors d'un clic.

---

## 6. Les boucles

La boucle MLX appelle en continu la fonction enregistrée via `mlx_loop_hook` pour rendre les frames suivantes.

### Lancer une boucle simple

**C :**
```c
mlx = mlx_init();
mlx_loop(mlx);
```

**Python :**
```python
mlx_ptr = mlx.init()
mlx.loop(mlx_ptr)
```

Ça ne fait rien si aucun loop hook n'est enregistré.

---

### Enregistrer un hook de rendu

**C (original) :**
```c
int render_next_frame(void *YourStruct);

int main(void)
{
    void *mlx;
    mlx = mlx_init();
    mlx_loop_hook(mlx, render_next_frame, YourStruct);
    mlx_loop(mlx);
}
```

**Python (adapté) :**
```python
import mlx

def render_next_frame(state):
    # state est un dict/objet persistant entre les frames
    # Mets à jour ton image ici et pousse-la dans la fenêtre
    pass

state = {
    'mlx': mlx.init(),
    # ajoute fenêtre, image, etc.
}
state['win'] = mlx.new_window(state['mlx'], 1920, 1080, "Animation")

mlx.loop_hook(state['mlx'], render_next_frame, state)
mlx.loop(state['mlx'])
```

> `state` est passé par référence : ses modifications persistent entre les appels. Profites-en !

---

### Exercices

- Un arc-en-ciel animé qui cycl entre rouge → vert → bleu en boucle.
- Un cercle que tu déplaces avec les touches WASD.

---

## 7. Les images

Les images permettent à MiniLibX d'atteindre son plein potentiel, notamment pour charger des textures et sprites depuis des fichiers.

### Lire une image depuis un fichier

Les formats supportés sont **XPM** et **PNG**.  
⚠️ `mlx_png_file_to_image` a une fuite mémoire connue — préfère XPM quand c'est possible.

**C (original) :**
```c
void *mlx;
void *img;
char *relative_path = "./test.xpm";
int  img_width, img_height;

mlx = mlx_init();
img = mlx_xpm_file_to_image(mlx, relative_path, &img_width, &img_height);
```

**Python (adapté) :**
```python
import mlx

mlx_ptr = mlx.init()
img_width  = 0
img_height = 0

img, img_width, img_height = mlx.xpm_file_to_image(mlx_ptr, "./test.xpm")
# ou pour PNG :
img, img_width, img_height = mlx.png_file_to_image(mlx_ptr, "./test.png")
```

> Si `img` vaut `None`, la lecture a échoué. `img_width` et `img_height` sont remplis automatiquement — pratique pour les sprites !

---

### Exercices

- Importe un curseur personnalisé et fais-le se déplacer librement dans la fenêtre.
- Importe une texture et répète-la sur toute la fenêtre (tile).

---

## 8. La synchronisation (Sync)

### Pourquoi ?

Gérer le double buffering manuellement (plusieurs images) est fastidieux. Depuis la version MLX 2020, `mlx_sync` permet de synchroniser tes frames plus proprement.

### Les constantes

```python
MLX_SYNC_IMAGE_WRITABLE   = 1
MLX_SYNC_WIN_FLUSH_CMD    = 2
MLX_SYNC_WIN_CMD_COMPLETED = 3
```

### Utilisation

**C (original) :**
```c
int mlx_sync(int cmd, void *ptr);
```

**Python :**
```python
mlx.sync(MLX_SYNC_IMAGE_WRITABLE, img)    # bufferise les écritures dans l'image
mlx.sync(MLX_SYNC_WIN_FLUSH_CMD, win)     # pousse les changements dans la fenêtre
```

- `MLX_SYNC_IMAGE_WRITABLE` : bufferise tous les appels d'écriture sur l'image pointée par `ptr`.
- `MLX_SYNC_WIN_FLUSH_CMD` : propage les changements dans la fenêtre donnée en `ptr`.

---

### Exercice

Reprends le petit jeu avec le cercle mobile (exercice des Loops) et intègre `mlx_sync` à ton rendu.

---

## 9. Épilogue

Félicitations, tu as fini le tutoriel complet ! Tu peux maintenant te considérer comme un maître de MiniLibX (en Python en plus, respect).

La section suivante est une **référence rapide** de toutes les fonctions disponibles, avec leur signature Python.

---

## 10. Prototypes (référence complète)

### Fonctions d'initialisation

#### `mlx.init()`
Initialise la lib MLX. **Doit être appelé en premier.** Retourne `None` en cas d'échec.
```python
mlx_ptr = mlx.init()
```

#### `mlx.new_window(mlx_ptr, width, height, title)`
Crée une nouvelle fenêtre. Retourne un pointeur de fenêtre.
```python
win = mlx.new_window(mlx_ptr, 1920, 1080, "Mon titre")
```

#### `mlx.clear_window(mlx_ptr, win_ptr)`
Efface le contenu de la fenêtre. **Déconseillé** — préfère pousser une image noire avec `mlx_put_image_to_window`.
```python
mlx.clear_window(mlx_ptr, win)
```

#### `mlx.destroy_window(mlx_ptr, win_ptr)`
Détruit une instance de fenêtre.
```python
mlx.destroy_window(mlx_ptr, win)
```

---

### Fonctions utilitaires

#### `mlx.get_color_value(mlx_ptr, color)`
Convertit un entier couleur `0xTTRRGGBB` vers la valeur interne MLX.
```python
color_val = mlx.get_color_value(mlx_ptr, 0x00FF0000)
```

#### `mlx.pixel_put(mlx_ptr, win_ptr, x, y, color)`
Dessine un pixel directement. **Très lent, à éviter** — utilise plutôt une image buffered.
```python
mlx.pixel_put(mlx_ptr, win, 100, 200, 0x00FF0000)
```

#### `mlx.string_put(mlx_ptr, win_ptr, x, y, color, text)`
Affiche une chaîne à la position `(x, y)`.
```python
mlx.string_put(mlx_ptr, win, 50, 50, 0x00FFFFFF, "Hello!")
```

---

### Fonctions image

#### `mlx.new_image(mlx_ptr, width, height)`
Crée une nouvelle image MLX. Retourne un pointeur image.
```python
img = mlx.new_image(mlx_ptr, 1920, 1080)
```

#### `mlx.get_data_addr(img_ptr)`
Récupère l'adresse mémoire de l'image avec ses métadonnées.
```python
addr, bpp, line_length, endian = mlx.get_data_addr(img)
```
Calcul de position d'un pixel :
```python
offset = y * line_length + x * (bpp // 8)
```

#### `mlx.put_image_to_window(mlx_ptr, win_ptr, img_ptr, x, y)`
Affiche une image dans la fenêtre à la position `(x, y)`.
```python
mlx.put_image_to_window(mlx_ptr, win, img, 0, 0)
```

#### `mlx.destroy_image(mlx_ptr, img_ptr)`
Détruit une instance d'image.
```python
mlx.destroy_image(mlx_ptr, img)
```

---

### Hooks

#### `mlx.mouse_hook(win_ptr, callback, param)`
S'abonne aux événements souris. Callback : `f(button, x, y, param)`.
```python
mlx.mouse_hook(win, on_mouse, my_state)
```

#### `mlx.key_hook(win_ptr, callback, param)`
S'abonne aux événements clavier (fenêtre focalisée uniquement). Callback : `f(keycode, param)`.
```python
mlx.key_hook(win, on_key, my_state)
```

#### `mlx.expose_hook(win_ptr, callback, param)`
Alias de `mlx_hook` sur l'événement expose. Callback : `f(param)`.
```python
mlx.expose_hook(win, on_expose, my_state)
```

#### `mlx.loop_hook(mlx_ptr, callback, param)`
Enregistre une fonction appelée à chaque frame. Callback : `f(param)`.
```python
mlx.loop_hook(mlx_ptr, render, my_state)
```

#### `mlx.loop(mlx_ptr)`
Lance la boucle principale. Bloquant — tous les hooks enregistrés sont appelés dans l'ordre.
```python
mlx.loop(mlx_ptr)
```

#### `mlx.hook(win_ptr, x_event, x_mask, callback, param)`
Hook générique sur n'importe quel événement X11.
```python
mlx.hook(win, 2, 1 << 0, on_keypress, my_state)
```

---

### Conversion d'images (sprites / textures)

#### `mlx.xpm_to_image(mlx_ptr, xpm_data, width, height)`
Convertit des données XPM en image. `xpm_data` = liste de chaînes.
```python
img, w, h = mlx.xpm_to_image(mlx_ptr, xpm_data)
```

#### `mlx.xpm_file_to_image(mlx_ptr, filename)`
Charge un fichier XPM en image.
```python
img, w, h = mlx.xpm_file_to_image(mlx_ptr, "./sprite.xpm")
```

#### `mlx.png_file_to_image(mlx_ptr, filename)`
Charge un fichier PNG en image. ⚠️ Fuite mémoire connue.
```python
img, w, h = mlx.png_file_to_image(mlx_ptr, "./texture.png")
```

---

### Fonctions souris

#### `mlx.mouse_hide()`
Cache le curseur.
```python
mlx.mouse_hide()
```

#### `mlx.mouse_show()`
Affiche le curseur.
```python
mlx.mouse_show()
```

#### `mlx.mouse_move(win_ptr, x, y)`
Déplace le curseur à la position `(x, y)`.
```python
mlx.mouse_move(win, 100, 200)
```

#### `mlx.mouse_get_pos(win_ptr)`
Retourne la position actuelle du curseur.
```python
x, y = mlx.mouse_get_pos(win)
```

---

### Auto-répétition des touches

#### `mlx.do_key_autorepeatoff(mlx_ptr)`
Désactive la répétition automatique des touches.
```python
mlx.do_key_autorepeatoff(mlx_ptr)
```

#### `mlx.do_key_autorepeaton(mlx_ptr)`
Active la répétition automatique des touches.
```python
mlx.do_key_autorepeaton(mlx_ptr)
```

---

### Divers

#### `mlx.do_sync(mlx_ptr)`
Synchronise les frames de toutes les fenêtres MLX.
```python
mlx.do_sync(mlx_ptr)
```

#### `mlx.get_screen_size(mlx_ptr)`
Retourne la taille de l'écran.
```python
width, height = mlx.get_screen_size(mlx_ptr)
```

---

*Doc adaptée depuis [harm-smits.github.io/42docs/libs/minilibx](https://harm-smits.github.io/42docs/libs/minilibx) — traduction et adaptation Python par Claude.*
