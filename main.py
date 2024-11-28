import datetime
import sqlite3
import sys

from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem

from Window import Ui_MainWindow


class Wallet(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.values = {"₽": 1, "$": 100, "€": 106, "¥": 14}
        self.operation = None
        self.key_is = False
        self.con = sqlite3.connect("transactions.sqlite")
        self.cur = self.con.cursor()
        self.setupUi(self)
        self.id = False
        # Добавляем кнопки
        self.save_replenishment.clicked.connect(self.do_save_replenishment)
        self.save_purchase.clicked.connect(self.do_save_purchase)
        self.add_purchase.clicked.connect(self.do_new_purchase)
        self.cancel.clicked.connect(self.do_cancel)
        self.goal.textChanged.connect(self.do_count_percent)
        self.radio_auto.clicked.connect(self.auto_time)
        self.error_about.clicked.connect(self.do_about_sum_error)
        self.add_replenishment.clicked.connect(self.do_new_replenishment)
        self.search_line.textChanged.connect(self.do_search)
        self.search_filter.activated.connect(self.do_search)
        self.clear_search.clicked.connect(self.do_clear_search)
        self.id_button.clicked.connect(self.do_id)
        self.take.clicked.connect(self.do_take)
        self.put.clicked.connect(self.do_put)
        self.accept_bank.clicked.connect(self.do_accept_bk)
        self.cancel_bank.clicked.connect(self.do_cancel_bk)
        self.about_3 = True
        self.error_label_2.setHidden(True)
        self.error_label_4.setHidden(True)
        self.do_cancel_bk()
        self.refresh_bank()

        # Скрываем не нужное
        self.do_cancel()
        self.date.setDateTime(datetime.datetime.today())
        self.do_refresh()

    def do_put(self):
        self.banksum_line.setHidden(False)
        self.accept_bank.setHidden(False)
        self.cancel_bank.setHidden(False)
        self.currency_tobank.setHidden(False)
        self.operation = 1

    def do_take(self):
        self.banksum_line.setHidden(False)
        self.accept_bank.setHidden(False)
        self.cancel_bank.setHidden(False)
        self.currency_tobank.setHidden(False)
        self.operation = 0

    def do_accept_bk(self):
        if self.operation == 1:
            with open("bank.txt", "r") as w:
                w = w.readline()
            try:
                line = int(self.banksum_line.text()) * self.values[self.currency_tobank.currentText()]
                if line <= int(self.money.text()[:-1]):
                    self.money.setText(str(int(self.money.text()[:-1]) - line))
                    with open("bank.txt", "w") as f:
                        print(str(int(w) + line), file=f)
                        self.error_label_5.setHidden(True)
                        date_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
                        sql = """INSERT INTO spendings
                        (names, summs, time, currency, status)
                        VALUES ("Вклад в копилку", ?, ?, ?, '-');"""
                        values = (int(self.banksum_line.text()), date_time, self.currency_tobank.currentText())
                        self.cur.execute(sql, values)
                        self.con.commit()
                        self.do_refresh()
                        self.do_cancel_bk()
                        self.banksum_line.setText("")
                        self.do_cancel_bk()
                else:
                    self.error_label_5.setText("Недостаточно средств")
                    self.error_label_5.setHidden(False)
            except ValueError:
                self.error_label_5.setText("Неверный ввод")
                self.error_label_5.setHidden(False)
        elif self.operation == 0:
            with open("bank.txt", "r") as w:
                w = w.readline()
            try:
                line = int(self.banksum_line.text()) * self.values[self.currency_tobank.currentText()]
                if line <= int(self.available.text()):
                    self.money.setText(str(int(self.money.text()[:-1]) + line))
                    with open("bank.txt", "w") as f:
                        print(str(int(w) - line), file=f)
                        self.error_label_5.setHidden(True)
                        date_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
                        if date_time[11] == "0":
                            date_time = date_time[:11] + date_time[12:]
                        sql = """INSERT INTO spendings
                        (names, summs, time, currency, status)
                        VALUES ("Вывод с копилки", ?, ?, ?, '+');"""
                        values = (int(self.banksum_line.text()), date_time, self.currency_tobank.currentText())
                        self.cur.execute(sql, values)
                        self.banksum_line.setText("")
                        self.con.commit()
                        self.do_refresh()
                        self.do_cancel_bk()

                else:
                    self.error_label_5.setText("Недостаточно средств")
                    self.error_label_5.setHidden(False)
            except ValueError:
                self.error_label_5.setText("Неверный ввод")
                self.error_label_5.setHidden(False)
        self.refresh_bank()
        self.do_count_percent()

    def refresh_bank(self):
        with open("bank.txt") as f:
            f = f.readline()
            self.available.setText(f)

    def do_cancel_bk(self):
        self.error_label_5.setHidden(True)
        self.banksum_line.setHidden(True)
        self.banksum_line.setText("")
        self.accept_bank.setHidden(True)
        self.cancel_bank.setHidden(True)
        self.currency_tobank.setHidden(True)

    def do_count_percent(self):
        try:
            goal = self.goal.text()
            percent = int(self.available.text()) / int(goal)
            self.procents.setRange(0, 100)
            if percent < 1:
                self.procents.setValue(int(round(percent * 100)))
                self.error_label_4.setHidden(True)
                self.error_label_2.setHidden(True)
            else:
                self.error_label_4.setHidden(False)
                self.procents.setValue(100)
                self.error_label_2.setHidden(True)
        except ValueError:
            self.error_label_2.setHidden(False)
            self.error_label_4.setHidden(True)

    def do_clear_search(self):
        self.search_line.setText("")
        self.do_refresh()

    def do_search(self):
        self.key_is = True
        self.key = self.search_line.text()
        self.do_refresh()

    def do_about_sum_error(self):
        if self.about_3:
            self.about_3 = False
            self.error_label_3.setText("Числа отсутствуют")
        else:
            self.about_3 = True
            self.error_label_3.setText("Неверный ввод:")

    def do_id(self):
        if self.id:
            icon = QIcon()
            icon.addPixmap(QPixmap("фото/cross.png"), QIcon.Mode.Normal, QIcon.State.Off)
            self.id_status.setIcon(icon)
            self.id = False
        else:
            icon = QIcon()
            icon.addPixmap(QPixmap("фото/True.png"), QIcon.Mode.Normal, QIcon.State.Off)
            self.id_status.setIcon(icon)
            self.id = True
        self.do_refresh()

    def do_new_replenishment(self):
        self.do_cancel()
        self.purchase.setHidden(False)
        self.label_name.setText("Описание пополнения")
        self.sum.setHidden(False)
        self.date.setHidden(False)
        self.radio_auto.setHidden(False)
        self.save_replenishment.setHidden(False)
        self.cancel.setHidden(False)
        self.currency.setHidden(False)
        self.label_name.setHidden(False)
        self.label_sum.setHidden(False)
        self.label_date.setHidden(False)

    def do_new_purchase(self):
        self.do_cancel()
        self.label_name.setText("Описание покупки")
        self.purchase.setHidden(False)
        self.sum.setHidden(False)
        self.date.setHidden(False)
        self.radio_auto.setHidden(False)
        self.save_purchase.setHidden(False)
        self.cancel.setHidden(False)
        self.currency.setHidden(False)
        self.label_name.setHidden(False)
        self.label_sum.setHidden(False)
        self.label_date.setHidden(False)

    def do_save_replenishment(self):
        purchase = self.purchase.text()
        summ = self.sum.text()
        date_time = self.date.dateTime()
        date_time = str(date_time.toString(self.date.displayFormat()))
        summ = "".join(c for c in summ if c.isdecimal())
        if summ:
            self.error_label_3.setHidden(True)
            self.error_about.setHidden(True)
            sql = """INSERT INTO spendings
            (names, summs, time, currency, status)
            VALUES (?, ?, ?, ?, '+');"""
            values = (purchase, summ, date_time, self.currency.currentText())
            self.cur.execute(sql, values)
            self.con.commit()
            self.do_cancel()
            self.do_refresh()
        else:
            self.error_label_3.setHidden(False)
            self.error_about.setHidden(False)

    def do_save_purchase(self):
        purchase = self.purchase.text()
        summ = self.sum.text()
        date_time = self.date.dateTime()
        date_time = str(date_time.toString(self.date.displayFormat()))
        summ = "".join(c for c in summ if c.isdecimal())
        if summ:
            self.error_label_3.setHidden(True)
            self.error_about.setHidden(True)
            sql = """INSERT INTO spendings
            (names, summs, time, currency, status)
            VALUES (?, ?, ?, ?, '-');"""
            values = (purchase, summ, date_time, self.currency.currentText())
            self.cur.execute(sql, values)
            self.con.commit()
            self.do_cancel()
            self.do_refresh()
        else:
            self.error_label_3.setHidden(False)
            self.error_about.setHidden(False)

    def auto_time(self):
        signal = not (self.radio_auto.isChecked())
        self.date.setEnabled(signal)
        if not signal:
            self.date.setDateTime(datetime.datetime.today())

    def do_cancel(self):
        self.purchase.setHidden(True)
        self.sum.setHidden(True)
        self.date.setHidden(True)
        self.sum.setText("")
        self.purchase.setText("")
        self.radio_auto.setHidden(True)
        self.save_purchase.setHidden(True)
        self.cancel.setHidden(True)
        self.error_label_3.setHidden(True)
        self.error_about.setHidden(True)
        self.currency.setHidden(True)
        self.save_replenishment.setHidden(True)
        self.label_name.setHidden(True)
        self.label_sum.setHidden(True)
        self.label_date.setHidden(True)

    def do_refresh(self):
        if self.key_is:
            if self.search_filter.currentText() == "По имени":
                self.sql = """
                    SELECT * FROM spendings
                    WHERE names LIKE ? or names LIKE ?;
                    """
                self.cur.execute(self.sql, [f'%{self.key.lower()}%', f'%{self.key.upper()}%'])
            elif self.search_filter.currentText() == "По сумме":
                self.sql = """
                    SELECT * FROM spendings
                    WHERE summs LIKE ? or summs LIKE ?;
                    """
                self.cur.execute(self.sql, [f'%{self.key.lower()}%', f'%{self.key.upper()}%'])
            elif self.search_filter.currentText() == "По времени":
                self.sql = """
                    SELECT * FROM spendings
                    WHERE time LIKE ? or names LIKE ?;
                    """
                self.cur.execute(self.sql, [f'%{self.key.lower()}%', f'%{self.key.upper()}%'])
            else:
                self.sql = """
                    SELECT * FROM spendings
                    WHERE names LIKE ? OR 
                    summs LIKE ? OR
                    time LIKE ? OR
                    names LIKE ? OR 
                    summs LIKE ? OR
                    time LIKE ?;
                    """
                keys = (
                    f"%{self.key.lower()}%", f"%{self.key.upper()}%",
                    f"%{self.key.lower()}%", f"%{self.key.upper()}%",
                    f"%{self.key.lower()}%", f"%{self.key.upper()}%")
                self.cur.execute(self.sql, keys)

        else:
            self.cur.execute("SELECT * FROM spendings")
        spends = self.cur.fetchall()
        self.purchase_table.setRowCount(len(spends))

        if self.id:
            self.purchase_table.setColumnCount(4)
            self.purchase_table.setHorizontalHeaderLabels(("id", "names", "sums", "time"))
            if len(spends) > 2:
                self.purchase_table.setColumnWidth(0, 40)
                self.purchase_table.setColumnWidth(1, 100)
                self.purchase_table.setColumnWidth(2, 100)
                self.purchase_table.setColumnWidth(3, 98)
            else:
                self.purchase_table.setColumnWidth(0, 50)
                self.purchase_table.setColumnWidth(1, 110)
                self.purchase_table.setColumnWidth(2, 112)
                self.purchase_table.setColumnWidth(3, 90)
            i = len(spends) - 1
            for line in spends:
                self.purchase_table.setItem(i, 0, QTableWidgetItem(str(line[0])))
                self.purchase_table.setItem(i, 1, QTableWidgetItem(str(line[1])))
                self.purchase_table.setItem(i, 2, QTableWidgetItem(str(f"{line[4]}{line[2]}{line[5]}")))
                self.purchase_table.setItem(i, 3, QTableWidgetItem(str(line[3])))
                i -= 1
        else:
            self.purchase_table.setColumnCount(3)
            self.purchase_table.setHorizontalHeaderLabels(("names", "sums", "time"))
            if len(spends) > 3:
                self.purchase_table.setColumnWidth(0, 120)
                self.purchase_table.setColumnWidth(1, 115)
                self.purchase_table.setColumnWidth(2, 104)
            elif len(spends) == 3:
                self.purchase_table.setColumnWidth(0, 120)
                self.purchase_table.setColumnWidth(1, 116)
                self.purchase_table.setColumnWidth(2, 110)
            else:
                self.purchase_table.setColumnWidth(0, 123)
                self.purchase_table.setColumnWidth(1, 120)
                self.purchase_table.setColumnWidth(2, 120)

            i = len(spends) - 1
            for line in spends:
                self.purchase_table.setItem(i, 0, QTableWidgetItem(str(line[1])))
                self.purchase_table.setItem(i, 1, QTableWidgetItem(str(f"{line[4]}{line[2]}{line[5]}")))
                self.purchase_table.setItem(i, 2, QTableWidgetItem(str(line[3])))
                i -= 1
        self.key_is = False
        sql = """
        SELECT summs, currency FROM spendings
        WHERE status LIKE "+";
        """
        self.cur.execute(sql)
        plus = self.cur.fetchall()
        sql = """
        SELECT summs, currency FROM spendings
        WHERE status LIKE "-";
        """
        self.cur.execute(sql)
        minus = self.cur.fetchall()
        list_min = []
        list_pls = []
        for spends in minus:
            list_min.append(spends)
        for replen in plus:
            list_pls.append(replen)
        list_minuses = []
        list_pluses = []
        for amounts in list_min:
            list_minuses.append(amounts[0] * self.values[amounts[1]])
        for amounts in list_pls:
            list_pluses.append(amounts[0] * self.values[amounts[1]])
        self.money.setText(str(0 - sum(list_minuses) + sum(list_pluses)) + "₽")
        self.do_count_percent()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Wallet()
    ex.show()
    sys.exit(app.exec())
