import flet as ft
import requests
import random
import asyncio

# Cores do tema
COLOR_PRIMARY = "#5E35B1"
COLOR_SECONDARY = "#3949AB"
COLOR_ACCENT = "#FFC107"
COLOR_BACKGROUND = "#F5F5F5"
COLOR_TEXT = "#212121"

# Função de busca de palavras
def buscar_palavras_relacionadas(palavra):
    base_url = "http://api.conceptnet.io"
    endpoints = [
        f"/c/pt/{palavra}",
        f"/query?node=/c/pt/{palavra}&rel=/r/RelatedTo&limit=100",
        f"/query?node=/c/pt/{palavra}&rel=/r/Synonym&limit=50",
        f"/query?node=/c/pt/{palavra}&rel=/r/IsA&limit=50",
        f"/query?node=/c/pt/{palavra}&rel=/r/PartOf&limit=50"
    ]
    
    palavras_relacionadas = set()
    categorias_indesejadas = {"cor", "color", "número", "numero", "numeral", "quantidade"}
    
    try:
        palavras_relacionadas.add(palavra.lower())
        palavras_relacionadas.add(palavra.upper())
        palavras_relacionadas.add(palavra.capitalize())
        
        for endpoint in endpoints:
            url = base_url + endpoint
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            for edge in data.get("edges", []):
                if f"/c/pt/{palavra}" in edge["start"]["@id"]:
                    palavra_alvo = edge["end"]["label"].lower()
                else:
                    palabra_alvo = edge["start"]["label"].lower()
                
                if (palavra_alvo.replace(" ", "").isalpha() and 
                    3 <= len(palavra_alvo) <= 25 and
                    not any(cat in palavra_alvo for cat in categorias_indesejadas) and
                    palavra_alvo not in palavras_relacionadas):
                    
                    palavras_relacionadas.add(palavra_alvo)
        
        if len(palavras_relacionadas) < 30:
            endpoints_en = [
                f"/query?node=/c/en/{palavra}&rel=/r/RelatedTo&limit=50",
                f"/query?node=/c/en/{palavra}&rel=/r/Synonym&limit=30"
            ]
            for endpoint in endpoints_en:
                url = base_url + endpoint
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    for edge in data.get("edges", []):
                        palavra_alvo = edge["end"]["label"].lower()
                        if (palavra_alvo.replace(" ", "").isalpha() and 
                            3 <= len(palavra_alvo) <= 25 and
                            not any(cat in palavra_alvo for cat in categorias_indesejadas)):
                            
                            palavras_relacionadas.add(palavra_alvo)
        
        return sorted(list(palavras_relacionadas), key=lambda x: len(x))[:100]
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar palavras: {e}")
        return []

# Componente de cabeçalho
def header(title):
    return ft.Container(
        content=ft.Text(
            title,
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.WHITE,
            text_align=ft.TextAlign.CENTER
        ),
        padding=20,
        bgcolor=COLOR_PRIMARY,
        border_radius=ft.border_radius.only(top_left=10, top_right=10),
        width=800
    )

# Botão personalizado
def styled_button(text, on_click, icon=None, width=200, bgcolor=COLOR_SECONDARY):
    return ft.ElevatedButton(
        text=text,
        icon=icon,
        on_click=on_click,
        width=width,
        height=50,
        style=ft.ButtonStyle(
            bgcolor=bgcolor,
            color=ft.colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=20,
            elevation=8,
            overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE)
        ),
    )

