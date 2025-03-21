import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QTimeEdit, QMessageBox
)
from PyQt5.QtCore import QTimer, QTime, Qt  # 添加 Qt 模块
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta


class WorkTimeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("工作助手")
        self.setGeometry(100, 100, 500, 450)  # 增大界面大小

        # 初始化变量
        self.work_start = None
        self.work_end = None
        self.next_drink = None
        self.next_activity = None
        self.overtime_start = None  # 加班开始时间
        self.overtime_hours = 0.0  # 加班小时数
        self.is_weekend = False  # 是否为周末

        # 创建界面
        self.init_ui()

        # 启动定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)  # 每秒更新一次

    def init_ui(self):
        # 设置全局字体和样式
        self.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #333;
            }
            QPushButton {
                font-size: 16px;
                padding: 10px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTimeEdit {
                font-size: 16px;
                padding: 8px;
            }
        """)

        # 布局
        layout = QVBoxLayout()

        # 年月日显示在最上方
        self.date_label = QLabel()
        self.date_label.setFont(QFont("Arial", 20, QFont.Bold))  # 增大字体
        self.date_label.setStyleSheet("color: #2c3e50;")  # 深蓝色
        self.date_label.setAlignment(Qt.AlignCenter)  # 居中显示
        layout.addWidget(self.date_label)

        # 上班时间选择部分
        self.time_label = QLabel("选择上班时间:")
        layout.addWidget(self.time_label)

        # 使用 QTimeEdit 选择时间
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")  # 设置时间格式
        self.time_edit.setTime(QTime.currentTime())  # 默认当前时间
        self.time_edit.setWrapping(True)  # 允许时间循环滚动
        layout.addWidget(self.time_edit)

        # 设置上班时间按钮
        self.btn_set_time = QPushButton("设置上班时间")
        self.btn_set_time.clicked.connect(self.set_work_time)
        layout.addWidget(self.btn_set_time)

        # 下班时间显示
        self.info_label = QLabel("下班时间：未设置")
        self.info_label.setStyleSheet("font-size: 18px; color: #e74c3c;")  # 红色
        layout.addWidget(self.info_label)

        # 已工作时间显示
        self.elapsed_label = QLabel("已工作时间：0小时0分钟")
        layout.addWidget(self.elapsed_label)

        # 剩余时间显示
        self.remaining_label = QLabel("剩余时间：0小时0分钟")
        layout.addWidget(self.remaining_label)

        # 加班时间显示
        self.overtime_label = QLabel("加班时间：0.00小时")
        self.overtime_label.setStyleSheet("font-size: 18px; color: #8e44ad;")  # 紫色
        layout.addWidget(self.overtime_label)

        # 提醒显示
        self.reminder_label = QLabel("提醒：无")
        self.reminder_label.setStyleSheet("font-size: 18px; color: #3498db;")  # 蓝色
        layout.addWidget(self.reminder_label)

        # 打卡下班按钮
        self.btn_clock_out = QPushButton("打卡下班")
        self.btn_clock_out.clicked.connect(self.clock_out)
        layout.addWidget(self.btn_clock_out)

        # 设置布局
        self.setLayout(layout)

    def set_work_time(self):
        # 获取用户选择的时间
        selected_time = self.time_edit.time()
        now = datetime.now()

        # 设置上班时间
        work_start = now.replace(
            hour=selected_time.hour(),
            minute=selected_time.minute(),
            second=0, microsecond=0
        )

        if work_start > now:
            QMessageBox.warning(self, "错误", "选择的上班时间不能晚于当前时间！")
            return

        self.work_start = work_start

        # 判断是否为周末
        self.is_weekend = now.weekday() >= 5  # 5=星期六, 6=星期日

        if not self.is_weekend:
            # 计算下班时间（上班时间 + 8小时45分钟）
            self.work_end = self.work_start + timedelta(hours=8, minutes=45)
            self.info_label.setText(f"下班时间：{self.work_end.strftime('%H:%M')}")
        else:
            # 周末不计算下班时间
            self.work_end = None
            self.info_label.setText("下班时间：周末自由上下班")

        # 初始化提醒时间
        self.next_drink = self.work_start + timedelta(minutes=45)
        self.next_activity = self.work_start + timedelta(hours=2)

    def update_clock(self):
        now = datetime.now()

        # 更新日期信息
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        weekday = weekdays[now.weekday()]
        week_number = now.isocalendar()[1]  # 获取当前是第几周
        self.date_label.setText(
            f"{now.strftime('%Y年-%m月-%d日')}（{weekday}） 第{week_number}周"
        )

        if self.work_start:
            # 计算工作时间，减去45分钟
            worked = now - self.work_start - timedelta(minutes=45)
            if worked.total_seconds() < 0:
                worked = timedelta(0)
            worked_h = worked.seconds // 3600
            worked_m = (worked.seconds % 3600) // 60
            self.elapsed_label.setText(f"已工作时间：{worked_h}小时{worked_m}分钟")

            if not self.is_weekend and self.work_end:
                # 工作日计算剩余时间和加班时间
                remaining = self.work_end - now

                if remaining.total_seconds() > 0:
                    # 剩余时间
                    remain_h = remaining.seconds // 3600
                    remain_m = (remaining.seconds % 3600) // 60
                    self.remaining_label.setText(f"剩余时间：{remain_h}小时{remain_m}分钟")

                    # 精确剩余时间
                    remain_decimal = remaining.seconds / 3600
                    self.decimal_label.setText(f"精确剩余：{remain_decimal:.2f}小时")
                else:
                    self.remaining_label.setText("下班时间已到！")
                    self.decimal_label.setText("精确剩余：0.00小时")

                    # 计算加班时间（下班时间延后30分钟开始计算）
                    self.overtime_start = self.work_end + timedelta(minutes=30)
                    if now > self.overtime_start:
                        overtime = now - self.overtime_start
                        self.overtime_hours = overtime.total_seconds() / 3600
                        self.overtime_label.setText(f"加班时间：{self.overtime_hours:.2f}小时")
            else:
                # 周末不计算剩余时间
                self.remaining_label.setText("剩余时间：周末自由上下班")
                self.decimal_label.setText("精确剩余：无")

            # 检查提醒
            self.check_reminders(now)

    def check_reminders(self, now):
        # 初始化提醒内容
        reminder_text = "提醒：无"

        # 喝水提醒
        if now > self.next_drink:
            reminder_text = "🕒 工作45分钟了，该喝水休息一下啦！"
            self.next_drink += timedelta(minutes=45)

        # 活动提醒
        if now > self.next_activity:
            reminder_text = "🕒 连续工作2小时了，起来活动活动吧！"
            self.next_activity += timedelta(hours=2)

        # 更新提醒显示
        self.reminder_label.setText(reminder_text)

    def clock_out(self):
        if self.work_start:
            now = datetime.now()
            if self.is_weekend:
                # 周末直接显示已工作时间
                worked = now - self.work_start
                worked_hours = worked.total_seconds() / 3600
                QMessageBox.information(
                    self,
                    "打卡下班",
                    f"您已打卡下班！\n工作时间：{worked_hours:.2f}小时"
                )
            else:
                if now > self.work_end + timedelta(minutes=30):
                    overtime = now - (self.work_end + timedelta(minutes=30))
                    overtime_hours = overtime.total_seconds() / 3600
                    QMessageBox.information(
                        self,
                        "打卡下班",
                        f"您已打卡下班！\n加班时间：{overtime_hours:.2f}小时"
                    )
                else:
                    QMessageBox.information(
                        self,
                        "打卡下班",
                        "您已打卡下班！\n加班时间：0.00小时"
                    )
        else:
            QMessageBox.warning(self, "错误", "请先设置上班时间！")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WorkTimeApp()
    window.show()
    sys.exit(app.exec_())