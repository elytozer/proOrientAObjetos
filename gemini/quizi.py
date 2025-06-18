import tkinter as tk
from tkinter import messagebox, simpledialog # Importa simpledialog para entrada de texto simples
import random

# --- Classes de Lógica do Quiz ---

class Pergunta:
    """
    Classe base para representar uma pergunta do quiz.
    Encapsula o texto da pergunta e a resposta correta.
    """
    def __init__(self, texto, resposta_correta):
        self._texto = texto
        self._resposta_correta = resposta_correta.lower()

    def get_texto(self):
        """Retorna o texto da pergunta."""
        return self._texto

    def verificar_resposta(self, resposta_usuario):
        """Verifica se a resposta do usuário está correta."""
        return resposta_usuario.lower() == self._resposta_correta

    def get_opcoes_exibicao(self):
        """Método polimórfico para obter opções de exibição. Usado pela GUI."""
        return [] # Para perguntas gerais, não há opções específicas, mas um campo de texto livre.

class PerguntaMultiplaEscolha(Pergunta):
    """
    Subclasse para perguntas de múltipla escolha.
    """
    def __init__(self, texto, resposta_correta, opcoes):
        if not opcoes:
            raise ValueError("Uma pergunta de múltipla escolha deve ter opções.")
        if resposta_correta.lower() not in [opcao.lower() for opcao in opcoes]:
            raise ValueError("A resposta correta deve ser uma das opções fornecidas.")
        super().__init__(texto, resposta_correta)
        self._opcoes = opcoes

    def get_opcoes_exibicao(self):
        """Retorna as opções formatadas com letras (A, B, C...)."""
        return self._opcoes

class PerguntaVerdadeiroFalso(Pergunta):
    """
    Subclasse para perguntas de verdadeiro ou falso.
    A resposta correta deve ser 'verdadeiro' ou 'falso'.
    """
    def __init__(self, texto, resposta_correta):
        if resposta_correta.lower() not in ['verdadeiro', 'falso']:
            raise ValueError("A resposta para perguntas Verdadeiro/Falso deve ser 'verdadeiro' ou 'falso'.")
        super().__init__(texto, resposta_correta)

    def get_opcoes_exibicao(self):
        """Retorna opções fixas para Verdadeiro/Falso."""
        return ["Verdadeiro", "Falso"]

class Usuario:
    """
    Classe para representar um usuário do quiz.
    Encapsula o nome do usuário e a pontuação.
    """
    def __init__(self, nome):
        self._nome = nome
        self._pontuacao = 0

    def get_nome(self):
        """Retorna o nome do usuário."""
        return self._nome

    def get_pontuacao(self):
        """Retorna a pontuação atual do usuário."""
        return self._pontuacao

    def adicionar_pontuacao(self, pontos=1):
        """Adiciona pontos à pontuação do usuário."""
        self._pontuacao += pontos

    def resetar_pontuacao(self):
        """Reseta a pontuação do usuário."""
        self._pontuacao = 0

class Quiz:
    """
    Classe principal para gerenciar o jogo de quiz.
    Gerencia as perguntas e a execução do quiz.
    """
    def __init__(self, nome_quiz="Quiz de Conhecimentos Gerais"):
        self._nome_quiz = nome_quiz
        self._perguntas = []
        self._perguntas_atuais = [] # Perguntas para a rodada atual
        self._indice_pergunta_atual = 0

    def adicionar_pergunta(self, pergunta):
        """Adiciona uma pergunta à lista de perguntas do quiz."""
        if isinstance(pergunta, Pergunta):
            self._perguntas.append(pergunta)
            messagebox.showinfo("Sucesso", "Pergunta adicionada ao quiz!")
        else:
            messagebox.showerror("Erro", "Apenas objetos da classe Pergunta (ou suas subclasses) podem ser adicionados.")

    def preparar_quiz(self):
        """Prepara as perguntas para uma nova rodada (embaralha)."""
        if not self._perguntas:
            messagebox.showwarning("Atenção", "Nenhuma pergunta cadastrada. Adicione perguntas antes de iniciar o quiz.")
            return False
        self._perguntas_atuais = list(self._perguntas) # Cria uma cópia para não alterar a lista original
        random.shuffle(self._perguntas_atuais)
        self._indice_pergunta_atual = 0
        return True

    def get_proxima_pergunta(self):
        """Retorna a próxima pergunta ou None se o quiz terminou."""
        if self._indice_pergunta_atual < len(self._perguntas_atuais):
            pergunta = self._perguntas_atuais[self._indice_pergunta_atual]
            self._indice_pergunta_atual += 1
            return pergunta
        return None

    def get_total_perguntas(self):
        """Retorna o número total de perguntas no quiz."""
        # Se o quiz está em andamento, retorna o total de perguntas da rodada atual
        if self._perguntas_atuais:
            return len(self._perguntas_atuais)
        # Caso contrário, retorna o total de perguntas cadastradas
        return len(self._perguntas)