# Página inicial
def home_page(page: ft.Page):
    def ir_para_jogo_letras(e):
        palavra = input_field.value.strip()
        if not palavra:
            result_text.value = "Por favor, digite uma palavra para o jogo de letras!"
            result_text.color = ft.colors.RED
            page.update()
            return
        
        result_text.value = "Buscando palavras relacionadas..."
        result_text.color = COLOR_TEXT
        page.update()
        
        palavras_encontradas = buscar_palavras_relacionadas(palavra)
        if not palavras_encontradas:
            result_text.value = "Nenhuma palavra encontrada, tente outra!"
            result_text.color = ft.colors.RED
            page.update()
            return
        
        page.session.set("palavras_relacionadas", palavras_encontradas)
        page.go("/jogo_letras")

    def ir_para_jogo_figuras(e):
        page.go("/jogo_figuras")

    input_field = ft.TextField(
        label="Digite uma palavra para o jogo de letras",
        text_align=ft.TextAlign.CENTER,
        width=400,
        border_color=COLOR_PRIMARY,
        focused_border_color=COLOR_ACCENT,
        prefix_icon=ft.icons.SEARCH,
        hint_text="Ex: gato, livro, felicidade",
        border_radius=10
    )
    
    result_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    
    return ft.View(
        "/",
        controls=[
            ft.Column(
                [
                    header("Jogos Educativos"),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Image(
                                    src="https://i.imgur.com/7GP6nW3.png",
                                    width=200,
                                    height=200,
                                    fit=ft.ImageFit.CONTAIN
                                ),
                                ft.Text("Escolha um jogo para começar:", 
                                       size=20, 
                                       weight=ft.FontWeight.BOLD,
                                       color=COLOR_TEXT),
                                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                                ft.Text("Para o jogo de letras, digite uma palavra:", 
                                       size=16,
                                       color=COLOR_TEXT),
                                input_field,
                                result_text,
                                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                                ft.Row([
                                    styled_button(
                                        "Jogo de Letras", 
                                        ir_para_jogo_letras, 
                                        icon=ft.icons.TEXT_FIELDS,
                                        bgcolor=COLOR_PRIMARY
                                    ),
                                    styled_button(
                                        "Jogo de Figuras", 
                                        ir_para_jogo_figuras, 
                                        icon=ft.icons.IMAGE,
                                        bgcolor=COLOR_SECONDARY
                                    ),
                                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15
                        ),
                        padding=30,
                        bgcolor=ft.colors.WHITE,
                        border_radius=10,
                        width=800,
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=15,
                            color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                            offset=ft.Offset(0, 0),
                            blur_style=ft.ShadowBlurStyle.NORMAL,
                        )
                    ),
                    ft.Text("Desenvolvido com ❤️ e Flet", 
                           size=12, 
                           color=ft.colors.GREY,
                           text_align=ft.TextAlign.CENTER)
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0
            )
        ]
    )

