# imports
from PyQt5 import QtWidgets, QtWebEngineWidgets
from PyQt5.QtWidgets import QMessageBox, QDesktopWidget
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import equation_formation
import sys, random, os, time, json
import resource_rc

################################### 定义所有可能出现的数学操作，包括加减乘除 ###################################
def division(a, b):  # 除法比较特殊，用了try except来考虑到被除数为0的情况
    try:
        return a / b
    except:
        return ''

def multiply(a, b):
    return a * b

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def evaluate(equation):
    op = equation[1]
    a,b = equation[0], equation[2]
    if op == '+':
        return add(a,b)
    elif op == '−':
        return subtract(a,b)
    elif op == '÷':
        return division(a,b)
    else:
        return multiply(a,b)

class EvaluateThread(QThread):
    calc = pyqtSignal(str)
    def __init__(self):
        super(EvaluateThread, self).__init__()
    def receive_info(self,target,num_list):
        self.target_ = target
        self.num_list_ = num_list
    def run(self):
        result = equation_formation.translate_to_latex(self.num_list_, self.target_)
        if result == -1:
            result = ':('
        self.calc.emit(result)

class TimeThread(QThread):
    trigger = pyqtSignal(int)
    def __init__(self):
        super(TimeThread, self).__init__()
    def receive(self,value):
        self.total_time = value
    def run(self):
        self.countdown()
    def countdown(self):

        for i in range(self.total_time,-1,-1):
            time.sleep(1)
            self.trigger.emit(i)