# --- Implementação da Interface Gráfica com Tkinter ---

class QuizApp:
    """
    Classe que gerencia a interface gráfica do jogo de quiz.
    """
    def __init__(self, master):
        self.master = master
        master.title("Jogo de Quiz - Python")
        master.geometry("600x450") # Ajusta o tamanho da janela
        master.resizable(False, False) # Impede redimensionamento para layout mais estável

        # Configurações de estilo (fonte, cores básicas)
        self.font_large = ('Arial', 14)
        self.font_medium = ('Arial', 12)
        self.bg_color = '#e0f2f7' # Azul claro
        self.fg_color = '#2c3e50' # Azul escuro para texto
        self.button_color = '#3498db' # Azul padrão para botões
        self.button_fg_color = 'white'

        master.config(bg=self.bg_color)

        self.quiz = Quiz("Quiz de Conhecimentos Gerais")
        self.usuario = Usuario("Jogador") # Nome padrão, pode ser alterado por uma tela inicial

        self._adicionar_perguntas_iniciais() # Adiciona as perguntas predefinidas

        self.current_question = None
        self.selected_option_var = tk.StringVar() # Variável para armazenar a opção selecionada nos Radiobuttons
        self.entry_answer_var = tk.StringVar() # Variável para armazenar a resposta do campo de texto

        self.radio_buttons = [] # Lista para manter referência aos Radiobuttons
        self.answer_entry = None # Referência para o campo de entrada de texto

        self._create_menu() # Cria o menu na interface
        self._create_widgets()
        self._show_start_screen() # Inicia mostrando a tela de início

    def _create_menu(self):
        """Cria a barra de menu com as opções."""
        self.menubar = tk.Menu(self.master)
        self.master.config(menu=self.menubar)

        # Menu "Quiz"
        quiz_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Quiz", menu=quiz_menu)
        quiz_menu.add_command(label="Iniciar Quiz", command=self._start_quiz)
        quiz_menu.add_command(label="Adicionar Perguntas", command=self._open_add_question_window)
        quiz_menu.add_separator()
        quiz_menu.add_command(label="Sair", command=self.master.quit) # Usa master.quit para fechar a janela

    def _adicionar_perguntas_iniciais(self):
        """Adiciona as perguntas predefinidas ao quiz silenciosamente."""
        perguntas_iniciais = [
            Pergunta("Qual é a capital da França?", "Paris"),
            PerguntaMultiplaEscolha("Qual o comando para instalar pacotes Python?", "pip install", ["pip install", "python install", "install-pip", "get pip"]),
            Pergunta("O Python é uma linguagem de programação interpretada?", "Verdadeiro"),
            PerguntaVerdadeiroFalso("Brasília é a capital do Brasil.", "Verdadeiro"),
            PerguntaMultiplaEscolha("Qual estrutura de dados armazena itens em pares chave-valor?", "Dicionário", ["Lista", "Tupla", "Dicionário", "Conjunto"]),
            Pergunta("Qual é o maior oceano do mundo?", "Pacífico")
        ]

        # Adiciona as perguntas diretamente à lista, sem mostrar pop-ups
        for p in perguntas_iniciais:
            if isinstance(p, Pergunta):
                self.quiz._perguntas.append(p)

    def _create_widgets(self):
        """Cria e posiciona todos os widgets da interface."""
        # Frame principal para organizar o conteúdo
        self.main_frame = tk.Frame(self.master, bg=self.bg_color, padx=20, pady=20)
        self.main_frame.pack(expand=True, fill='both')

        # Título do Quiz
        self.title_label = tk.Label(self.main_frame, text=self.quiz._nome_quiz, font=('Arial', 20, 'bold'), bg=self.bg_color, fg=self.fg_color)
        self.title_label.pack(pady=10)

        # Label para a pergunta
        self.question_label = tk.Label(self.main_frame, text="", font=self.font_large, wraplength=500, bg=self.bg_color, fg=self.fg_color, justify='center')
        self.question_label.pack(pady=20)

        # Frame para as opções de resposta (Radiobuttons)
        self.options_frame = tk.Frame(self.main_frame, bg=self.bg_color)

        # Campo de entrada de texto para perguntas abertas
        self.answer_entry = tk.Entry(self.main_frame, textvariable=self.entry_answer_var, font=self.font_medium, width=50)

        # Botão de Submissão
        self.submit_button = tk.Button(self.main_frame, text="Responder", command=self._submit_answer, font=self.font_medium, bg=self.button_color, fg=self.button_fg_color, relief='raised', bd=3, padx=10, pady=5)
        self.submit_button.pack(pady=20)

        # Label para a pontuação
        self.score_label = tk.Label(self.main_frame, text=f"Pontuação: 0/{self.quiz.get_total_perguntas()}", font=self.font_medium, bg=self.bg_color, fg=self.fg_color)
        self.score_label.pack(side='bottom', anchor='se', padx=10, pady=10)

        # Botão de Iniciar/Reiniciar (será manipulado por _show_start_screen e _show_end_screen)
        self.start_button = tk.Button(self.main_frame, text="Iniciar Quiz", command=self._start_quiz, font=self.font_medium, bg=self.button_color, fg=self.button_fg_color, relief='raised', bd=3, padx=10, pady=5)


    def _show_start_screen(self):
        """Mostra a tela inicial com o botão de iniciar."""
        self.question_label.config(text="Bem-vindo ao Quiz!\nUse o menu 'Quiz' ou clique em 'Iniciar Quiz' para começar.")
        self.submit_button.pack_forget() # Esconde o botão de responder
        for rb in self.radio_buttons:
            rb.destroy() # Remove quaisquer radiobuttons anteriores
        self.options_frame.pack_forget() # Esconde o frame de opções
        self.answer_entry.pack_forget() # Esconde o campo de entrada
        self.score_label.pack_forget() # Esconde a pontuação
        self.start_button.config(text="Iniciar Quiz")
        self.start_button.pack(pady=50) # Mostra o botão de iniciar

    def _show_quiz_screen(self):
        """Mostra os elementos do quiz (pergunta, opções, botão responder)."""
        self.start_button.pack_forget() # Esconde o botão de iniciar
        # options_frame e answer_entry são empacotados em _update_options_display
        self.submit_button.pack(pady=20)
        self.score_label.pack(side='bottom', anchor='se', padx=10, pady=10)

    def _start_quiz(self):
        """Inicia ou reinicia o quiz."""
        self.usuario.resetar_pontuacao()
        if self.quiz.preparar_quiz(): # Verifica se há perguntas para iniciar
            self.score_label.config(text=f"Pontuação: {self.usuario.get_pontuacao()}/{self.quiz.get_total_perguntas()}")
            self._show_quiz_screen()
            self._display_next_question()
        else:
            self._show_start_screen() # Volta para a tela inicial se não houver perguntas


    def _display_next_question(self):
        """Exibe a próxima pergunta na interface."""
        self.current_question = self.quiz.get_proxima_pergunta()
        if self.current_question:
            self.question_label.config(text=self.current_question.get_texto())
            self._update_options_display(self.current_question)
            self.submit_button.config(state=tk.NORMAL) # Habilita o botão de responder
        else:
            self._show_final_score()

    def _update_options_display(self, question):
        """Atualiza a exibição de opções/campo de entrada com base no tipo de pergunta."""
        # Limpa e esconde todos os widgets de opções anteriores
        for rb in self.radio_buttons:
            rb.destroy()
        self.radio_buttons = []
        self.options_frame.pack_forget() # Esconde o frame de radiobuttons
        self.answer_entry.pack_forget() # Esconde o campo de entrada

        self.selected_option_var.set("") # Reseta a seleção do radiobutton
        self.entry_answer_var.set("") # Reseta o texto do campo de entrada

        if isinstance(question, PerguntaMultiplaEscolha) or isinstance(question, PerguntaVerdadeiroFalso):
            self.options_frame.pack(pady=10) # Garante que o frame esteja empacotado para radiobuttons
            options = question.get_opcoes_exibicao()
            letras_opcoes = [chr(65 + i) for i in range(len(options))]
            for i, option_text in enumerate(options):
                rb_text = f"{letras_opcoes[i]}. {option_text}"
                rb = tk.Radiobutton(self.options_frame, text=rb_text, variable=self.selected_option_var,
                                    value=option_text, font=self.font_medium, bg=self.bg_color, fg=self.fg_color,
                                    selectcolor=self.bg_color, activebackground=self.bg_color)
                rb.pack(anchor='w', pady=2)
                self.radio_buttons.append(rb)
        else: # Pergunta geral (aberta), usa campo de entrada de texto
            # Atualiza o texto da pergunta para indicar que é uma resposta aberta
            self.question_label.config(text=f"{question.get_texto()}\n\n(Digite sua resposta abaixo)")
            self.answer_entry.pack(pady=10)
            self.answer_entry.focus_set() # Coloca o foco no campo de entrada para facilitar a digitação


    def _submit_answer(self):
        """Processa a resposta do usuário."""
        if not self.current_question:
            return

        user_answer = ""
        # Determina a fonte da resposta baseada no tipo de pergunta
        if isinstance(self.current_question, PerguntaMultiplaEscolha) or isinstance(self.current_question, PerguntaVerdadeiroFalso):
            user_answer = self.selected_option_var.get().strip()
            # Validação extra para múltipla escolha com letras, se o usuário digitar a letra (embora não seja o foco da GUI)
            if isinstance(self.current_question, PerguntaMultiplaEscolha) and len(user_answer) == 1 and user_answer.isalpha():
                indice = ord(user_answer.upper()) - ord('A')
                opcoes_atuais = self.current_question.get_opcoes_exibicao()
                if 0 <= indice < len(opcoes_atuais):
                    user_answer = opcoes_atuais[indice] # Converte letra para o texto da opção
        else: # Pergunta geral, obter do campo de entrada de texto
            user_answer = self.entry_answer_var.get().strip()


        if not user_answer:
            messagebox.showwarning("Atenção", "Por favor, digite ou selecione uma opção para responder.")
            return

        # Limpa o campo de entrada ou seleção de rádio após a submissão
        if isinstance(self.current_question, PerguntaMultiplaEscolha) or isinstance(self.current_question, PerguntaVerdadeiroFalso):
            self.selected_option_var.set("")
        else: # Pergunta geral
            self.entry_answer_var.set("") # Limpa o campo de texto


        if self.current_question.verificar_resposta(user_answer):
            self.usuario.adicionar_pontuacao()
            messagebox.showinfo("Resultado", "Resposta Correta! :)")
        else:
            messagebox.showinfo("Resultado", "Resposta Incorreta! :(")

        self.score_label.config(text=f"Pontuação: {self.usuario.get_pontuacao()}/{self.quiz.get_total_perguntas()}")
        self._display_next_question()

    def _show_final_score(self):
        """Exibe a pontuação final e oferece para reiniciar."""
        messagebox.showinfo("Quiz Finalizado!",
                            f"Parabéns, {self.usuario.get_nome()}!\nSua pontuação final é: {self.usuario.get_pontuacao()} de {self.quiz.get_total_perguntas()}")
        self.question_label.config(text="Quiz encerrado!\nClique em 'Reiniciar Quiz' para jogar novamente.")
        self.submit_button.pack_forget()
        for rb in self.radio_buttons:
            rb.destroy()
        self.options_frame.pack_forget()
        self.answer_entry.pack_forget() # Esconde o campo de entrada
        self.start_button.config(text="Reiniciar Quiz")
        self.start_button.pack(pady=50)

    def _open_add_question_window(self):
        """Abre uma nova janela para o usuário adicionar perguntas."""
        add_window = tk.Toplevel(self.master)
        add_window.title("Adicionar Nova Pergunta")
        add_window.geometry("450x400")
        add_window.transient(self.master) # Torna a janela filha da principal
        add_window.grab_set() # Bloqueia a interação com a janela principal

        # Variáveis de controle para os widgets de entrada
        question_text_var = tk.StringVar()
        correct_answer_var = tk.StringVar()
        options_text_var = tk.StringVar()
        question_type_var = tk.StringVar(value="geral") # Default para Pergunta Geral

        # Estilos para a nova janela
        add_window.config(bg=self.bg_color)
        font_label = ('Arial', 10, 'bold')
        font_entry = ('Arial', 10)
        button_font = ('Arial', 10, 'bold')

        # Frame principal para a janela de adição
        add_frame = tk.Frame(add_window, bg=self.bg_color, padx=15, pady=15)
        add_frame.pack(fill='both', expand=True)

        # Rótulos e Campos de entrada
        tk.Label(add_frame, text="Tipo de Pergunta:", font=font_label, bg=self.bg_color, fg=self.fg_color).pack(anchor='w', pady=(5,0))
        tk.Radiobutton(add_frame, text="Geral (Resposta Aberta)", variable=question_type_var, value="geral", font=font_entry, bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color, activebackground=self.bg_color).pack(anchor='w')
        tk.Radiobutton(add_frame, text="Múltipla Escolha", variable=question_type_var, value="multipla_escolha", font=font_entry, bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color, activebackground=self.bg_color).pack(anchor='w')
        tk.Radiobutton(add_frame, text="Verdadeiro/Falso", variable=question_type_var, value="verdadeiro_falso", font=font_entry, bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color, activebackground=self.bg_color).pack(anchor='w')

        tk.Label(add_frame, text="Texto da Pergunta:", font=font_label, bg=self.bg_color, fg=self.fg_color).pack(anchor='w', pady=(10,0))
        tk.Entry(add_frame, textvariable=question_text_var, width=50, font=font_entry).pack(fill='x', pady=2)

        tk.Label(add_frame, text="Resposta Correta:", font=font_label, bg=self.bg_color, fg=self.fg_color).pack(anchor='w', pady=(10,0))
        correct_answer_entry = tk.Entry(add_frame, textvariable=correct_answer_var, width=50, font=font_entry)
        correct_answer_entry.pack(fill='x', pady=2)

        # Frame e campo para opções (múltipla escolha, inicialmente escondido)
        self.options_input_frame = tk.Frame(add_frame, bg=self.bg_color)
        tk.Label(self.options_input_frame, text="Opções (separadas por vírgula):", font=font_label, bg=self.bg_color, fg=self.fg_color).pack(anchor='w', pady=(10,0))
        options_entry = tk.Entry(self.options_input_frame, textvariable=options_text_var, width=50, font=font_entry)
        options_entry.pack(fill='x', pady=2)

        def toggle_options_entry():
            """Mostra/esconde o campo de opções com base no tipo de pergunta."""
            if question_type_var.get() == "multipla_escolha":
                self.options_input_frame.pack(fill='x', pady=5)
                # Adiciona validação para Verdadeiro/Falso no campo de resposta correta
                correct_answer_entry.config(state=tk.NORMAL)
            elif question_type_var.get() == "verdadeiro_falso":
                self.options_input_frame.pack_forget() # Esconde o campo de opções
                messagebox.showinfo("Dica", "Para Verdadeiro/Falso, a resposta correta deve ser 'verdadeiro' ou 'falso'.")
                correct_answer_var.set("") # Limpa o campo para o usuário digitar
                correct_answer_entry.config(state=tk.NORMAL)
            else: # Geral
                self.options_input_frame.pack_forget() # Esconde o campo de opções
                correct_answer_entry.config(state=tk.NORMAL) # Campo de resposta habilitado

        # Liga a função ao Radiobutton
        question_type_var.trace_add("write", lambda *args: toggle_options_entry())
        toggle_options_entry() # Chama uma vez para configurar o estado inicial

        # Botão para adicionar a pergunta
        add_question_button = tk.Button(add_frame, text="Adicionar Pergunta",
                                        command=lambda: self._add_question_from_form(
                                            add_window,
                                            question_type_var.get(),
                                            question_text_var.get(),
                                            correct_answer_var.get(),
                                            options_text_var.get()
                                        ),
                                        font=button_font, bg=self.button_color, fg=self.button_fg_color, relief='raised', bd=3, padx=10, pady=5)
        add_question_button.pack(pady=15)

    def _add_question_from_form(self, window, q_type, q_text, q_answer, q_options_str):
        """
        Adiciona uma pergunta ao quiz baseada nos dados do formulário da janela de adição.
        """
        try:
            if not q_text or not q_answer:
                messagebox.showwarning("Erro de Entrada", "Texto da pergunta e resposta correta não podem estar vazios.")
                return

            if q_type == "geral":
                new_question = Pergunta(q_text, q_answer)
            elif q_type == "multipla_escolha":
                if not q_options_str:
                    messagebox.showwarning("Erro de Entrada", "Opções não podem estar vazias para múltipla escolha.")
                    return
                options = [o.strip() for o in q_options_str.split(',') if o.strip()]
                new_question = PerguntaMultiplaEscolha(q_text, q_answer, options)
            elif q_type == "verdadeiro_falso":
                new_question = PerguntaVerdadeiroFalso(q_text, q_answer)
            else:
                messagebox.showerror("Erro", "Tipo de pergunta inválido selecionado.")
                return

            self.quiz.adicionar_pergunta(new_question)
            window.destroy() # Fecha a janela de adição após o sucesso
            self.score_label.config(text=f"Pontuação: {self.usuario.get_pontuacao()}/{self.quiz.get_total_perguntas()}") # Atualiza o total de perguntas
        except ValueError as e:
            messagebox.showerror("Erro ao Adicionar", f"Erro de validação: {e}")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")


# --- Execução da Aplicação GUI ---
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()