# Jogo de letras
def jogo_letras_page(page: ft.Page):
    palavras = page.session.get("palavras_relacionadas") or []

    if not palavras:
        page.go("/")
        return
    
    class WordGame(ft.Column):
        def __init__(self):
            super().__init__()
            self.words = palavras
            self.used_words = set()
            self.selected_word = self.get_new_word()
            self.shuffled_word = self.shuffle_word(self.selected_word)
            self.current_letter_index = 0
            self.letter_buttons = self.create_letter_buttons()
            
            self.word_display = ft.Container(
                content=ft.Text(
                    value=f"Palavra: {self.selected_word}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    color=COLOR_TEXT
                ),
                padding=10,
                bgcolor=ft.colors.with_opacity(0.1, COLOR_PRIMARY),
                border_radius=10,
                width=600
            )
            
            self.letters_row = ft.Row(
                controls=self.letter_buttons, 
                alignment=ft.MainAxisAlignment.CENTER,
                wrap=True,
                spacing=10,
                run_spacing=10,
                width=600
            )
            
            self.result_text = ft.Container(
                content=ft.Text(
                    "", 
                    size=18, 
                    weight=ft.FontWeight.BOLD, 
                    text_align=ft.TextAlign.CENTER
                ),
                padding=10,
                border_radius=10,
                width=600
            )
            
            self.controls.extend([
                header("Jogo de Letras"),
                ft.Container(
                    content=ft.Column(
                        [
                            self.word_display,
                            ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                            ft.Text("Clique nas letras na ordem correta:", 
                                   size=16, 
                                   color=COLOR_TEXT),
                            self.letters_row,
                            self.result_text,
                            ft.Row([
                                styled_button(
                                    "Nova Palavra", 
                                    self.reload_word, 
                                    icon=ft.icons.REFRESH,
                                    width=180
                                ),
                                styled_button(
                                    "Voltar", 
                                    lambda e: page.go("/"), 
                                    icon=ft.icons.ARROW_BACK,
                                    width=150,
                                    bgcolor=ft.colors.GREY
                                ),
                                styled_button(
                                    "Jogo de Figuras", 
                                    lambda e: page.go("/jogo_figuras"), 
                                    icon=ft.icons.IMAGE,
                                    width=180
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=15
                    ),
                    padding=30,
                    bgcolor=ft.colors.WHITE,
                    border_radius=10,
                    width=800,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=15,
                        color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                        offset=ft.Offset(0, 0),
                        blur_style=ft.ShadowBlurStyle.NORMAL,
                    )
                )
            ])
        
        def get_new_word(self):
            available_words = [word for word in self.words if word not in self.used_words]
            if not available_words:
                self.used_words.clear()
                available_words = self.words
            new_word = random.choice(available_words)
            self.used_words.add(new_word)
            return new_word
        
        def shuffle_word(self, word):
            letters = list(word)
            random.shuffle(letters)
            return letters
        
        def create_letter_buttons(self):
            buttons = []
            for letter in self.shuffled_word:
                button = ft.Container(
                    content=ft.Text(
                        letter,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXT
                    ),
                    width=50,
                    height=50,
                    alignment=ft.alignment.center,
                    bgcolor=ft.colors.with_opacity(0.1, COLOR_SECONDARY),
                    border_radius=10,
                    animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
                    on_click=lambda e, l=letter: self.check_letter(e, l),
                    ink=True
                )
                buttons.append(button)
            return buttons
        
        def check_letter(self, e, clicked_letter):
            correct_letter = self.selected_word[self.current_letter_index]
            if clicked_letter == correct_letter:
                e.control.bgcolor = ft.colors.GREEN
                e.control.content.color = ft.colors.WHITE
                e.control.elevation = 0
                self.current_letter_index += 1
                if self.current_letter_index == len(self.selected_word):
                    self.result_text.content.value = "Parabéns! Você acertou a palavra! 🎉"
                    self.result_text.content.color = ft.colors.GREEN
                    self.result_text.bgcolor = ft.colors.with_opacity(0.1, ft.colors.GREEN)
            else:
                self.result_text.content.value = "Letra errada. Tente novamente!"
                self.result_text.content.color = ft.colors.RED
                self.result_text.bgcolor = ft.colors.with_opacity(0.1, ft.colors.RED)
            self.update()
        
        def reload_word(self, e):
            self.selected_word = self.get_new_word()
            self.shuffled_word = self.shuffle_word(self.selected_word)
            self.current_letter_index = 0
            self.letter_buttons = self.create_letter_buttons()
            self.letters_row.controls = self.letter_buttons
            self.result_text.content.value = ""
            self.result_text.bgcolor = None
            self.word_display.content.value = f"Palavra: {self.selected_word}"
            self.update()
    
    return ft.View(
        "/jogo_letras",
        controls=[WordGame()]
    )

# Jogo de figuras com autoavanço
def jogo_figuras_page(page: ft.Page):
    class WordMatrixGame(ft.Column):
        def __init__(self):
            super().__init__()
            self.animal_icons = {
                "🐶": "Cachorro",
                "🐱": "Gato",
                "🐭": "Rato",
                "🐹": "Hamster",
                "🐰": "Coelho",
                "🦊": "Raposa",
                "🐻": "Urso",
                "🐼": "Panda",
                "🐨": "Coala",
                "🐯": "Tigre",
                "🦁": "Leão",
                "🐮": "Vaca",
                "🐷": "Porco",
                "🐸": "Sapo",
                "🐵": "Macaco",
                "🐔": "Galinha",
                "🐧": "Pinguim",
                "🐦": "Pássaro",
                "🐤": "Pintinho",
                "🦅": "Águia",
                "🦉": "Coruja",
                "🦇": "Morcego",
                "🐺": "Lobo",
                "🦄": "Unicórnio",
                "🦋": "Borboleta"
            }
            self.selected_emoji, self.correct_name = random.choice(list(self.animal_icons.items()))
            
            # Contador de acertos
            self.score = 0
            self.score_display = ft.Text(
                value=f"Acertos: {self.score}",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=COLOR_PRIMARY
            )
            
            self.emoji_display = ft.Container(
                content=ft.Text(
                    value=self.selected_emoji,
                    size=120,
                    text_align=ft.TextAlign.CENTER
                ),
                padding=20,
                bgcolor=ft.colors.with_opacity(0.05, COLOR_PRIMARY),
                border_radius=20,
                animate=ft.animation.Animation(500, ft.AnimationCurve.EASE_IN_OUT)
            )
            
            self.input_field = ft.TextField(
                label="Digite o nome do animal",
                text_align=ft.TextAlign.CENTER,
                on_submit=self.check_answer,
                width=300,
                border_color=COLOR_PRIMARY,
                focused_border_color=COLOR_ACCENT,
                prefix_icon=ft.icons.EDIT,
                border_radius=10,
                autofocus=True
            )
            
            self.result_text = ft.Container(
                content=ft.Text(
                    "", 
                    size=18, 
                    weight=ft.FontWeight.BOLD, 
                    text_align=ft.TextAlign.CENTER
                ),
                padding=10,
                border_radius=10,
                animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
            )
            
            self.letter_count_field = ft.TextField(
                label="Quantas letras 'P' há no nome?",
                text_align=ft.TextAlign.CENTER,
                on_submit=self.check_letter_count,
                width=300,
                border_color=COLOR_PRIMARY,
                focused_border_color=COLOR_ACCENT,
                prefix_icon=ft.icons.FILTER_1,
                border_radius=10
            )
            
            self.letter_count_result = ft.Container(
                content=ft.Text(
                    "", 
                    size=18, 
                    weight=ft.FontWeight.BOLD, 
                    text_align=ft.TextAlign.CENTER
                ),
                padding=10,
                border_radius=10,
                animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
            )
            
            self.timer = ft.Text(
                value="",
                size=16,
                color=COLOR_TEXT,
                visible=False
            )
            
            self.controls.extend([
                header("Jogo de Figuras"),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("Adivinhe o Animal", 
                                           size=22, 
                                           weight=ft.FontWeight.BOLD,
                                           color=COLOR_TEXT),
                                    self.score_display,
                                    self.timer
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            self.emoji_display,
                            self.input_field,
                            self.result_text,
                            self.letter_count_field,
                            self.letter_count_result,
                            ft.Row([
                                styled_button(
                                    "Novo Animal", 
                                    self.new_animal, 
                                    icon=ft.icons.REFRESH,
                                    width=180
                                ),
                                styled_button(
                                    "Voltar", 
                                    lambda e: page.go("/"), 
                                    icon=ft.icons.ARROW_BACK,
                                    width=150,
                                    bgcolor=ft.colors.GREY
                                ),
                                styled_button(
                                    "Jogo de Letras", 
                                    lambda e: page.go("/jogo_letras"), 
                                    icon=ft.icons.TEXT_FIELDS,
                                    width=180
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20
                    ),
                    padding=30,
                    bgcolor=ft.colors.WHITE,
                    border_radius=10,
                    width=800,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=15,
                        color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                        offset=ft.Offset(0, 0),
                        blur_style=ft.ShadowBlurStyle.NORMAL,
                    )
                )
            ])
        
        def new_animal(self, e=None):
            # Seleciona um novo animal aleatório, garantindo que não repita o atual
            current_emoji = self.selected_emoji
            available_emojis = [emoji for emoji in self.animal_icons.keys() if emoji != current_emoji]
            
            if not available_emojis:
                # Se não houver mais animais disponíveis, recomeça
                available_emojis = list(self.animal_icons.keys())
            
            self.selected_emoji = random.choice(available_emojis)
            self.correct_name = self.animal_icons[self.selected_emoji]
            
            self.emoji_display.content.value = self.selected_emoji
            self.emoji_display.bgcolor = ft.colors.with_opacity(0.05, COLOR_PRIMARY)
            self.input_field.value = ""
            self.letter_count_field.value = ""
            self.result_text.content.value = ""
            self.result_text.bgcolor = None
            self.letter_count_result.content.value = ""
            self.letter_count_result.bgcolor = None
            
            # Define foco automático no campo de entrada
            self.input_field.focus()
            self.update()
        
        async def auto_advance(self):
            # Mostra contagem regressiva
            self.timer.visible = True
            for i in range(3, 0, -1):
                self.timer.value = f"Próximo animal em: {i}"
                self.update()
                await asyncio.sleep(1)
            
            self.timer.visible = False
            self.new_animal()
        
        def check_answer(self, e):
            if self.input_field.value.lower() == self.correct_name.lower():
                self.score += 1
                self.score_display.value = f"Acertos: {self.score}"
                
                self.result_text.content.value = "Correto! 🎉"
                self.result_text.content.color = ft.colors.GREEN
                self.result_text.bgcolor = ft.colors.with_opacity(0.1, ft.colors.GREEN)
                self.emoji_display.bgcolor = ft.colors.with_opacity(0.1, ft.colors.GREEN)
                
                # Limpa os campos
                self.input_field.value = ""
                self.letter_count_field.value = ""
                
                # Agenda o autoavanço após 1.5 segundos
                page.run_task(self.auto_advance)
            else:
                self.result_text.content.value = f"Incorreto! O correto é: {self.correct_name}"
                self.result_text.content.color = ft.colors.RED
                self.result_text.bgcolor = ft.colors.with_opacity(0.1, ft.colors.RED)
                self.emoji_display.bgcolor = ft.colors.with_opacity(0.1, ft.colors.RED)
            
            self.update()
        
        def check_letter_count(self, e):
            correct_count = self.correct_name.lower().count('p')
            try:
                user_count = int(self.letter_count_field.value)
                if user_count == correct_count:
                    self.letter_count_result.content.value = "Correto! ✅"
                    self.letter_count_result.content.color = ft.colors.GREEN
                    self.letter_count_result.bgcolor = ft.colors.with_opacity(0.1, ft.colors.GREEN)
                else:
                    self.letter_count_result.content.value = f"Incorreto! Tem {correct_count} letras 'P'"
                    self.letter_count_result.content.color = ft.colors.RED
                    self.letter_count_result.bgcolor = ft.colors.with_opacity(0.1, ft.colors.RED)
            except:
                self.letter_count_result.content.value = "Digite um número válido"
                self.letter_count_result.content.color = ft.colors.RED
                self.letter_count_result.bgcolor = ft.colors.with_opacity(0.1, ft.colors.RED)
            self.update()
    
    return ft.View(
        "/jogo_figuras",
        controls=[WordMatrixGame()]
    )

# Função principal
def main(page: ft.Page):
    page.title = "Jogos Educativos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 20
    page.bgcolor = COLOR_BACKGROUND
    
    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(home_page(page))
        elif page.route == "/jogo_letras":
            page.views.append(jogo_letras_page(page))
        elif page.route == "/jogo_figuras":
            page.views.append(jogo_figuras_page(page))
        page.update()

    page.on_route_change = route_change
    page.go("/")

ft.app(target=main, view=ft.WEB_BROWSER, assets_dir="assets")