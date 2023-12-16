import os
import psycopg2
import dearpygui.dearpygui as dpg

from dotenv import load_dotenv
from datetime import datetime
from base import client, contains, project, tag, task, team, wastes, worker, working_rate, worktime


load_dotenv()
conn = psycopg2.connect(
    dbname=os.getenv('DBNAME'), user=os.getenv('USER'),
    password=os.getenv('PASSWORD'), host=os.getenv('HOST'), port=os.getenv('PORT')
)
cursor = conn.cursor()

def close_base():
    global conn, cursor
    cursor.close()
    conn.close()


dpg.create_context()
with dpg.font_registry():
    with dpg.font(
        "/usr/share/fonts/FiraCode/Fira Code Retina Nerd Font Complete.otf",
        18, default_font=True, tag="Default font"
    ) as f:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
dpg.bind_font("Default font")


def update_value(sender, value, user_data):
    table_name, column, last_value = user_data['table_name'], user_data['column'], user_data['value']
    value = user_data['handler'](value)
    last_value = user_data['handler'](last_value)
    cursor.execute(
        f"UPDATE {table_name} SET {column}={value} WHERE {column}={last_value};"
    )
    conn.commit()
    user_data['value'] = value
    dpg.set_item_user_data(sender, user_data)


def add_table(table_name, labels, table_labels, datas):
    with dpg.table(header_row=True):
        for label in labels:
            dpg.add_table_column(label=label)
        for data in datas:
            with dpg.table_row():
                for value, label in zip(data, table_labels):
                    value = '' if value is None else value
                    user_data = {
                        "table_name": table_name,
                        "value": value,
                        "column": label,
                        "handler": lambda x: x,
                    }
                    if isinstance(value, int):
                        dpg.add_input_int(
                            default_value=value, callback=update_value,
                            user_data=user_data, width=-1
                        )
                    elif isinstance(value, float):
                        dpg.add_input_float(
                            default_value=value, callback=update_value,
                            user_data=user_data, width=-1
                        )
                    else:
                        user_data['handler'] = lambda x: f"'{x}'"
                        dpg.add_input_text(
                            default_value=value, callback=update_value,
                            user_data=user_data, on_enter=True, width=-1,
                        )


def add_report_table(labels, datas, parent, tag):
    with dpg.table(header_row=True, parent=parent, tag=tag,
                   borders_innerH=True, borders_innerV=True):
        for label in labels:
            dpg.add_table_column(label=label)
        for data in datas:
            with dpg.table_row():
                for value in data:
                    value = '' if value is None else str(value)
                    dpg.add_text(value, wrap=0)


def exec_procedure():
    d = dpg.get_item_user_data('procedure-task')
    assert d is not None
    task_id = d[dpg.get_value('procedure-task')]
    d = dpg.get_item_user_data('procedure-worker')
    assert d is not None
    worker_id = d[dpg.get_value('procedure-worker')]
    text = dpg.get_value('procedure-text')
    start = dpg.get_value('procedure-start')
    finish = dpg.get_value('procedure-finish')
    cursor.execute(
        f"call public.create_worktime({worker_id}, {task_id}, '{start}', '{finish}', '{text}')"
    )
    conn.commit()


with dpg.window(label="Процедура", modal=True, show=False, tag="procedure", width=1000, height=900):
    cursor.execute(f"SELECT tsk_id, tsk_name FROM task;")
    task_ = cursor.fetchall()
    cursor.execute(
        f"SELECT wrkr_id, wrkr_surname, wrkr_name, wrkr_middlename, tem_name, wrkr_post FROM worker;"
    )
    worker_ = cursor.fetchall()

    dpg.add_text('Начало (DateTime)')
    date = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    dpg.add_input_text(default_value=date, width=-1, tag='procedure-start')
    dpg.add_text('Конец (DateTime)')
    dpg.add_input_text(default_value=date, width=-1, tag='procedure-finish')
    ##################################################################################################
    dpg.add_text('Задача')
    dpg.add_listbox(
        items=[line[1] for line in task_], width=-1, num_items=10,
        user_data={line[1]: line[0] for line in task_},
        tag='procedure-task'
    )
    dpg.add_separator()
    ##################################################################################################
    dpg.add_text('Работник')
    dpg.add_listbox(
        items=[f"{i[4]} {i[5]} | {i[1]} {i[2]} {i[3]}" for i in worker_], width=-1, num_items=10,
        user_data={f"{i[4]} {i[5]} | {i[1]} {i[2]} {i[3]}": i[0] for i in worker_},
        tag='procedure-worker'
    )
    ##################################################################################################
    dpg.add_text('Текст')
    dpg.add_input_text(width=-1, multiline=True, tab_input=True, tag='procedure-text')
    dpg.add_button(label='Добавить', width=-1, callback=exec_procedure)


def draw_time_on_project():
    start = dpg.get_value('time_on_project-start')
    finish = dpg.get_value('time_on_project-finish')
    cursor.execute(
        f"""
        select worker.wrkr_id, worker.wrkr_surname, worker.wrkr_name, worker.wrkr_middlename,
               project.pjt_name, sum(wtm_finish-wtm_start)
        from worktime
        join worker on worker.wrkr_id=worktime.wrkr_id
        join task on task.tsk_id=worktime.tsk_id
        join project on project.pjt_id=task.pjt_id
        where wtm_start >= '{start}' and wtm_finish <= '{finish}'
        group by worker.wrkr_id, worker.wrkr_surname, worker.wrkr_name, worker.wrkr_middlename, task.pjt_id, project.pjt_name
        order by worker.wrkr_id;
        """
    )
    result = cursor.fetchall()
    add_report_table(
        ("Номер", "Фамилия", "Имя", "Отчество", "Название", "Время"),
        result if result is not None else [],
        parent=dpg.get_item_parent("time_on_project-button"),
        tag="time_on_project-table"
    )


