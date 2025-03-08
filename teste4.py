import flet as ft
import random

class WordMatrixApp(ft.Column):
    def __init__(self):
        super().__init__(alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
        self.words = [
            "Gol", "Bola", "Time", "Jogador", "Técnico", "Goleiro", "Zagueiro", "Atacante", "Meia", "Lateral",
            "Artilheiro", "Cartão", "Falta", "Escanteio", "Pênalti", "Torcida", "Estádio", "Camisa", "Treino", "Apito"
        ]
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
            "🦅": "Águia"
        }
        # Escolhe aleatoriamente entre palavras e ícones de animais
        self.is_animal_mode = random.choice([True, False])
        self.selected_item = self.get_random_item()
        self.word_display = ft.Text(
            value=self.selected_item if self.is_animal_mode else f"Palavra: {self.selected_item}",
            size=60 if self.is_animal_mode else 24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        
        self.input_field = ft.TextField(
            label="Digite o nome correspondente:",
            text_align=ft.TextAlign.CENTER,
            on_submit=self.check_word,
            width=300
        )
        self.result_text = ft.Text("", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        
        self.letter_count_field = ft.TextField(
            label="Quantas letras 'P' há no nome?",
            text_align=ft.TextAlign.CENTER,
            on_submit=self.check_letter_count,
            width=300
        )
        self.letter_count_result = ft.Text("", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        
        self.reload_button = ft.ElevatedButton(
            text="Novo Item",
            icon=ft.icons.REFRESH,
            on_click=self.reload_item,
            width=200
        )
        
        self.controls.extend([
            self.word_display,
            self.input_field,
            self.result_text,
            self.letter_count_field,
            self.letter_count_result,
            self.reload_button
        ])
    
    def get_random_item(self):
        if self.is_animal_mode:
            icon, name = random.choice(list(self.animal_icons.items()))
            return icon
        else:
            return random.choice(self.words)
    
    def reload_item(self, e):
        self.is_animal_mode = random.choice([True, False])
        self.selected_item = self.get_random_item()
        self.word_display.value = self.selected_item if self.is_animal_mode else f"Palavra: {self.selected_item}"
        self.word_display.size = 60 if self.is_animal_mode else 24
        self.input_field.value = ""
        self.letter_count_field.value = ""
        self.result_text.value = ""
        self.letter_count_result.value = ""
        self.update()
    
    def check_word(self, e):
        if self.is_animal_mode:
            correct_name = self.animal_icons.get(self.selected_item, "")
            if self.input_field.value.lower() == correct_name.lower():
                self.result_text.value = "Correto! Você digitou o nome do animal corretamente."
            else:
                self.result_text.value = f"Incorreto! O nome correto é: {correct_name}."
        else:
            if self.input_field.value.lower() == self.selected_item.lower():
                self.result_text.value = "Correto! Você digitou a palavra corretamente."
            else:
                self.result_text.value = f"Incorreto! A palavra correta é: {self.selected_item}."
        self.update()
    
    def check_letter_count(self, e):
        if self.is_animal_mode:
            correct_name = self.animal_icons.get(self.selected_item, "")
            correct_count = correct_name.lower().count('p')
        else:
            correct_count = self.selected_item.lower().count('p')
        
        if self.letter_count_field.value.isdigit() and int(self.letter_count_field.value) == correct_count:
            self.letter_count_result.value = "Correto! Número de letras 'P' está certo."
        else:
            self.letter_count_result.value = f"Incorreto! O número correto de 'P' é: {correct_count}."
        self.update()


class LetterClickGame(ft.Column):
    def __init__(self):
        super().__init__(alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
        self.words = ["Casa", "Carro", "Computador", "Livro", "Caneta", "Mesa", "Cadeira", "Janela", "Porta", "Lápis"]
        self.selected_word = random.choice(self.words)
        self.shuffled_word = self.shuffle_word(self.selected_word)
        self.current_letter_index = 0
        self.letter_buttons = self.create_letter_buttons()
        
        self.word_display = ft.Text(
            value="Clique nas letras na ordem correta:",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        
        self.letters_row = ft.Row(controls=self.letter_buttons, alignment=ft.MainAxisAlignment.CENTER)
        self.result_text = ft.Text("", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        
        self.reload_button = ft.ElevatedButton(
            text="Nova Palavra",
            icon=ft.icons.REFRESH,
            on_click=self.reload_word,
            width=200
        )
        
        self.controls.extend([
            self.word_display,
            self.letters_row,
            self.result_text,
            self.reload_button
        ])
    
    def shuffle_word(self, word):
        letters = list(word)
        random.shuffle(letters)
        return letters
    
    def create_letter_buttons(self):
        buttons = []
        for letter in self.shuffled_word:
            button = ft.ElevatedButton(
                text=letter,
                on_click=lambda e, l=letter: self.check_letter(e, l),
                width=50,
                height=50
            )
            buttons.append(button)
        return buttons
    
    def check_letter(self, e, clicked_letter):
        correct_letter = self.selected_word[self.current_letter_index]
        if clicked_letter == correct_letter:
            e.control.bgcolor = ft.colors.GREEN
            e.control.disabled = True
            self.current_letter_index += 1
            if self.current_letter_index == len(self.selected_word):
                self.result_text.value = "Parabéns! Você acertou a palavra."
        else:
            self.result_text.value = "Letra errada. Tente novamente."
        self.update()
    
    def reload_word(self, e):
        self.selected_word = random.choice(self.words)
        self.shuffled_word = self.shuffle_word(self.selected_word)
        self.current_letter_index = 0
        self.letter_buttons = self.create_letter_buttons()
        self.letters_row.controls = self.letter_buttons
        self.result_text.value = ""
        self.update()


def main(page: ft.Page):
    page.title = "Jogo de Palavras e Letras"
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 20
    
    # Escolhe aleatoriamente entre WordMatrixApp e LetterClickGame
    game = random.choice([WordMatrixApp(), LetterClickGame()])
    page.add(game)

ft.app(target=main)