baseUIClass, baseUIWidget = uic.loadUiType("main_widget.ui")
class maininterface(baseUIWidget, baseUIClass):
    start_timing= pyqtSignal(int)
    send = pyqtSignal(int, list)

    def __init__(self):
        super(maininterface, self).__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.setupUi(self)
        self.button_set = [self.plus, self.minus, self.times, self.divide]
        self.history = []
        self.card_operation = []
        self.sign_op = []
        self.noanswer = False
        self.min_time = 0
        self.target = 0
        self.card_choice = [0,1,2,3,4,5,6,7,8,9,10,11,12,13]
        self.card_num = 4
        self.answer = ''
        self.timing = TimeThread()
        self.calculation = EvaluateThread()
        self.ai_answer = False
        self.setWindowIcon(QIcon("bin/icon.png"))
        self.setWindowTitle("24 POINT")
        self.setup()
        self.startupposition()
        self.display_home()

    def startupposition(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())


    def setup(self):
        self.display_latex('')
        self.closebtn.clicked.connect(self.close)
        self.minibtn.clicked.connect(self.minimizeclick)
        self.closebtn_2.clicked.connect(self.close)
        self.minibtn_2.clicked.connect(self.minimizeclick)
        self.closebtn_3.clicked.connect(self.close)
        self.minibtn_3.clicked.connect(self.minimizeclick)
        self.closebtn_4.clicked.connect(self.close)
        self.minibtn_4.clicked.connect(self.minimizeclick)
        self.closebtn_5.clicked.connect(self.close)
        self.minibtn_5.clicked.connect(self.minimizeclick)
        self.closebtn_6.clicked.connect(self.close)
        self.minibtn_6.clicked.connect(self.minimizeclick)

        self.start_timing.connect(self.timing.receive)
        self.send.connect(self.calculation.receive_info)

        self.label.setAlignment(Qt.AlignCenter)
        self.webEngineView.setAttribute(Qt.WA_TranslucentBackground);
        self.webEngineView.setStyleSheet("background:transparent");
        webEnginePage = self.webEngineView.page()
        webEnginePage.setBackgroundColor(Qt.transparent)

        self.formula_display.setAttribute(Qt.WA_TranslucentBackground);
        self.formula_display.setStyleSheet("background:transparent");
        formula_display_page = self.formula_display.page()
        formula_display_page.setBackgroundColor(Qt.transparent)

        self.instruction_btn.clicked.connect(self.display_instruction)
        self.cheater_btn.clicked.connect(self.display_cheater)
        self.game_btn.clicked.connect(self.display_game)
        self.back.clicked.connect(self.display_home)
        self.back_2.clicked.connect(self.display_home)
        self.back_3.clicked.connect(self.display_home)
        self.back_4.clicked.connect(self.display_game)
        self.back_5.clicked.connect(self.setting_up_custom)
        self.lineEdit.returnPressed.connect(self.input_list)
        self.clear_all_btn.clicked.connect(self.clear_all_fcn)
        self.submit_btn.clicked.connect(self.display_equation)

        self.novice_btn.clicked.connect(self.setting_up_novice)
        self.intermediate_btn.clicked.connect(self.setting_up_intermediate)
        self.expert_btn.clicked.connect(self.setting_up_expert)
        self.custom_btn.clicked.connect(self.setting_up_custom)
        self.start_btn.clicked.connect(self.start_game)
        self.reset_btn.clicked.connect(self.reset)
        self.undo_btn.clicked.connect(self.undo)
        self.custo_setting.clicked.connect(self.setting_display)
        self.horizontalSlider.valueChanged.connect(self.change_slider_value)
        self.card_input.returnPressed.connect(self.input_list_setting)
        self.save_change_btn.clicked.connect(self.save_change)

        self.plus.clicked.connect(self.make_move)
        self.minus.clicked.connect(self.make_move)
        self.times.clicked.connect(self.make_move)
        self.divide.clicked.connect(self.make_move)

        self.card_layout = QtWidgets.QHBoxLayout()
        self.dont_have_sol.clicked.connect(self.dont_have_an_answer)

    ## game navigation page fcn ##
    def time_run_out(self):
        if self.noanswer:
            pass
        elif self.ai_answer:
            self.bot_word.show()
            self.formula_display.setHtml(self.pageSource)
            self.formula_display.show()
        # self.start_btn.setEnabled(True)
        # self.back_4.setEnable(True)

    def start_timer(self):
        list_number = []
        for i in range(len(self.d)):
            list_number.append(self.d[i].text())

        value = self.min_time
        self.start_timing.emit(value)
        self.send.emit(self.target,list_number)
        self.calculation.start()
        self.timing.start()
        self.timing.trigger.connect(self.display)
        self.calculation.calc.connect(self.formula)

    def clear_formula(self):
        self.pageSource = """
                                     <html><head>
                                     <script type="text/javascript" 
                                     src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML">                     
                                     </script></head>
                                     <body>
                                     <p><mathjax style="font-size:2.3em">$$$$</mathjax></p>
                                     </body></html>
                                     """
        self.formula_display.setHtml(self.pageSource)
        self.formula_display.show()

    def formula(self,string):
        """setting up the latex equation block"""
        self.ai_answer = True
        self.answer = string

        self.pageSource = """
                             <html><head>
                             <script type="text/javascript" 
                             src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML">                     
                             </script></head>
                             <body>
                             <p><mathjax style="font-size:2.3em">$$%s$$</mathjax></p>
                             </body></html>
                             """ % string

        if self.time_count.text() == '0':
            self.bot_word.show()
            self.formula_display.setHtml(self.pageSource)
            self.formula_display.show()
        elif self.noanswer==True:
            if self.answer == ':(':
                self.win_message()
            else:
                self.bot_word.setText("You are wrong. Here's an example:")
                self.bot_word.show()
                self.formula_display.setHtml(self.pageSource)
                self.formula_display.show()



    def display(self, num):
        self.time_count.setText(str(num))
        if num == 0:
            self.time_run_out()

    def undo(self):
        if self.history != []:
            undoset = self.history[-1]
            for i in range(len(self.d)):
                if self.d[i].isHidden():
                    self.d[i].show()
                    break
            count = 0
            for i in range(len(self.d)):
                if not self.d[i].isHidden():
                    self.d[i].setText(undoset[count])
                    count += 1

            self.history = self.history[:-1]

    def start_game(self):
        try:
            # self.start_btn.setEnabled(False)
            # self.back_4.setEnabled(False)
            if self.timing.isRunning():
                self.timing.terminate()
                self.timing.quit()
            if self.calculation.isRunning():
                self.calculation.terminate()
                self.calculation.quit()

            self.clear_formula()
            self.bot_word.hide()
            self.ai_answer = False
            self.noanswer = False
            self.new_card_set = []
            self.answer = ''
            for i in range(len(self.d)):
                self.new_card_set.append(random.choice(self.card_choice))
                self.d[i].setText(str(self.new_card_set[i]))
                self.d[i].setChecked(False)
                if self.d[i].isHidden():
                    self.d[i].show()
            for i in range(4):
                self.button_set[i].setChecked(False)
            self.start_timer()
            self.deleted_card = []
            self.card_operation = []
            self.sign_op = []
            self.history = []

            self.time_count.setText(str(self.min_time))

        except BaseException:
            pass

    def dont_have_an_answer(self):
        if self.timing.isRunning():
            self.timing.terminate()
            self.timing.quit()

        self.noanswer = True
        if self.ai_answer == True:
            if self.answer == ':(':
                self.win_message()
            else:
                self.bot_word.setText("You are wrong. Here's an example:")
                self.pageSource = """
                                             <html><head>
                                             <script type="text/javascript" 
                                             src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML">                     
                                             </script></head>
                                             <body>
                                             <p><mathjax style="font-size:2.3em">$$%s$$</mathjax></p>
                                             </body></html>
                                             """ % self.answer
                self.bot_word.show()
                self.formula_display.setHtml(self.pageSource)
                self.formula_display.show()
        else:
            self.bot_word.setText("Wow, you are too fast, wait a sec...")
            self.bot_word.show()

    def reset(self):
        try:
            for i in range(len(self.d)):
                self.d[i].setText(str(self.new_card_set[i]))
                self.d[i].setChecked(False)
                if self.d[i].isHidden():
                    self.d[i].show()
            for i in range(4):
                self.button_set[i].setChecked(False)
            self.deleted_card = []
            self.card_operation = []
            self.sign_op = []
            self.history = []
        except BaseException:
            pass

    def make_move(self):
        sender = self.sender()
        if sender.isChecked():
            if sender in self.d:
                self.card_operation.append(sender)
            else:
                self.sign_op.append(sender)

        else:
            if sender in self.d:
                self.card_operation.remove(sender)
            else:
                self.sign_op.remove(sender)


        if len(self.card_operation) == 2 and len(self.sign_op) == 1:
            self.store_history()

            num = []
            for j in self.card_operation:
                j.setChecked(False)
                num.append(float(j.text()))
            self.sign_op[0].setChecked(False)
            num.insert(1,self.sign_op[0].text())

            result = evaluate(num)
            if result != '':
                if result == int(result):
                    result = int(result)
                self.card_operation[1].hide()
                self.deleted_card.append(self.card_operation[1])
                self.card_operation[0].setText(str(result))
                self.card_operation = []
                self.sign_op = []
            self.winning_check()

    def store_history(self):
        new_set = []
        for i in range(len(self.d)):
            if not self.d[i].isHidden():
                new_set.append(self.d[i].text())
        self.history.append(new_set)

    def winning_check(self):
        target =  float(self.target_display.text())
        count = len(self.d)
        index = 0
        for i in range(len(self.d)):
            if self.d[i].isHidden():
                count -= 1
            else:
                index = i

        if count == 1:
            final_value = float(self.d[index].text())
            if final_value==target:
                # self.start_btn.setEnabled(True)
                # self.back_4.setEnabled(True)
                if self.timing.isRunning():
                    self.timing.terminate()
                    self.timing.quit()
                if self.calculation.isRunning():
                    self.calculation.terminate()
                    self.calculation.quit()
                self.win_message()

    # have not set stylesheet for win_message yet.
    def win_message(self):
        reply = QMessageBox()
        reply.setWindowIcon(QIcon("bin/exclamation.png"))
        reply.setBaseSize(QSize(600, 120));
        reply.setText('Congrats!\nYou found a solution before the Bot did! Want another round?')
        yes = reply.addButton('Yes', QMessageBox.YesRole)
        no = reply.addButton('No', QMessageBox.NoRole)
        reply.setWindowFlags(reply.windowFlags() | Qt.FramelessWindowHint|Qt.WA_TranslucentBackground)
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        reply.setGraphicsEffect(shadow)
        reply.setStyleSheet("QMessageBox {background-color: rgb(212, 212, 212);font: 10.5pt 'Adobe Devanagari';"
                            "color:black;border:1px solid black;}"
                            "QMessageBox QLabel {background-color:rgb(212, 212, 212);padding-top:40px;"
                            "padding-bottom:40px;color: black;min-width: 700px;}")
        style = "QPushButton{padding-top:5px;" \
                "border: 2px solid black;"\
                          "border-radius: 15px;"\
                          "width: 200px;"\
                          "font: 75 10pt 'Adobe Devanagari';}"\
                          "QPushButton:hover{"\
                          "padding-top:5px;"\
                          "border: 5px solid black;"\
                          "border-radius: 15px;"\
                          "font: 75 10pt 'Adobe Devanagari';}"
        no.setStyleSheet(style)
        yes.setStyleSheet(style)
        reply.exec()
        if reply.clickedButton() == yes:
            self.setting_up_novice()
        if reply.clickedButton() == no:
            self.display_game()

    def clearLayout(self,layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def custom_card_widget(self,num):
        self.clearLayout(self.card_layout)
        self.d = []
        self.deleted_card = []
        for x in range(num):
            self.d.append(QtWidgets.QToolButton())

            # d["card{0}".format(x)]
            self.d[x].setFixedSize(100, 175)
            self.d[x].setCheckable(True)
            self.d[x].clicked.connect(self.make_move)
            self.d[x].setFont(QFont("Adobe Devanagari", 20))
            self.d[x].setStyleSheet('QToolButton{padding-top:5px;border: 2px solid black;border-radius: 15px;'
                                    'background-color: white;}'
                                    'QToolButton:hover{padding-top:5px;border: 5px solid black;border-radius: 15px;'
                                    'font: 75 20pt "Adobe Devanagari";}'
                                    'QToolButton:checked{padding-top:5px;'
                                    'border: 5px solid black;border-radius: 15px;font: 75 20pt "Adobe Devanagari";}')
            self.card_layout.addWidget(self.d[x])

        self.scrollAreaWidgetContents.setLayout(self.card_layout)

    def setting_up_novice(self):

        # self.start_btn.setEnabled(True)
        # self.back_4.setEnabled(True)
        self.card_choice=[1,2,3,4,5,6,7,8,9,10,11,12,13]
        self.custo_setting.hide()
        self.background_container.setCurrentIndex(4)
        self.difficulty_display.setText("Novice")
        self.min_time = 30
        self.time_count.setText(str(self.min_time))
        self.target = 24
        self.target_display.setText(str(self.target))
        if not self.bot_word.isHidden():
            self.bot_word.hide()
        self.card_num = 4
        self.custom_card_widget(self.card_num)
        self.clear_formula()

    def setting_up_intermediate(self):
        # self.start_btn.setEnabled(True)
        # self.back_4.setEnabled(True)
        self.card_choice = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        self.custo_setting.hide()
        self.background_container.setCurrentIndex(4)
        self.difficulty_display.setText("Intermediate")
        self.min_time = 15
        self.time_count.setText(str(self.min_time))
        self.target = 24
        self.target_display.setText(str(self.target))
        if not self.bot_word.isHidden():
            self.bot_word.hide()
        self.card_num = 4
        self.custom_card_widget(self.card_num)
        self.clear_formula()

    def setting_up_expert(self):
        # self.start_btn.setEnabled(True)
        # self.back_4.setEnabled(True)
        self.card_choice = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        self.custo_setting.hide()
        self.background_container.setCurrentIndex(4)
        self.difficulty_display.setText("Expert")
        self.min_time = 35
        self.time_count.setText(str(self.min_time))
        self.target = 24
        self.target_display.setText(str(self.target))
        if not self.bot_word.isHidden():
            self.bot_word.hide()
        self.card_num = 6
        self.custom_card_widget(self.card_num)
        self.clear_formula()
    def setting_display(self):
        u = open("last_custom.json", encoding='utf-8')
        data = json.load(u)
        self.background_container.setCurrentIndex(5)
        self.horizontalSlider.setValue(data['card_number'])
        self.card_num_set.setText(str(data['card_number']))
        self.target_input.setText(str(data['target']))
        self.time_input.setText(str(data['ai_reaction_time']))
        list_new = data['card_ranges']
        self.card_list_2.clear()
        new = []
        for i in range(len(list_new)):
            new.append(QtWidgets.QListWidgetItem(str(list_new[i])))
            self.card_list_2.addItem(new[i])
            new[i].setTextAlignment(Qt.AlignCenter)

    def change_slider_value(self):
        num = self.horizontalSlider.value()
        self.card_num_set.setText(str(num))

    def save_change(self):
        try:
            float(self.target_input.text())
            float(self.time_input.text())
            items = []
            for x in range(self.card_list_2.count() - 1):
                items.append(int(self.card_list_2.item(x).text()))
            store_dic = {}
            store_dic.update({"target":int(self.target_input.text()),
                              "ai_reaction_time": int(self.time_input.text()),
                              "card_number": self.horizontalSlider.value(),
                              "card_ranges": items})

            with open("last_custom.json", 'w',encoding='utf-8') as fw:
                json.dump(store_dic, fw)

        except ValueError:
            self.setting_display()

    def input_list_setting(self):
        """inputting into the listview"""
        new_card = self.card_input.text()
        try:
            float(new_card)
            new = QtWidgets.QListWidgetItem(str(new_card))
            self.card_input.setText("")
            self.card_list_2.addItem(new)
            list_new = self.card_list_2.findItems(new_card,Qt.MatchExactly)
            for i in range(len(list_new)):
                list_new[i].setTextAlignment(Qt.AlignCenter)
        except ValueError:
            self.card_input.setText("")

    def setting_up_custom(self):
        u = open("last_custom.json", encoding='utf-8')
        data = json.load(u)

        if self.custo_setting.isHidden():
            self.custo_setting.show()
        self.background_container.setCurrentIndex(4)
        self.difficulty_display.setText("Custom")

        self.min_time = data['ai_reaction_time']
        self.time_count.setText(str(self.min_time))
        self.target = data['target']
        self.target_display.setText(str(self.target))
        if not self.bot_word.isHidden():
            self.bot_word.hide()
        self.card_num = data['card_number']
        self.card_choice = data['card_ranges']
        self.custom_card_widget(self.card_num)

        self.clear_formula()


    ## cheater page fcn ##
    def display_equation(self):
        """retrive card composition, calculate the right equation, and display"""
        if self.target_enter.text()!='':
            try:
                items = []
                target = float(self.target_enter.text())

                for i in range(self.card_list.count()):
                    if int(self.card_list.item(i).text())==float(self.card_list.item(i).text()):
                        items.append(int(self.card_list.item(i).text()))
                    else:
                        items.append(float(self.card_list.item(i).text()))

                latex = equation_formation.translate_to_latex(items, target)
                if latex == -1:
                    self.display_latex(":(")
                else:
                    self.display_latex(latex) # division: \div; multiplication &times

            except ValueError:
                self.target_enter.setText("")
        
    def display_latex(self,string):
        """setting up the latex equation block"""
        pageSource = """
                     <html><head>
                     <script type="text/javascript" 
                     src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML">                     
                     </script></head>
                     <body>
                     <p><mathjax style="font-size:2.3em">$$%s$$</mathjax></p>
                     </body></html>
                     """%string
        self.webEngineView.setHtml(pageSource)
        self.webEngineView.show()

    def input_list(self):
        """inputting into the listview"""
        new_card = self.lineEdit.text()
        try:
            float(new_card)
            new = QtWidgets.QListWidgetItem(str(new_card))
            self.lineEdit.setText("")
            self.card_list.addItem(new)
            list_new = self.card_list.findItems(new_card,Qt.MatchExactly)
            for i in range(len(list_new)):
                list_new[i].setTextAlignment(Qt.AlignCenter)
        except ValueError:
            self.lineEdit.setText("")

    def keyPressEvent(self, event):
        """keyboard event function"""
        if event.key() == Qt.Key_Escape:
            self.close()
        if event.key() in [Qt.Key_Delete, Qt.Key_Backspace]:
            if self.background_container.currentIndex()==2 and len(self.card_list.selectedIndexes())!=0:
                self.card_list.takeItem(self.card_list.currentRow())
            if self.background_container.currentIndex()==5 and len(self.card_list_2.selectedIndexes())!=0:
                self.card_list_2.takeItem(self.card_list_2.currentRow())
        if event.key() == Qt.Key_Enter:
            if self.background_container.currentIndex()==2 and self.lineEdit.getText()=='':
                self.display_equation()
        if event.key() is Qt.Key_Left:
            if self.background_container.currentIndex()==4:
                self.undo_cards()

    def clear_all_fcn(self):
        """clear widget"""
        self.card_list.clear()
        self.display_latex('')
        self.lineEdit.setText('')
        self.target_enter.setText('')

    ## home page fcn##
    def display_home(self):
        """display home page"""
        self.background_container.setCurrentIndex(0)

    def display_instruction(self):
        """display instruction page"""
        self.background_container.setCurrentIndex(1)

    def display_cheater(self):
        """display correct page"""
        self.background_container.setCurrentIndex(2)

    def display_game(self):
        """display correct page"""
        self.background_container.setCurrentIndex(3)
        if self.timing.isRunning():
            self.timing.terminate()
        if self.calculation.isRunning():
            self.calculation.terminate()

    ## window configureation ##
    def closeEvent(self,event):
        """close event of mainwindow"""
        event.accept()

    def minimizeclick(self):
        """minimize event of mainwindow"""
        self.showMinimized()

    def mousePressEvent(self, event):
        """Part 1 of flexible mainwindow movement: press mouse action"""
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, QMouseEvent):
        """Part 2 of flexible mainwindow movement: move mouse action"""
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        """Part 3 of flexible mainwindow movement: release mouse action"""
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = maininterface()
    ui.show()
    sys.exit(app.exec_())