with dpg.window(label="Время на проект", modal=True, show=False, tag="time_on_project", width=1000, height=900):
    dpg.add_text('Начало (DateTime)')
    date = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    dpg.add_input_text(default_value=date, width=-1, tag='time_on_project-start')
    dpg.add_text('Конец (DateTime)')
    dpg.add_input_text(default_value=date, width=-1, tag='time_on_project-finish')
    dpg.add_button(label="Сгенерировать", tag='time_on_project-button', callback=draw_time_on_project, width=-1)


def draw_time_on_task():
    start = dpg.get_value('time_on_task-start')
    finish = dpg.get_value('time_on_task-finish')
    cursor.execute(
        f"""
        select worker.wrkr_id, worker.wrkr_surname, worker.wrkr_name, worker.wrkr_middlename,
               task.tsk_name, sum(wtm_finish-wtm_start)
        from worktime
        join worker on worker.wrkr_id=worktime.wrkr_id
        join task on task.tsk_id=worktime.tsk_id
        where wtm_start >= '{start}' and wtm_finish <= '{finish}'
        group by worker.wrkr_id, worker.wrkr_surname, worker.wrkr_name, worker.wrkr_middlename, task.tsk_name
        order by worker.wrkr_id;
        """
    )
    result = cursor.fetchall()
    add_report_table(
        ("Номер", "Фамилия", "Имя", "Отчество", "Название", "Время"),
        result if result is not None else [],
        parent=dpg.get_item_parent("time_on_task-button"),
        tag="time_on_task-table"
    )


with dpg.window(label="Время на задачи", modal=True, show=False, tag="time_on_task", width=1000, height=900):
    dpg.add_text('Начало (DateTime)')
    date = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    dpg.add_input_text(default_value=date, width=-1, tag='time_on_task-start')
    dpg.add_text('Конец (DateTime)')
    dpg.add_input_text(default_value=date, width=-1, tag='time_on_task-finish')
    dpg.add_button(label="Сгенерировать", tag='time_on_task-button', callback=draw_time_on_task, width=-1)


def draw_bush():
    start = dpg.get_value('bush-start')
    finish = dpg.get_value('bush-finish')
    cursor.execute(
        f"""
        select worker.wrkr_id, worker.wrkr_surname, worker.wrkr_name, worker.wrkr_middlename,
               extract(epoch from sum(wtm_finish-wtm_start)) / 3600 * rte_main as itog
        from worktime
        join worker on worker.wrkr_id=worktime.wrkr_id
        join working_rate on working_rate.rte_id=worker.rte_id
        where wtm_start >= '{start}' and wtm_finish <= '{finish}'
        group by worker.wrkr_id, worker.wrkr_surname, worker.wrkr_name, worker.wrkr_middlename, rte_main
        order by worker.wrkr_id;
        """
    )
    result = cursor.fetchall()
    add_report_table(
        ("Номер", "Фамилия", "Имя", "Отчество", "Сумма"),
        result if result is not None else [],
        parent=dpg.get_item_parent("bush-button"),
        tag="bush-table"
    )


with dpg.window(label="Бухгалтерский отчёт", modal=True, show=False, tag="bush", width=1000, height=900):
    dpg.add_text('Начало (DateTime)')
    date = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    dpg.add_input_text(default_value=date, width=-1, tag='bush-start')
    dpg.add_text('Конец (DateTime)')
    dpg.add_input_text(default_value=date, width=-1, tag='bush-finish')
    dpg.add_button(label="Сгенерировать", tag='bush-button', callback=draw_bush, width=-1)


with dpg.window(label="Window", tag="window"):
    with dpg.menu_bar(tag='bar'):
        with dpg.menu(label="Процедуры"):
            dpg.add_menu_item(label="Отслеживание времени", callback=lambda: dpg.configure_item("procedure", show=True))
        with dpg.menu(label="Отчёты"):
            dpg.add_menu_item(
                label="Время на проект",
                callback=lambda: dpg.configure_item("time_on_project", show=True)
            )
            dpg.add_menu_item(
                label="Время на задачи",
                callback=lambda: dpg.configure_item("time_on_task", show=True)
            )
            dpg.add_menu_item(
                label="Бухалтерский отчёт",
                callback=lambda: dpg.configure_item("bush", show=True)
            )
    with dpg.tab_bar(tag="tables") as tb:
        with dpg.tab(label="WorkTime", tag="worktime"):
            add_table("worktime", *worktime(cursor))
        with dpg.tab(label="WorkingRate", tag="working_rate"):
            add_table("working_rate", *working_rate(cursor))
        with dpg.tab(label="Worker", tag="worker"):
            add_table("worker", *worker(cursor))
        with dpg.tab(label="Wastes", tag="wastes"):
            add_table("wastes", *wastes(cursor))
        with dpg.tab(label="Team", tag="team"):
            add_table("team", *team(cursor))
        with dpg.tab(label="Task", tag="task"):
            add_table("task", *task(cursor))
        with dpg.tab(label="Tag", tag="tag"):
            add_table("tag", *tag(cursor))
        with dpg.tab(label="Contains", tag="contains"):
            add_table("contains", *contains(cursor))
        with dpg.tab(label="project", tag="project"):
            add_table("project", *project(cursor))
        with dpg.tab(label="client", tag="client"):
            add_table("client", *client(cursor))


dpg.create_viewport(title="СУПчик")
dpg.set_primary_window("window", True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_exit_callback(close_base)
dpg.start_dearpygui()
dpg.destroy_context()

